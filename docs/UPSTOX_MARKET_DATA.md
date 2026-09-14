# Upstox V3 Market Data Boundary

## Scope

This document defines the broker-side lifecycle boundary for Upstox Market Data Feed V3. The adapter owns SDK callbacks, connection recovery, desired subscriptions and provider limits. Normalized market contracts cross into the domain; Upstox SDK/protobuf types do not.

## Current limits

The implementation defaults to the normal Upstox V3 limits documented by Upstox:

- 2 concurrent WebSocket connections per user
- LTPC: 5,000 instruments when used alone; 2,000 when combined with other feed categories
- Option Greeks: 3,000 instruments when used alone; 2,000 when combined
- Full: 2,000 instruments when used alone; 1,500 when combined
- Full D30: disabled by default because it is an Upstox Plus feature; when enabled, the manager accepts a configured 50-instrument individual limit

These are provider limits, not strategy or application limits. The manager is configurable so account-plan changes do not require changes to domain contracts.

Source: Upstox Market Data Feed V3 documentation.

## Desired subscription state

`UpstoxSubscriptionManager` keeps the application-level desired subscription set. This is separate from the broker socket's transient connection state so reconnect can replay the accepted subscriptions deterministically.

Subscription changes are deduplicated by instrument key within a request. Mode changes are validated against the same configured provider limits before the desired state is committed.

## Reconnect behavior

The adapter uses a generation token to distinguish the active connection from stale callbacks. An intentional disconnect increments the generation and cancels the reconnect task, so an old `close`/`error` callback cannot resurrect the connection.

Unexpected close/error schedules reconnect with bounded exponential backoff:

```text
1s → 2s → 4s → ... → 30s cap
```

The first successful reconnect creates a clean streamer and replays the desired subscriptions after the `open` callback. A failed reconnect leaves the desired subscription state intact and retries with the next backoff interval.

## Safety boundaries

- No order placement occurs in this adapter.
- No RiskEngine or OMS path is reachable from subscription recovery.
- Access tokens are supplied at runtime; none are stored in source.
- PAPER remains the platform default.
- Broker-specific SDK objects remain inside `adapters/upstox`.
- Reconnect does not fabricate market data; it waits for the provider snapshot/live stream to resume.

## Follow-up

The next ingestion hardening step is quote/depth sequencing and data-quality state: distinguish connection health from feed freshness, track snapshot-versus-live transitions, detect timestamp regressions/gaps, and ensure downstream candle construction consumes only valid ordered events.
