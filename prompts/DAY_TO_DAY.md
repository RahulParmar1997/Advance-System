# Advance-System — Day-to-Day Prompt

Use this short prompt for normal development requests after the permanent rules in `prompts/ALWAYS.md` are understood.

> **Continue working on Advance-System according to `AGENTS.md`, `MARKET INTELLIGENCE & AUTOMATED TRADING PLATFORM BluePrint`, `.ai/CURRENT_STATE.md`, `.ai/DECISIONS.md`, `.ai/TODO.md`, and relevant `docs/`. Inspect the existing implementation first, make the next logical production-quality change for my request, reuse existing architecture, test it, review the diff, update project state/docs, and report what changed, tests run, limitations, and next step. Follow all safety rules; PAPER remains the default and never enable live trading without my explicit approval.**

## Very Short Version

> **Continue Advance-System from the current repo state. Follow `AGENTS.md` + the master Blueprint + `.ai/*` + relevant docs. Inspect first, implement, test, document, and report. Do not bypass architecture, RiskEngine, OMS, or PAPER-first safety.**

## Useful Commands

### Continue
> Continue the next logical milestone.

### Build a feature
> Build this feature according to the project Blueprint and current architecture. Inspect first, implement, test, and update project state.

### Fix a bug
> Diagnose and fix this in Advance-System using the existing architecture. Reproduce the issue, make the smallest coherent fix, add a regression test, and verify it.

### Review
> Review the current implementation against `AGENTS.md`, the master Blueprint, and the relevant docs. Find correctness, architecture, data-quality, performance, security, and trading-safety issues. Fix only what is appropriate and test the changes.

### Next milestone
> Inspect the current project state and implement the next safe milestone from the roadmap. Do not ask me to repeat the requirements.
