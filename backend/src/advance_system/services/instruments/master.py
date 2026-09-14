from __future__ import annotations

import gzip
import json
from typing import Any, Protocol

from advance_system.domain.instruments import InstrumentMasterSnapshot, parse_instrument_master


class InstrumentSource(Protocol):
    def fetch(self, url: str) -> bytes: ...


class UpstoxInstrumentMaster:
    """Fetch and validate Upstox BOD instrument JSON without leaking broker types into domain code."""

    COMPLETE_URL = "https://assets.upstox.com/market-quote/instruments/exchange/complete.json.gz"
    NSE_URL = "https://assets.upstox.com/market-quote/instruments/exchange/NSE.json.gz"
    BSE_URL = "https://assets.upstox.com/market-quote/instruments/exchange/BSE.json.gz"
    MCX_URL = "https://assets.upstox.com/market-quote/instruments/exchange/MCX.json.gz"

    def __init__(self, source: InstrumentSource) -> None:
        self.source = source

    def load(self, url: str = COMPLETE_URL) -> InstrumentMasterSnapshot:
        payload = self.source.fetch(url)
        records = decode_upstox_json(payload)
        return parse_instrument_master(records, source_url=url)


def decode_upstox_json(payload: bytes) -> list[dict[str, Any]]:
    """Decode gzipped or plain Upstox JSON instrument payloads."""
    raw = gzip.decompress(payload) if payload[:2] == b"\x1f\x8b" else payload
    decoded = json.loads(raw.decode("utf-8"))
    if not isinstance(decoded, list):
        raise ValueError("Upstox instrument payload must be a JSON array")
    if not all(isinstance(item, dict) for item in decoded):
        raise ValueError("Upstox instrument payload contains a non-object record")
    return decoded
