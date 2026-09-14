# Market Intelligence & Automated Trading Platform — Implementation Architecture

## Purpose

This document turns the **MARKET INTELLIGENCE & AUTOMATED TRADING PLATFORM Blue Print** into an implementation contract for `main`.

The platform is market-intelligence-first. Automated trading consumes qualified intelligence; it never becomes a second source of market truth.

## System boundary

```text
Broker / Exchange Feeds
        ↓
Ingestion → Normalization → Data Quality
        ↓
Hot State / Analytical Store / Raw Research Store
        ↓
Candle Engine → Feature Engine
        ↓
Market Intelligence
  ├─ Structure / SMC / ICT / Wyckoff
  ├─ Liquidity
  ├─ Volume / Profile
  ├─ Order Flow / Microstructure
  ├─ Futures / OI
  ├─ Options / IV / Greeks
  ├─ Breadth / Sectors
  └─ Regime
        ↓
Broad Market Scanner
        ↓
Trade Type Filter
        ↓
Strategy Engine → Probability / EV
        ↓
Risk Engine
        ↓
OMS → Paper Execution → Broker Adapter
        ↓
Fills / Positions / Journal / Pattern DNA / Research
```

## Canonical layers

### 1. Ingestion

Broker-specific adapters translate upstream protocols into internal events. No strategy or indicator code imports a broker SDK.

### 2. Normalization

Normalized events must carry at minimum:

- canonical instrument identifier
- event timestamp
- source timestamp when available
- event sequence when available
- event type
- source/provider
- payload version
- data-quality status

Normalization is deterministic and side-effect free.

### 3. Data quality

Every realtime stream is evaluated for:

- freshness / heartbeat
- timestamp regression
- sequence regression
- duplicate events
- impossible prices or sizes
- crossed/locked quote anomalies where applicable
- missing required fields
- reconnect generation changes
- snapshot-before-delta ordering

Invalid data is quarantined or marked unusable; it must not silently feed trading decisions.

### 4. Storage

- **PostgreSQL:** configuration, users, strategies, versions, trade types, orders, fills, positions, risk, audit.
- **ClickHouse:** ticks, quotes, depth, candles, options/futures observations, features, events, regimes, signals.
- **Redis:** current state and low-latency serving only.
- **Parquet + object storage:** immutable raw/research datasets and replay data.
- **DuckDB:** local analytical/research workflows.

### 5. Intelligence

Features are versioned. A feature must declare its input fields, timeframe, lookback, null behavior, and calculation version. Intelligence modules produce measurable events/scores rather than opaque labels.

### 6. Scanner

The broad scanner describes market conditions. The automated scanner evaluates setups against a selected Trade Type and Strategy. Scanner rules compile to a typed AST; arbitrary executable code is never accepted from user configuration.

### 7. Opportunity

An opportunity contains instrument, direction, trade type, strategy/version, regime, entry/stop/targets, component scores, probability, expected R, estimated costs, risk and an explanation including negative evidence.

### 8. Risk and OMS

No strategy can submit directly to a broker. The mandatory path is:

```text
Strategy → Opportunity → Risk Engine → OMS → Broker Adapter
```

Paper execution remains the default. Live execution requires explicit production configuration and additional controls.

## Realtime sequencing contract

For each instrument/stream:

1. Accept connection/status event.
2. Accept the broker snapshot.
3. Establish the current stream generation.
4. Accept live updates only after snapshot initialization.
5. Reject or quarantine stale/regressing updates.
6. Update normalized state atomically.
7. Publish only quality-approved events downstream.
8. On reconnect, create a new generation and require a fresh snapshot before deltas are considered authoritative.

## Testing contract

Trading-critical components require deterministic unit tests and replay tests. Tests must cover normal events, malformed events, duplicates, timestamp/sequence regressions, reconnect generations, stale data and partial/missing fields.

A full repository test run is required before claiming a milestone complete. If infrastructure prevents the run, report the limitation explicitly rather than claiming success.

## Product priority

The next implementation milestones are:

1. Canonical market-event/data-quality contracts.
2. Candle engine.
3. ClickHouse market-data schema and repository boundary.
4. Feature engine foundations.
5. Market Intelligence modules.
6. Broad Market Scanner and typed DSL.
7. Trade Type filter.
8. Opportunity/probability/EV engine.
9. Risk/OMS hardening and paper execution.
10. Realtime chart/dashboard and research loop.
