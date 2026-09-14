from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any

from advance_system.domain.market_events import NormalizedQuote


def _number(value: Any) -> Decimal | None:
    if value is None or value == "":
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None


def _integer(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def _timestamp_ms(value: Any) -> datetime | None:
    parsed = _integer(value)
    if parsed is None:
        return None
    return datetime.fromtimestamp(parsed / 1000, tz=timezone.utc)


def _first(mapping: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in mapping:
            return mapping[key]
    return None


def decode_quotes(message: dict[str, Any]) -> list[NormalizedQuote]:
    """Convert an Upstox V3 SDK-decoded message into domain quote contracts.

    This intentionally accepts the SDK's JSON-compatible dictionary rather than
    importing protobuf types into the domain. Unknown fields are ignored so the
    broker adapter remains resilient to additive feed changes.
    """
    feeds = message.get("feeds")
    if not isinstance(feeds, dict):
        return []

    received_at = _timestamp_ms(message.get("currentTs"))
    quotes: list[NormalizedQuote] = []

    for instrument_key, feed in feeds.items():
        if not isinstance(feed, dict):
            continue

        # V3 full feeds place LTPC under marketFF/fullFeed depending on mode.
        full_feed = feed.get("fullFeed")
        if not isinstance(full_feed, dict):
            full_feed = feed.get("marketFF")
        if not isinstance(full_feed, dict):
            full_feed = feed

        ltpc = full_feed.get("ltpc")
        if not isinstance(ltpc, dict):
            ltpc = feed.get("ltpc")
        if not isinstance(ltpc, dict):
            continue

        timestamp = _timestamp_ms(ltpc.get("ltt")) or received_at
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)

        market_level = full_feed.get("marketLevel")
        bid_price = bid_qty = ask_price = ask_qty = None
        if isinstance(market_level, dict):
            levels = market_level.get("bidAskQuote")
            if isinstance(levels, list) and levels:
                best = levels[0]
                if isinstance(best, dict):
                    bid_price = _number(_first(best, "bidP", "bidPrice"))
                    bid_qty = _integer(_first(best, "bidQ", "bidQty"))
                    ask_price = _number(_first(best, "askP", "askPrice"))
                    ask_qty = _integer(_first(best, "askQ", "askQty"))

        quotes.append(
            NormalizedQuote(
                instrument_key=str(instrument_key),
                timestamp=timestamp,
                ltp=_number(ltpc.get("ltp")),
                ltq=_integer(ltpc.get("ltq")),
                volume=_integer(_first(full_feed, "vtt", "volume")),
                oi=_integer(_first(full_feed, "oi", "openInterest")),
                bid_price=bid_price,
                bid_qty=bid_qty,
                ask_price=ask_price,
                ask_qty=ask_qty,
                source="upstox_v3",
            )
        )

    return quotes
