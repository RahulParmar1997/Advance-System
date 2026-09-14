Current State
Updated: 2026-09-14

Project phase
Foundation / Upstox V3 ingestion.

Implemented in this increment
- Typed backend package foundation under backend/src/advance_system.
- PAPER-first environment settings; LIVE requires explicit production + LIVE configuration.
- Normalized market event contracts for quote/status/quality.
- Upstox adapter boundary isolated from domain logic.
- Realtime heartbeat/data-quality monitor with stale-data detection.
- Added Upstox V3 feed decoder for SDK-decoded LTPC/full messages.
- Added Upstox MarketDataStreamerV3 lifecycle boundary with subscribe/unsubscribe/change-mode operations.
- Added async bridge from SDK callbacks into normalized domain quote handlers.
- Corrected backend dependency to the maintained official upstox-python-sdk package.
- Added decoder unit tests covering LTPC, full-feed depth/OI and unknown messages.
- Added canonical instrument master model independent of broker SDK types.
- Added Upstox BOD JSON/gzip decoder with expiry normalization, duplicate-key detection and invalid-record rejection.
- Added instrument master parsing tests.
- Added safe instrument-master refresh service with minimum-count and invalid-record-ratio gates.
- Added SHA-256 source manifest and explicit freshness checks.
- Refresh publishes only validated candidates and preserves the last known-good snapshot on failure.
- Added serialized async refresh and periodic worker-loop support without introducing a new scheduler dependency.
- Added refresh tests for single-fetch behavior, freshness, rejection safety and invalid policy configuration.

Current priority
Complete production-grade Upstox V3 market-data ingestion without introducing broker logic into the domain, then connect normalized realtime data to instrument master, ClickHouse, Redis, candle engine and the chart.

Next milestones
1. Upstox OAuth/token lifecycle and secure credential handling.
2. Persistent instrument-master snapshot storage and lookup indexes.
3. V3 reconnect/resubscribe state machine and subscription-limit enforcement.
4. Quote/depth normalization and data-quality sequencing.
5. Candle engine and closed-candle guarantees.
6. ClickHouse market schema + batched writer.
7. Redis realtime state + event fan-out.
8. Realtime chart gateway and TradingView-like chart state.
9. Market intelligence modules: structure, liquidity, profile, order flow, futures/options, breadth and regime.
10. Typed scanner DSL → opportunity engine → Trade Type → strategy → probability/EV.
11. Risk/OMS hardening and paper execution simulator.
12. Event-driven backtester with costs, slippage and deterministic replay.
13. ML calibration, observability and production readiness.

Not production-ready
- Live execution
- Broker reconciliation
- Full options analytics
- Full order-flow reconstruction
- Production-grade backtester
- ML probability model
- HA/disaster recovery
- Persistent instrument-master repository and distributed worker deployment

Safety
No broker credentials, tokens or live-order implementation were added. PAPER remains the default.
