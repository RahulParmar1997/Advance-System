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

## Next implementation

The next instrument-master increment should add:

1. scheduled/download integration
2. freshness and source checksum validation
3. atomic snapshot replacement
4. persistence suitable for PostgreSQL application state
5. lookup indexes by instrument key, trading symbol, ISIN, segment and underlying
6. expiry lifecycle handling for derivatives
7. reconciliation between the current master and active subscriptions

Do not make the instrument master a substitute for ClickHouse market history. It owns instrument identity and metadata; ClickHouse owns high-volume market observations.
