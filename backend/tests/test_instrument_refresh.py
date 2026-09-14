import gzip
import json
from datetime import datetime, timedelta, timezone

import pytest

from advance_system.services.instruments.master import UpstoxInstrumentMaster
from advance_system.services.instruments.refresh import (
    InstrumentMasterRefreshError,
    InstrumentMasterRefresher,
)


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
    }
    record.update(overrides)
    return record


class FakeSource:
    def __init__(self, payload: bytes):
        self.payload = payload
        self.calls = 0

    def fetch(self, url: str) -> bytes:
        self.calls += 1
        return self.payload


def payload(*records):
    return gzip.compress(json.dumps(list(records)).encode())


def test_refresh_fetches_once_and_publishes_manifest():
    source = FakeSource(payload(equity_record()))
    loader = UpstoxInstrumentMaster(source)
    now = datetime(2026, 9, 14, tzinfo=timezone.utc)
    refresher = InstrumentMasterRefresher(loader, clock=lambda: now)

    snapshot = refresher.refresh("test://instruments")

    assert source.calls == 1
    assert snapshot.count == 1
    assert refresher.snapshot is snapshot
    assert refresher.manifest is not None
    assert len(refresher.manifest.payload_sha256) == 64
    assert refresher.is_fresh(now)
    assert not refresher.is_fresh(now + timedelta(hours=25))


def test_rejected_ratio_blocks_candidate_without_replacing_last_good_snapshot():
    good_source = FakeSource(payload(equity_record()))
    loader = UpstoxInstrumentMaster(good_source)
    now = datetime(2026, 9, 14, tzinfo=timezone.utc)
    refresher = InstrumentMasterRefresher(loader, max_rejected_ratio=0.1, clock=lambda: now)
    refresher.refresh("test://good")
    previous = refresher.snapshot

    bad_source = FakeSource(payload(equity_record(), {"broken": True}))
    refresher.loader = UpstoxInstrumentMaster(bad_source)
    with pytest.raises(InstrumentMasterRefreshError, match="rejected"):
        refresher.refresh("test://bad")

    assert refresher.snapshot is previous


def test_minimum_count_blocks_empty_candidate():
    source = FakeSource(payload())
    refresher = InstrumentMasterRefresher(
        UpstoxInstrumentMaster(source), min_instruments=1
    )

    with pytest.raises(InstrumentMasterRefreshError, match="minimum"):
        refresher.refresh("test://empty")


def test_constructor_rejects_invalid_refresh_policy():
    source = FakeSource(payload(equity_record()))
    loader = UpstoxInstrumentMaster(source)
    with pytest.raises(ValueError):
        InstrumentMasterRefresher(loader, max_age=timedelta(0))
    with pytest.raises(ValueError):
        InstrumentMasterRefresher(loader, min_instruments=0)
    with pytest.raises(ValueError):
        InstrumentMasterRefresher(loader, max_rejected_ratio=1)
