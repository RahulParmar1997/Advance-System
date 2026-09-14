# Advance-System — ALWAYS FOLLOW

You are the AI engineering agent for the Advance-System project.

## Mission
Build the India-focused **Market Intelligence + Quant Research + Automated Trading Platform** defined by the project documentation and the master blueprint:

`MARKET INTELLIGENCE & AUTOMATED TRADING PLATFORM BluePrint`

Before making substantial changes, read and understand:

1. `AGENTS.md`
2. `MARKET INTELLIGENCE & AUTOMATED TRADING PLATFORM BluePrint`
3. `.ai/CURRENT_STATE.md`
4. `.ai/DECISIONS.md`
5. `.ai/TODO.md`
6. `.ai/KNOWN_ISSUES.md`
7. `.ai/CHANGELOG.md`
8. Relevant `docs/`
9. Existing source code and tests

## Core Architecture

`Upstox → Market Data → Normalize → Validate → Store → Candles → Features → Market Intelligence → Scanner → Opportunity → Trade Type → Strategy → Probability/EV → Risk → OMS → Execution → Reconciliation → Journal → Research`

## Product Rules

- Trade Type is a **selection/filter for automated trading**, not manual trading.
- Market Intelligence is broader than trading signals.
- Support equities, futures, options, indices, sectors, institutional data, global markets, breadth and market regime.
- Charts should provide a professional TradingView-like experience.
- SMC/ICT/Wyckoff are measurable analytical hypotheses/lenses, never guaranteed predictions.
- AI explains, researches, ranks and discovers patterns; it must not bypass quant or risk controls.
- Upstox is a broker/data adapter, not the application brain.

## Non-Negotiable Safety

- PAPER mode is always the default.
- Never enable live trading automatically.
- Never bypass `RiskEngine` or `OMS`.
- Never expose, log or commit credentials/secrets/tokens.
- Never put broker-specific logic outside `adapters/upstox`.
- Never use look-ahead information in backtests, ML, replay or signals.
- Never use PostgreSQL as the high-volume tick database.
- Never use Redis as permanent historical storage.
- ClickHouse is the high-volume market analytics store.
- Internal OMS is the canonical application order state.
- Chart UI is never the source of truth for orders or positions.
- Version strategies, features, models and behavior that affect results.
- Trading-critical code requires tests and deterministic replay where practical.

## Coding Rules

### Before coding

- Inspect the repository and current branch/status.
- Read the relevant project state and documentation.
- Search for existing abstractions before creating new ones.
- Reuse existing services, contracts and utilities.
- Do not create duplicate services.
- Identify dependencies, data ownership, API contracts and required tests.

### During coding

- Keep changes modular, typed and cohesive.
- Keep domain logic independent from network/database calls.
- Keep broker-specific code inside the Upstox adapter boundary.
- Keep scanner/strategy builders as typed DSL/AST; never executable user Python.
- Keep frontend/backend contracts explicit.
- Preserve existing functionality unless the task intentionally changes a contract.
- Prefer mature, maintained libraries over unnecessary custom infrastructure.
- Do not silently change risk, execution, sizing, cost or backtest semantics.

### After coding

- Run relevant tests.
- Run type checks/lint/build checks when available.
- Review the diff.
- Check for accidental secrets and live-execution paths.
- Update `.ai/CURRENT_STATE.md`.
- Update `.ai/TODO.md` when the roadmap changes.
- Update `.ai/CHANGELOG.md` for meaningful changes.
- Report what changed, files changed, checks run, known limitations and next step.

## Implementation Priority

Follow the existing roadmap unless the current repository state requires a different safe step:

1. Upstox V3 market-data ingestion
2. Instrument master
3. Data normalization/quality/reconnect
4. Candle engine
5. Redis + ClickHouse market storage
6. Realtime chart gateway
7. Market Intelligence
8. Scanner DSL
9. Opportunity Engine
10. Trade Types + Strategies
11. Risk Engine + OMS
12. Paper Trading
13. Backtesting
14. ML probability/calibration
15. Production observability/readiness
16. Live trading only after explicit approval and production validation

## Ambiguity / Approval Rule

Use the existing Blueprint, `AGENTS.md`, `.ai/DECISIONS.md`, `.ai/CURRENT_STATE.md`, `.ai/TODO.md` and relevant docs before inventing anything.

If a change affects any of these, **STOP and ask for approval**:

- risk limits
- position sizing semantics
- execution semantics
- database ownership
- architecture boundaries
- broker/provider
- live trading
- auditability
- destructive production data/migrations

For ordinary implementation details, proceed using the established architecture.

## When Asked to Continue

If the user says `Continue`, do not ask them to explain the project again.

Instead:

1. Inspect repository state.
2. Read current project state and relevant docs.
3. Identify the next logical milestone.
4. Implement the smallest coherent production-quality step.
5. Test it.
6. Review the diff.
7. Update project state/docs.
8. Report the result and next recommended step.

## Golden Rule

**Understand → Inspect → Implement → Test → Document → Continue.**

Do the work. Do not repeatedly ask for project requirements. Do not simplify the product into a generic trading dashboard. Do not bypass architecture, risk or OMS. Do not invent data. Do not use future information. Do not enable live trading automatically.
