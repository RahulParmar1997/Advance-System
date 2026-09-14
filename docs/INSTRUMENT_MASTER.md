# Instrument Master

## Purpose

The instrument master is the canonical mapping between Upstox market instruments and the platform's instrument identity used by market data, candles, analytics, scanners and charting.

## Source

Use Upstox's BOD JSON instrument files rather than the deprecated CSV format. Upstox documents `instrument_key` as the unique identifier and recommends the JSON format for programmatic processing.

The loader currently supports the documented complete, NSE, BSE and MCX JSON endpoints and accepts either gzip-compressed or plain JSON payloads.

## Boundary

```text
Upstox BOD JSON
    ↓
Adapter/loader
    ↓
Canonical Instrument model
    ↓
Validation
    ↓
Validated refresh snapshot
    ↓
Instrument Master Store (future)
    ↓
Market Data / Candle / Analytics / Chart
```

The domain model does not import Upstox SDK types.

## Validation

Each record requires:

- `instrument_key`
- `segment`
- `exchange`
- `name`
- `trading_symbol`
- `instrument_type`

The canonical model also normalizes:

- exchange token to string
- derivative expiry to `date`
- lot/freeze/tick constraints
- underlying references where supplied

Duplicate `instrument_key` values are reported and only the first valid record is retained. Invalid records are counted rather than silently inserted.

## Refresh and freshness

`InstrumentMasterRefresher` wraps the loader with a production-safety gate:

- fetches exactly one source payload per refresh
- validates a minimum accepted instrument count
- rejects a candidate whose invalid-record ratio exceeds the configured threshold
- records SHA-256 of the exact source payload
- exposes accepted fetch metadata through an immutable manifest
- publishes a candidate only after validation succeeds
- keeps the last known-good snapshot when a refresh fails
- reports freshness from the timestamp of the last accepted fetch
- serializes concurrent async refreshes
- supports an immediate refresh followed by a fixed scheduler interval

The default freshness window is 24 hours. Production workers should emit metrics/alerts for repeated failures and stale snapshots. Persistence is intentionally outside the refresher so the service does not establish a new database ownership boundary.

## Current integration status

The instrument identity layer is now separate from the V3 socket lifecycle. `UpstoxSubscriptionManager` consumes canonical instrument keys and enforces provider subscription limits; the market-data adapter owns reconnect/replay. The instrument master does not own WebSocket connections.

## Next implementation

The next instrument-master increment should add:

1. persistent snapshot storage suitable for PostgreSQL application state
2. lookup indexes by instrument key, trading symbol, ISIN, segment and underlying
3. expiry lifecycle handling for derivatives
4. reconciliation between the current master and active subscriptions

Do not make the instrument master a substitute for ClickHouse market history. It owns instrument identity and metadata; ClickHouse owns high-volume market observations.
