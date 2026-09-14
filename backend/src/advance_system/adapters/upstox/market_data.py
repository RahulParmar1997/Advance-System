from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone

from advance_system.adapters.upstox.feed_decoder import decode_quotes
from advance_system.domain.market_events import NormalizedMarketStatus, NormalizedQuote


@dataclass(frozen=True)
class UpstoxSubscription:
    instrument_keys: tuple[str, ...]
    mode: str = "ltpc"

    def __post_init__(self) -> None:
        if not self.instrument_keys:
            raise ValueError("instrument_keys must not be empty")
        if self.mode not in {"ltpc", "full", "option_greeks", "full_d30"}:
            raise ValueError(f"unsupported Upstox V3 mode: {self.mode}")


class UpstoxMarketDataAdapter:
    """Broker boundary for the official Upstox V3 market streamer.

    The adapter owns SDK lifecycle and feed decoding. Domain services receive only
    normalized contracts and never import Upstox SDK/protobuf types.
    """

    def __init__(
        self,
        access_token: str | None = None,
        *,
        streamer_factory: Callable[..., object] | None = None,
    ) -> None:
        self.access_token = access_token
        self._streamer_factory = streamer_factory
        self._streamer: object | None = None
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

    @property
    def connected(self) -> bool:
        return self._streamer is not None

    async def handle_normalized_quote(self, quote: NormalizedQuote) -> None:
        self._last_event_at = quote.timestamp
        if self._on_quote:
            await self._on_quote(quote)

    async def handle_status(self, status: NormalizedMarketStatus) -> None:
        self._last_event_at = status.timestamp
        if self._on_status:
            await self._on_status(status)

    async def handle_message(self, message: dict) -> None:
        for quote in decode_quotes(message):
            await self.handle_normalized_quote(quote)

    async def connect(
        self,
        instrument_keys: Sequence[str] = (),
        mode: str = "ltpc",
    ) -> None:
        if self._streamer is not None:
            return
        if not self.access_token:
            raise RuntimeError("Upstox access token is required to connect the market feed")
        if mode not in {"ltpc", "full", "option_greeks", "full_d30"}:
            raise ValueError(f"unsupported Upstox V3 mode: {mode}")

        factory = self._streamer_factory or self._default_streamer_factory
        self._streamer = factory(tuple(instrument_keys), mode)
        streamer = self._streamer

        # Upstox SDK callbacks are synchronous; bridge into the async domain
        # without allowing broker code to leak into domain services.
        streamer.on("open", self._on_open)  # type: ignore[attr-defined]
        streamer.on("message", self._on_message)  # type: ignore[attr-defined]
        streamer.on("close", self._on_close)  # type: ignore[attr-defined]
        streamer.on("error", self._on_error)  # type: ignore[attr-defined]
        streamer.connect()  # type: ignore[attr-defined]

    async def disconnect(self) -> None:
        if self._streamer is None:
            return
        streamer = self._streamer
        self._streamer = None
        streamer.disconnect()  # type: ignore[attr-defined]

    async def subscribe(self, instrument_keys: Sequence[str], mode: str = "ltpc") -> None:
        if self._streamer is None:
            raise RuntimeError("market feed is not connected")
        UpstoxSubscription(tuple(instrument_keys), mode)
        self._streamer.subscribe(list(instrument_keys), mode)  # type: ignore[attr-defined]

    async def unsubscribe(self, instrument_keys: Sequence[str]) -> None:
        if self._streamer is None:
            raise RuntimeError("market feed is not connected")
        self._streamer.unsubscribe(list(instrument_keys))  # type: ignore[attr-defined]

    async def change_mode(self, instrument_keys: Sequence[str], mode: str) -> None:
        if self._streamer is None:
            raise RuntimeError("market feed is not connected")
        UpstoxSubscription(tuple(instrument_keys), mode)
        self._streamer.change_mode(list(instrument_keys), mode)  # type: ignore[attr-defined]

    def _on_open(self) -> None:
        self._last_event_at = datetime.now(timezone.utc)

    def _on_message(self, message: dict) -> None:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return
        loop.create_task(self.handle_message(message))

    def _on_close(self, *_args: object) -> None:
        self._streamer = None

    def _on_error(self, *_args: object) -> None:
        # Data-quality monitoring owns failure policy/reconnect decisions.
        return None

    def _default_streamer_factory(self, instrument_keys: tuple[str, ...], mode: str) -> object:
        import upstox_client

        configuration = upstox_client.Configuration()
        configuration.access_token = self.access_token
        api_client = upstox_client.ApiClient(configuration)
        return upstox_client.MarketDataStreamerV3(api_client, list(instrument_keys), mode)
