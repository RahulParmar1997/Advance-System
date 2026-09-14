from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import datetime, timezone

from advance_system.domain.market_events import NormalizedMarketStatus, NormalizedQuote


@dataclass(frozen=True)
class UpstoxSubscription:
    instrument_keys: tuple[str, ...]
    mode: str = "ltpc"


class UpstoxMarketDataAdapter:
    """Broker boundary only. Parsing/feature logic must stay outside this adapter."""

    def __init__(self, access_token: str | None = None) -> None:
        self.access_token = access_token
        self._last_event_at: datetime | None = None
        self._on_quote: Callable[[NormalizedQuote], Awaitable[None]] | None = None
        self._on_status: Callable[[NormalizedMarketStatus], Awaitable[None]] | None = None

    def set_handlers(
        self,
        on_quote: Callable[[NormalizedQuote], Awaitable[None]],
        on_status: Callable[[NormalizedMarketStatus], Awaitable[None]],
    ) -> None:
        self._on_quote = on_quote
        self._on_status = on_status

    @property
    def last_event_at(self) -> datetime | None:
        return self._last_event_at

    async def handle_normalized_quote(self, quote: NormalizedQuote) -> None:
        self._last_event_at = quote.timestamp
        if self._on_quote:
            await self._on_quote(quote)

    async def handle_status(self, status: NormalizedMarketStatus) -> None:
        self._last_event_at = status.timestamp
        if self._on_status:
            await self._on_status(status)

    async def connect(self) -> None:
        """TODO: wire official Upstox V3 WebSocket + protobuf client here."""
        return None

    async def disconnect(self) -> None:
        return None
