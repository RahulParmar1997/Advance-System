from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class InstrumentType(StrEnum):
    EQUITY = "EQ"
    FUTURE = "FUT"
    CALL = "CE"
    PUT = "PE"
    INDEX = "INDEX"


class Instrument(BaseModel):
    """Canonical instrument contract independent of the broker SDK."""

    model_config = ConfigDict(extra="allow")

    instrument_key: str = Field(min_length=3)
    segment: str = Field(min_length=1)
    exchange: str = Field(min_length=1)
    name: str = Field(min_length=1)
    trading_symbol: str = Field(min_length=1)
    instrument_type: str = Field(min_length=1)
    exchange_token: str | None = None
    isin: str | None = None
    underlying_key: str | None = None
    underlying_symbol: str | None = None
    expiry: date | None = None
    strike_price: Decimal | None = None
    lot_size: int | None = Field(default=None, ge=1)
    minimum_lot: int | None = Field(default=None, ge=1)
    freeze_quantity: Decimal | None = Field(default=None, gt=0)
    tick_size: Decimal | None = Field(default=None, gt=0)
    weekly: bool | None = None
    source: str = "upstox_bod_json"
    source_updated_at: datetime | None = None

    @field_validator("instrument_key")
    @classmethod
    def validate_instrument_key(cls, value: str) -> str:
        if "|" not in value:
            raise ValueError("instrument_key must contain a segment separator '|'")
        return value


class InstrumentMasterSnapshot(BaseModel):
    """Validated point-in-time instrument master snapshot."""

    as_of: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source_url: str
    instruments: tuple[Instrument, ...]
    duplicate_keys: tuple[str, ...] = ()
    rejected_records: int = 0

    @property
    def count(self) -> int:
        return len(self.instruments)


def _expiry_from_upstox(value: Any) -> date | None:
    if value in (None, "", 0, 0.0):
        return None
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value / 1000, tz=timezone.utc).date()
    if isinstance(value, str):
        return date.fromisoformat(value[:10])
    raise ValueError(f"unsupported expiry value: {type(value).__name__}")


def parse_instrument_record(record: dict[str, Any]) -> Instrument:
    """Map an Upstox JSON BOD record into the canonical contract."""
    normalized = dict(record)
    normalized["expiry"] = _expiry_from_upstox(record.get("expiry"))
    if normalized.get("exchange_token") is not None:
        normalized["exchange_token"] = str(normalized["exchange_token"])
    return Instrument.model_validate(normalized)


def parse_instrument_master(records: list[dict[str, Any]], source_url: str) -> InstrumentMasterSnapshot:
    """Validate a complete BOD payload and reject duplicate instrument keys deterministically."""
    instruments: list[Instrument] = []
    seen: set[str] = set()
    duplicates: list[str] = []
    rejected = 0

    for record in records:
        try:
            instrument = parse_instrument_record(record)
        except (TypeError, ValueError):
            rejected += 1
            continue
        if instrument.instrument_key in seen:
            duplicates.append(instrument.instrument_key)
            continue
        seen.add(instrument.instrument_key)
        instruments.append(instrument)

    return InstrumentMasterSnapshot(
        source_url=source_url,
        instruments=tuple(instruments),
        duplicate_keys=tuple(sorted(set(duplicates))),
        rejected_records=rejected,
    )
