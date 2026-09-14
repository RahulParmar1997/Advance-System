from datetime import date
import gzip
import json

import pytest

from advance_system.domain.instruments import parse_instrument_master, parse_instrument_record
from advance_system.services.instruments.master import decode_upstox_json


def equity_record(**overrides):
    record = {
        "segment": "NSE_EQ",
        "name": "RELIANCE INDUSTRIES LTD",
        "exchange": "NSE",
        "isin": "INE002A01018",
        "instrument_type": "EQ",
        "instrument_key": "NSE_EQ|INE002A01018",
        "lot_size": 1,
        "freeze_quantity": 100000,
        "exchange_token": "2885",
        "tick_size": 0.05,
        "trading_symbol": "RELIANCE",
        "short_name": "Reliance Industries",
    }
    record.update(overrides)
    return record


def test_parse_equity_record():
    instrument = parse_instrument_record(equity_record())
    assert instrument.instrument_key == "NSE_EQ|INE002A01018"
    assert instrument.trading_symbol == "RELIANCE"
    assert instrument.lot_size == 1
    assert instrument.expiry is None


def test_parse_derivative_expiry_from_epoch_milliseconds():
    instrument = parse_instrument_record(
        equity_record(
            segment="NSE_FO",
            instrument_type="FUT",
            instrument_key="NSE_FO|12345",
            trading_symbol="RELIANCE FUT",
            expiry=1893455999000,
            underlying_key="NSE_EQ|INE002A01018",
            lot_size=500,
            strike_price=0,
        )
    )
    assert isinstance(instrument.expiry, date)
    assert instrument.underlying_key == "NSE_EQ|INE002A01018"


def test_duplicate_instrument_keys_are_reported_and_deduplicated():
    snapshot = parse_instrument_master(
        [equity_record(), equity_record(name="duplicate")],
        source_url="test://instruments",
    )
    assert snapshot.count == 1
    assert snapshot.duplicate_keys == ("NSE_EQ|INE002A01018",)
    assert snapshot.rejected_records == 0


def test_invalid_instrument_record_is_rejected():
    snapshot = parse_instrument_master(
        [equity_record(), {"segment": "NSE_EQ", "name": "missing required fields"}],
        source_url="test://instruments",
    )
    assert snapshot.count == 1
    assert snapshot.rejected_records == 1


def test_decode_plain_and_gzipped_json():
    payload = json.dumps([equity_record()]).encode()
    compressed = gzip.compress(payload)
    assert decode_upstox_json(payload)[0]["instrument_key"] == "NSE_EQ|INE002A01018"
    assert decode_upstox_json(compressed)[0]["instrument_key"] == "NSE_EQ|INE002A01018"


def test_decode_rejects_non_array_payload():
    with pytest.raises(ValueError, match="JSON array"):
        decode_upstox_json(b'{"instrument_key":"NSE_EQ|1"}')
