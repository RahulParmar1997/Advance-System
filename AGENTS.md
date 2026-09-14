# AGENTS.md

## Project

India-focused Market Intelligence + Quant Research +
Automated Trading Platform.

## Core architecture

Upstox
→ ingestion
→ normalization
→ validation
→ storage
→ feature engine
→ market intelligence
→ scanner
→ opportunity engine
→ Trade Type
→ strategy
→ probability/EV
→ risk
→ OMS
→ execution
→ Upstox

## Critical rules

1. PAPER mode is the default.
2. Never bypass RiskEngine.
3. Never bypass OMS.
4. Never put broker-specific code inside strategies.
5. Never put database/network calls inside pure strategy calculations.
6. Scanner UI must generate typed AST/DSL, never executable Python.
7. Never introduce look-ahead bias.
8. Every strategy must have a version.
9. Every ML model must have a version.
10. Never treat SMC/ICT/Wyckoff as guaranteed predictions.
11. Raw market data must remain separate from derived features.
12. PostgreSQL is not the high-volume tick store.
13. Redis is not permanent historical storage.
14. Chart UI is not the source of truth for orders.
15. Broker state must be reconciled with internal OMS state.
16. Trading-critical changes require tests.

## Before coding

Read:
- .ai/CURRENT_STATE.md
- docs/ARCHITECTURE.md
- relevant domain documentation
- docs/RISK_RULES.md for trading/execution changes

## After coding

1. Run tests.
2. Check type errors.
3. Check lint.
4. Update CURRENT_STATE.md.
5. Update CHANGELOG.md.
6. Explain files changed and why.

## Do not

- Rewrite architecture without approval.
- Replace libraries without justification.
- Add random indicators.
- create duplicate services.
- hard-code broker credentials.
- enable live trading by default.
