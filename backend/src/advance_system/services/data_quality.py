from __future__ import annotations

from datetime import datetime, timezone

from advance_system.domain.market_events import DataQuality


class DataQualityMonitor:
    def __init__(self, heartbeat_seconds: int = 15) -> None:
        self.heartbeat_seconds = heartbeat_seconds
        self.last_event_at: datetime | None = None

    def record_event(self, timestamp: datetime) -> None:
        self.last_event_at = timestamp

    def snapshot(self, now: datetime | None = None) -> DataQuality:
        current = now or datetime.now(timezone.utc)
        if self.last_event_at is None:
            return DataQuality(healthy=False, reason="NO_MARKET_DATA")
        lag_ms = max(0, int((current - self.last_event_at).total_seconds() * 1000))
        healthy = lag_ms <= self.heartbeat_seconds * 1000
        return DataQuality(
            healthy=healthy,
            reason=None if healthy else "STALE_MARKET_DATA",
            last_event_at=self.last_event_at,
            lag_ms=lag_ms,
        )
