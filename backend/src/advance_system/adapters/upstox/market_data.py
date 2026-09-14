from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone

from advance_system.adapters.upstox.feed_decoder import decode_quotes
from advance_system.adapters.upstox.subscriptions import (
    UPSTOX_MODES,
    UpstoxSubscription,
    UpstoxSubscriptionManager,
)
from advance_system.domain.market_events import NormalizedMarketStatus, NormalizedQuote


@dataclass(frozen=True)
class ReconnectPolicy:
    initial_delay_seconds: float = 1.0
    max_delay_seconds: float = 30.0

    def __post_init__(self) -> None:
        if self.initial_delay_seconds <= 0:
            raise ValueError("initial_delay_seconds must be positive")
        if self.max_delay_seconds < self.initial_delay_seconds:
            raise ValueError("max_delay_seconds must be >= initial_delay_seconds")


class UpstoxMarketDataAdapter:
    """Broker boundary for the official Upstox V3 market streamer.

    The adapter owns SDK lifecycle, reconnect/replay policy and feed decoding.
    Domain services receive only normalized contracts and never import Upstox
    SDK/protobuf types.
    """

    def __init__(
        self,
        access_token: str | None = None,
        *,
        streamer_factory: Callable[..., object] | None = None,
        subscription_manager: UpstoxSubscriptionManager | None = None,
        reconnect_policy: ReconnectPolicy | None = None,
    ) -> None:
        self.access_token = access_token
        self._streamer_factory = streamer_factory
        self._streamer: object | None = None
        self._last_event_at: datetime | None = None
        self._on_quote: Callable[[NormalizedQuote], Awaitable[None]] | None = None
        self._on_status: Callable[[NormalizedMarketStatus], Awaitable[None]] | None = None
        self.subscriptions = subscription_manager or UpstoxSubscriptionManager()
        self.reconnect_policy = reconnect_policy or ReconnectPolicy()
        self._connected = False
        self._intentional_disconnect = False
        self._generation = 0
        self._reconnect_task: asyncio.Task[None] | None = None

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
        return self._connected and self._streamer is not None

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
        if self.connected:
            return
        if not self.access_token:
            raise RuntimeError("Upstox access token is required to connect the market feed")
        if mode not in UPSTOX_MODES:
            raise ValueError(f"unsupported Upstox V3 mode: {mode}")
        if instrument_keys:
            self.subscriptions.add(instrument_keys, mode)
        self._intentional_disconnect = False
        self._generation += 1
        generation = self._generation
        self._open_streamer(
            instrument_keys=tuple(instrument_keys),
            mode=mode,
            generation=generation,
            replay_existing=False,
        )

    async def disconnect(self) -> None:
        self._intentional_disconnect = True
        self._generation += 1
        if self._reconnect_task:
            self._reconnect_task.cancel()
            self._reconnect_task = None
        streamer = self._streamer
        self._streamer = None
        self._connected = False
        if streamer is not None:
            streamer.disconnect()  # type: ignore[attr-defined]

    async def subscribe(self, instrument_keys: Sequence[str], mode: str = "ltpc") -> None:
        request = self.subscriptions.add(instrument_keys, mode)
        if not self.connected:
            raise RuntimeError("market feed is not connected")
        self._streamer.subscribe(list(request.instrument_keys), request.mode)  # type: ignore[attr-defined]

    async def unsubscribe(self, instrument_keys: Sequence[str]) -> None:
        if self._streamer is None:
            raise RuntimeError("market feed is not connected")
        self.subscriptions.remove(instrument_keys)
        self._streamer.unsubscribe(list(instrument_keys))  # type: ignore[attr-defined]

    async def change_mode(self, instrument_keys: Sequence[str], mode: str) -> None:
        if self._streamer is None:
            raise RuntimeError("market feed is not connected")
        if mode not in UPSTOX_MODES:
            raise ValueError(f"unsupported Upstox V3 mode: {mode}")
        self.subscriptions.change_mode(instrument_keys, mode)
        self._streamer.change_mode(list(instrument_keys), mode)  # type: ignore[attr-defined]

    def _open_streamer(
        self,
        *,
        instrument_keys: tuple[str, ...],
        mode: str,
        generation: int,
        replay_existing: bool,
    ) -> None:
        factory = self._streamer_factory or self._default_streamer_factory
        self._streamer = factory(instrument_keys, mode)
        streamer = self._streamer
        streamer.on("open", lambda: self._on_open(generation, replay_existing))  # type: ignore[attr-defined]
        streamer.on("message", self._on_message)  # type: ignore[attr-defined]
        streamer.on("close", lambda *_args: self._on_close(generation))  # type: ignore[attr-defined]
        streamer.on("error", lambda *_args: self._on_error(generation))  # type: ignore[attr-defined]
        streamer.connect()  # type: ignore[attr-defined]

    def _on_open(self, generation: int, replay_existing: bool) -> None:
        if generation != self._generation or self._intentional_disconnect:
            return
        self._connected = True
        self._last_event_at = datetime.now(timezone.utc)
        if replay_existing:
            streamer = self._streamer
            if streamer is None:
                return
            for subscription in self.subscriptions.subscriptions:
                streamer.subscribe(list(subscription.instrument_keys), subscription.mode)  # type: ignore[attr-defined]

    def _on_message(self, message: dict) -> None:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return
        loop.create_task(self.handle_message(message))

    def _on_close(self, generation: int) -> None:
        if generation != self._generation:
            return
        self._connected = False
        self._streamer = None
        self._schedule_reconnect(generation)

    def _on_error(self, generation: int) -> None:
        if generation != self._generation:
            return
        self._connected = False
        self._schedule_reconnect(generation)

    def _schedule_reconnect(self, generation: int) -> None:
        if self._intentional_disconnect or self._reconnect_task is not None:
            return
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return
        self._reconnect_task = loop.create_task(self._reconnect_loop(generation))

    async def _reconnect_loop(self, generation: int) -> None:
        delay = self.reconnect_policy.initial_delay_seconds
        try:
            while generation == self._generation and not self._intentional_disconnect:
                await asyncio.sleep(delay)
                if generation != self._generation or self._intentional_disconnect:
                    return
                try:
                    self._open_streamer(
                        instrument_keys=(),
                        mode="ltpc",
                        generation=generation,
                        replay_existing=True,
                    )
                    return
                except Exception:
                    delay = min(delay * 2, self.reconnect_policy.max_delay_seconds)
        except asyncio.CancelledError:
            return
        finally:
            if asyncio.current_task() is self._reconnect_task:
                self._reconnect_task = None

    def _default_streamer_factory(self, instrument_keys: tuple[str, ...], mode: str) -> object:
        import upstox_client

        configuration = upstox_client.Configuration()
        configuration.access_token = self.access_token
        api_client = upstox_client.ApiClient(configuration)
        return upstox_client.MarketDataStreamerV3(api_client, list(instrument_keys), mode)


__all__ = [
    "ReconnectPolicy",
    "UpstoxMarketDataAdapter",
    "UpstoxSubscription",
]
