from __future__ import annotations

import asyncio
import hashlib
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Callable

from advance_system.domain.instruments import InstrumentMasterSnapshot
from advance_system.services.instruments.master import UpstoxInstrumentMaster


@dataclass(frozen=True)
class InstrumentMasterManifest:
    """Immutable metadata describing the accepted source payload."""

    source_url: str
    fetched_at: datetime
    payload_sha256: str
    instrument_count: int
    rejected_records: int
    duplicate_count: int


class InstrumentMasterRefreshError(RuntimeError):
    """Raised when a candidate instrument snapshot fails safety validation."""


class InstrumentMasterRefresher:
    """Refresh and atomically publish validated instrument-master snapshots.

    The refresher deliberately keeps persistence out of the service. A caller can
    persist the accepted snapshot through an existing repository/object-store
    adapter without coupling ingestion to a particular database.
    """

    def __init__(
        self,
        loader: UpstoxInstrumentMaster,
        *,
        max_age: timedelta = timedelta(hours=24),
        min_instruments: int = 1,
        max_rejected_ratio: float = 0.05,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        if max_age <= timedelta(0):
            raise ValueError("max_age must be positive")
        if min_instruments < 1:
            raise ValueError("min_instruments must be positive")
        if not 0 <= max_rejected_ratio < 1:
            raise ValueError("max_rejected_ratio must be in [0, 1)")
        self.loader = loader
        self.max_age = max_age
        self.min_instruments = min_instruments
        self.max_rejected_ratio = max_rejected_ratio
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self._snapshot: InstrumentMasterSnapshot | None = None
        self._manifest: InstrumentMasterManifest | None = None
        self._refresh_lock = asyncio.Lock()

    @property
    def snapshot(self) -> InstrumentMasterSnapshot | None:
        return self._snapshot

    @property
    def manifest(self) -> InstrumentMasterManifest | None:
        return self._manifest

    def is_fresh(self, now: datetime | None = None) -> bool:
        if self._snapshot is None or self._manifest is None:
            return False
        current = now or self.clock()
        return current - self._manifest.fetched_at <= self.max_age

    def _validate_candidate(
        self,
        snapshot: InstrumentMasterSnapshot,
        payload: bytes,
        fetched_at: datetime,
    ) -> InstrumentMasterManifest:
        if snapshot.count < self.min_instruments:
            raise InstrumentMasterRefreshError(
                f"instrument master contains {snapshot.count} instruments; "
                f"minimum is {self.min_instruments}"
            )

        total_records = snapshot.count + snapshot.rejected_records + len(snapshot.duplicate_keys)
        rejected_ratio = (
            snapshot.rejected_records / total_records if total_records else 1.0
        )
        if rejected_ratio > self.max_rejected_ratio:
            raise InstrumentMasterRefreshError(
                f"instrument master rejected {rejected_ratio:.2%} of records; "
                f"maximum is {self.max_rejected_ratio:.2%}"
            )

        return InstrumentMasterManifest(
            source_url=snapshot.source_url,
            fetched_at=fetched_at,
            payload_sha256=hashlib.sha256(payload).hexdigest(),
            instrument_count=snapshot.count,
            rejected_records=snapshot.rejected_records,
            duplicate_count=len(snapshot.duplicate_keys),
        )

    def refresh(self, url: str = UpstoxInstrumentMaster.COMPLETE_URL) -> InstrumentMasterSnapshot:
        """Fetch, validate and atomically publish a new snapshot.

        The current accepted snapshot remains available if validation fails.
        """
        payload = self.loader.source.fetch(url)
        candidate = self.loader.load(url)
        fetched_at = self.clock()
        manifest = self._validate_candidate(candidate, payload, fetched_at)

        self._snapshot = candidate
        self._manifest = manifest
        return candidate

    async def refresh_async(
        self, url: str = UpstoxInstrumentMaster.COMPLETE_URL
    ) -> InstrumentMasterSnapshot:
        """Serialize refreshes so overlapping scheduler ticks cannot publish races."""
        async with self._refresh_lock:
            return await asyncio.to_thread(self.refresh, url)

    async def run_periodically(
        self,
        *,
        interval: timedelta,
        url: str = UpstoxInstrumentMaster.COMPLETE_URL,
        stop_event: asyncio.Event | None = None,
    ) -> None:
        """Refresh immediately, then continue on a fixed interval until stopped."""
        if interval <= timedelta(0):
            raise ValueError("interval must be positive")
        event = stop_event or asyncio.Event()
        while not event.is_set():
            try:
                await self.refresh_async(url)
            except Exception:
                # Keep the last known-good snapshot. The worker's caller should
                # surface this failure through application observability/alerts.
                pass
            try:
                await asyncio.wait_for(event.wait(), timeout=interval.total_seconds())
            except asyncio.TimeoutError:
                continue
