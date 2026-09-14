Current State
Updated: 2026-09-14

Project phase
Foundation / vibe-coding bootstrap.

Implemented in this increment
- Typed backend package foundation under backend/src/advance_system.
- PAPER-first environment settings; LIVE requires explicit production + LIVE configuration.
- Normalized market event contracts for quote/status/quality.
- Upstox adapter boundary isolated from domain logic.
- Realtime heartbeat/data-quality monitor with stale-data detection.
- Unit tests for data-quality behavior.

Current priority
Build production-grade Upstox V3 market-data ingestion and connect normalized realtime data to ClickHouse, feature engine and the chart.

Next milestones
1. Upstox OAuth/token lifecycle and secure credential handling.
2. V3 WebSocket + protobuf implementation using the official SDK.
3. Instrument master ingestion and validation.
4. Quote/depth normalization and reconnect/resubscribe state machine.
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

Safety
No broker credentials, tokens or live-order implementation were added. PAPER remains the default.
