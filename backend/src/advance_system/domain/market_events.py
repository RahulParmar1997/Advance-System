from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, Field


class MarketEventType(StrEnum):
    STATUS = "status"
    QUOTE = "quote"
    DEPTH = "depth"
    CANDLE = "candle"


class MarketStatus(StrEnum):
    OPEN = "open"
    CLOSED = "closed"
    PRE_OPEN = "pre_open"
    UNKNOWN = "unknown"


class NormalizedQuote(BaseModel):
    instrument_key: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    ltp: Decimal | None = None
    ltq: int | None = None
    volume: int | None = None
    oi: int | None = None
    bid_price: Decimal | None = None
    bid_qty: int | None = None
    ask_price: Decimal | None = None
    ask_qty: int | None = None
    source: str = "upstox_v3"
    sequence: int | None = None


class NormalizedMarketStatus(BaseModel):
    instrument_key: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: MarketStatus = MarketStatus.UNKNOWN
    source: str = "upstox_v3"


class DataQuality(BaseModel):
    healthy: bool
    reason: str | None = None
    last_event_at: datetime | None = None
    lag_ms: int | None = None
