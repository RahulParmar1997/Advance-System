import pytest

from advance_system.adapters.upstox.subscriptions import (
    SubscriptionLimitError,
    UpstoxSubscriptionManager,
)


def test_single_mode_uses_individual_limit():
    manager = UpstoxSubscriptionManager(individual_limits={"ltpc": 2})
    manager.add(["A", "B"], "ltpc")
    with pytest.raises(SubscriptionLimitError):
        manager.add(["C"], "ltpc")


def test_multiple_modes_use_combined_limits():
    manager = UpstoxSubscriptionManager(
        individual_limits={"ltpc": 5, "full": 5},
        combined_limits={"ltpc": 2, "full": 1},
    )
    manager.add(["A", "B"], "ltpc")
    with pytest.raises(SubscriptionLimitError):
        manager.add(["C", "D"], "full")


def test_duplicate_keys_do_not_consume_extra_capacity():
    manager = UpstoxSubscriptionManager(individual_limits={"ltpc": 2})
    manager.add(["A", "A"], "ltpc")
    manager.add(["A"], "ltpc")
    assert manager.instrument_keys == ("A",)


def test_change_mode_is_rolled_back_when_target_mode_would_exceed_limit():
    manager = UpstoxSubscriptionManager(
        individual_limits={"ltpc": 5, "full": 1},
        combined_limits={"ltpc": 5, "full": 1},
    )
    manager.add(["A"], "ltpc")
    manager.add(["B"], "full")
    with pytest.raises(SubscriptionLimitError):
        manager.change_mode(["A"], "full")
    assert {(s.mode, s.instrument_keys) for s in manager.subscriptions} == {
        ("ltpc", ("A",)),
        ("full", ("B",)),
    }


def test_full_d30_can_be_disabled_for_non_plus_account():
    manager = UpstoxSubscriptionManager(individual_limits={"full_d30": 0})
    with pytest.raises(SubscriptionLimitError):
        manager.add(["A"], "full_d30")
