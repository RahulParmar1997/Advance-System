from datetime import datetime, timedelta, timezone

from advance_system.services.data_quality import DataQualityMonitor


def test_no_event_is_unhealthy() -> None:
    monitor = DataQualityMonitor(heartbeat_seconds=15)
    assert monitor.snapshot().healthy is False
    assert monitor.snapshot().reason == "NO_MARKET_DATA"


def test_fresh_event_is_healthy() -> None:
    now = datetime.now(timezone.utc)
    monitor = DataQualityMonitor(heartbeat_seconds=15)
    monitor.record_event(now)
    quality = monitor.snapshot(now)
    assert quality.healthy is True
    assert quality.lag_ms == 0


def test_stale_event_is_unhealthy() -> None:
    now = datetime.now(timezone.utc)
    monitor = DataQualityMonitor(heartbeat_seconds=15)
    monitor.record_event(now - timedelta(seconds=16))
    quality = monitor.snapshot(now)
    assert quality.healthy is False
    assert quality.reason == "STALE_MARKET_DATA"
