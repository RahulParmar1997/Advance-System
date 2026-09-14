AGENTS.md — Trading Platform Coding Constitution
Mission
Build an India-focused professional Market Intelligence, Quant Research, Trading and Automation platform.
Architecture
Upstox → ingestion → normalization → validation → storage → candle/features → intelligence → scanner → opportunity → Trade Type → strategy → probability/EV → risk → OMS → execution → reconciliation → journal/research.
Non-negotiable rules
PAPER mode is always the default.
Never bypass RiskEngine or OMS.
Broker-specific code belongs only in adapters/upstox.
Domain logic must not make network/database calls.
Scanner and strategy builders produce typed AST/DSL, never executable Python from user input.
No look-ahead bias in backtests, replay, features or ML.
Raw, normalized, derived and model data remain separate.
PostgreSQL is application/OMS state, not the high-volume tick store.
Redis is hot/realtime state, not permanent historical storage.
ClickHouse is the primary high-volume market analytics store.
Chart UI is never the source of truth for orders or positions.
Internal OMS is the canonical application order state; broker status is reconciled into it.
Every strategy/model/feature contract must be versioned where behavior affects results.
SMC/ICT/Wyckoff are measurable hypotheses/lenses, never guaranteed predictions.
Do not silently change risk, execution, sizing, cost or backtest semantics.
Trading-critical code requires tests and deterministic replay where practical.
Do not enable live trading, real credentials or destructive operations by default.
Coding workflow
Before coding:
Read this file.
Read .ai/CURRENT_STATE.md.
Read .ai/DECISIONS.md.
Read the relevant docs.
Inspect existing code before creating new files.
While coding:
Prefer existing abstractions.
Avoid duplicate services.
Keep changes small and coherent.
Use typed interfaces.
Keep broker adapters isolated.
Preserve backward compatibility unless the task explicitly changes a contract.
After coding:
Run relevant tests.
Run type/lint checks where available.
Review changed files for accidental secrets or live execution.
Update .ai/CURRENT_STATE.md.
Update .ai/TODO.md if work changed.
Update .ai/CHANGELOG.md for meaningful changes.
Report what changed, tests run, known limitations and next step.
Stop and ask before
Changing architecture boundaries.
Changing database ownership.
Changing risk limits or position sizing semantics.
Enabling live execution.
Replacing the broker/data provider.
Removing auditability.
Deleting production data or migrations.
Adding a new major dependency when an existing dependency can solve the problem.
