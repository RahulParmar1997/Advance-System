# Risk Rules

## Execution hierarchy

Strategy
→ Risk Engine
→ OMS
→ Broker Adapter

Never:

Strategy → Broker

## Mandatory checks

- market status
- data freshness
- instrument validity
- duplicate signal
- position exposure
- sector exposure
- portfolio exposure
- daily loss
- strategy loss
- max concurrent positions
- max leverage
- margin
- slippage
- broker connectivity
- kill switch

## Default

EXECUTION_MODE=PAPER

Live execution requires explicit configuration.

## Kill switches

GLOBAL
STRATEGY
SYMBOL
BROKER
DATA
