from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass


UPSTOX_MODES = frozenset({"ltpc", "full", "option_greeks", "full_d30"})


@dataclass(frozen=True)
class UpstoxSubscription:
    instrument_keys: tuple[str, ...]
    mode: str = "ltpc"

    def __post_init__(self) -> None:
        if not self.instrument_keys:
            raise ValueError("instrument_keys must not be empty")
        if self.mode not in UPSTOX_MODES:
            raise ValueError(f"unsupported Upstox V3 mode: {self.mode}")


class SubscriptionLimitError(ValueError):
    """Raised before a request can exceed configured V3 subscription limits."""


class UpstoxSubscriptionManager:
    """Track desired subscriptions and enforce the documented V3 limits.

    The limits are configurable so account-plan changes can be handled without
    changing domain contracts. The defaults represent the normal V3 limits, not
    Upstox Plus.
    """

    INDIVIDUAL_LIMITS = {
        "ltpc": 5000,
        "option_greeks": 3000,
        "full": 2000,
        "full_d30": 50,
    }
    COMBINED_LIMITS = {
        "ltpc": 2000,
        "option_greeks": 2000,
        "full": 1500,
        "full_d30": 1500,
    }

    def __init__(
        self,
        *,
        max_connections: int = 2,
        individual_limits: dict[str, int] | None = None,
        combined_limits: dict[str, int] | None = None,
    ) -> None:
        if max_connections < 1:
            raise ValueError("max_connections must be positive")
        self.max_connections = max_connections
        self.individual_limits = {**self.INDIVIDUAL_LIMITS, **(individual_limits or {})}
        self.combined_limits = {**self.COMBINED_LIMITS, **(combined_limits or {})}
        self._subscriptions: dict[str, UpstoxSubscription] = {}

    @property
    def subscriptions(self) -> tuple[UpstoxSubscription, ...]:
        return tuple(self._subscriptions.values())

    @property
    def instrument_keys(self) -> tuple[str, ...]:
        return tuple(
            dict.fromkeys(
                key
                for subscription in self._subscriptions.values()
                for key in subscription.instrument_keys
            )
        )

    def _validate_mode(self, mode: str) -> None:
        if mode not in UPSTOX_MODES:
            raise ValueError(f"unsupported Upstox V3 mode: {mode}")
        if mode == "full_d30" and self.individual_limits.get(mode, 0) <= 0:
            raise SubscriptionLimitError("full_d30 is not enabled for this account")

    def _counts_by_mode(self) -> dict[str, set[str]]:
        counts: dict[str, set[str]] = {mode: set() for mode in UPSTOX_MODES}
        for subscription in self._subscriptions.values():
            counts[subscription.mode].update(subscription.instrument_keys)
        return counts

    def _validate_limits(self, candidate: UpstoxSubscription) -> None:
        self._validate_mode(candidate.mode)
        counts = self._counts_by_mode()
        counts[candidate.mode].update(candidate.instrument_keys)
        active_modes = {mode for mode, keys in counts.items() if keys}

        if len(active_modes) == 1:
            limit = self.individual_limits[candidate.mode]
            if len(counts[candidate.mode]) > limit:
                raise SubscriptionLimitError(
                    f"{candidate.mode} subscription has {len(counts[candidate.mode])} "
                    f"unique instruments; individual limit is {limit}"
                )
            return

        for mode in active_modes:
            limit = self.combined_limits[mode]
            if len(counts[mode]) > limit:
                raise SubscriptionLimitError(
                    f"combined {mode} subscription has {len(counts[mode])} "
                    f"unique instruments; combined limit is {limit}"
                )

    def add(self, instrument_keys: Sequence[str], mode: str) -> UpstoxSubscription:
        keys = tuple(dict.fromkeys(instrument_keys))
        candidate = UpstoxSubscription(keys, mode)
        self._validate_limits(candidate)
        self._subscriptions[self._key(candidate)] = candidate
        return candidate

    def remove(self, instrument_keys: Sequence[str]) -> None:
        keys = set(instrument_keys)
        for subscription_id, subscription in tuple(self._subscriptions.items()):
            remaining = tuple(key for key in subscription.instrument_keys if key not in keys)
            if remaining:
                self._subscriptions[subscription_id] = UpstoxSubscription(remaining, subscription.mode)
            else:
                del self._subscriptions[subscription_id]

    def change_mode(self, instrument_keys: Sequence[str], mode: str) -> None:
        keys = tuple(dict.fromkeys(instrument_keys))
        self._validate_mode(mode)
        current = [
            subscription
            for subscription in self._subscriptions.values()
            if set(subscription.instrument_keys) & set(keys)
        ]
        candidate = UpstoxSubscription(keys, mode)
        for subscription in current:
            remaining = tuple(key for key in subscription.instrument_keys if key not in keys)
            if remaining:
                self._subscriptions[self._key(subscription)] = UpstoxSubscription(remaining, subscription.mode)
            else:
                self._subscriptions.pop(self._key(subscription), None)
        try:
            self._validate_limits(candidate)
        except Exception:
            for subscription in current:
                self._subscriptions[self._key(subscription)] = subscription
            raise
        self._subscriptions[self._key(candidate)] = candidate

    @staticmethod
    def _key(subscription: UpstoxSubscription) -> str:
        return f"{subscription.mode}:{','.join(subscription.instrument_keys)}"
