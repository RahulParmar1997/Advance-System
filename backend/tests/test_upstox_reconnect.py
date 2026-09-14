import asyncio

import pytest

from advance_system.adapters.upstox.market_data import ReconnectPolicy, UpstoxMarketDataAdapter


class FakeStreamer:
    def __init__(self, keys, mode):
        self.keys = tuple(keys)
        self.mode = mode
        self.handlers = {}
        self.connected = False
        self.subscriptions = []

    def on(self, event, handler):
        self.handlers[event] = handler

    def connect(self):
        self.connected = True
        self.handlers["open"]()

    def disconnect(self):
        self.connected = False

    def subscribe(self, keys, mode):
        self.subscriptions.append((tuple(keys), mode))

    def unsubscribe(self, keys):
        return None

    def change_mode(self, keys, mode):
        return None


@pytest.mark.asyncio
async def test_close_reconnects_and_replays_desired_subscriptions():
    streamers = []

    def factory(keys, mode):
        streamer = FakeStreamer(keys, mode)
        streamers.append(streamer)
        return streamer

    adapter = UpstoxMarketDataAdapter(
        access_token="paper-token",
        streamer_factory=factory,
        reconnect_policy=ReconnectPolicy(0.001, 0.002),
    )
    await adapter.connect(["A", "B"], "ltpc")
    assert adapter.connected

    streamers[0].handlers["close"]()
    await asyncio.sleep(0.01)

    assert len(streamers) >= 2
    assert streamers[1].subscriptions == [(("A", "B"), "ltpc")]
    assert adapter.connected
    await adapter.disconnect()


@pytest.mark.asyncio
async def test_explicit_disconnect_does_not_reconnect():
    streamers = []

    def factory(keys, mode):
        streamer = FakeStreamer(keys, mode)
        streamers.append(streamer)
        return streamer

    adapter = UpstoxMarketDataAdapter(
        access_token="paper-token",
        streamer_factory=factory,
        reconnect_policy=ReconnectPolicy(0.001, 0.002),
    )
    await adapter.connect(["A"], "ltpc")
    await adapter.disconnect()
    await asyncio.sleep(0.01)
    assert len(streamers) == 1
    assert not adapter.connected
