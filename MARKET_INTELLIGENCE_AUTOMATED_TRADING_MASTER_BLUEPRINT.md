# MARKET INTELLIGENCE & AUTOMATED TRADING PLATFORM
# MASTER BLUEPRINT

## 1. Product Vision

Build a professional India-focused market intelligence and automated trading platform in which Market Intelligence is the primary product and Automated Trading is a controlled downstream consumer.

The platform continuously answers:

1. What is happening in the market?
2. Why is it happening?
3. Where is the opportunity?
4. Does the opportunity have positive expected value after costs?
5. Can it be traded within defined risk limits?

Core philosophy:

> Data → Intelligence → Opportunity → Validation → Risk → Execution → Learning

Automated trading must never bypass the Risk Engine or OMS.

Default execution mode is PAPER. Live execution is disabled until explicitly approved and production safety gates are satisfied.

---

## 2. Master System Workflow

```text
UPSTOX MARKET + BROKER APIs
            │
            ▼
      DATA INGESTION
            │
            ▼
       NORMALIZATION
            │
            ▼
       DATA QUALITY
            │
     ┌──────┼─────────┐
     ▼      ▼         ▼
   Redis ClickHouse Parquet/S3
     └──────┼─────────┘
            ▼
      CANDLE ENGINE
            │
            ▼
      FEATURE ENGINE
            │
   ┌────────┼────────────────────────────┐
   ▼        ▼            ▼               ▼
STRUCTURE LIQUIDITY    VOLUME         ORDER FLOW
   │        │            │               │
   └────────┼────────────┼───────────────┘
            ▼
       DERIVATIVES
            │
            ▼
          REGIME
            │
            ▼
   MARKET INTELLIGENCE
            │
            ▼
     MARKET SCANNER
            │
            ▼
      TRADE TYPE FILTER
            │
            ▼
     STRATEGY ENGINE
            │
            ▼
    OPPORTUNITY ENGINE
            │
            ▼
   PROBABILITY + EXPECTED VALUE
            │
            ▼
        RISK ENGINE
            │
       ┌────┴────┐
       │         │
    REJECT     APPROVE
                 │
                 ▼
                OMS
                 │
                 ▼
          PAPER EXECUTION
                 │
                 ▼
         POSITION MANAGER
                 │
                 ▼
              JOURNAL
                 │
                 ▼
            PATTERN DNA
                 │
                 ▼
          RESEARCH / ML
                 │
                 └──────► IMPROVED INTELLIGENCE
```

---

## 3. Product Modules

### Market Intelligence

- Dashboard
- Markets
- Equities
- Futures
- Options
- Indices
- Sectors
- Institutional / FII-DII
- Global Markets
- Breadth
- Heatmaps
- Regime
- Instrument Detail

### Automated Trading

- Market Scanner
- Trade Types
- Strategies
- Opportunity Engine
- Probability / EV
- Risk Engine
- OMS
- Paper Trading
- Position Manager
- Journal

### Research / Learning

- Backtesting
- Pattern DNA
- Historical Similarity
- Model Registry
- ML Probability Calibration
- Research Workspace

---

## 4. Data Acquisition

Primary broker/data gateway: Upstox.

Collect:

### Market
- LTP
- OHLC
- trades
- volume
- bid/ask
- depth
- timestamps
- market status

### Futures
- price
- volume
- OI
- OI change
- basis
- expiry
- rollover
- contango/backwardation

### Options
- option chain
- strike
- expiry
- CE/PE
- IV
- Greeks
- volume
- OI
- OI change
- bid/ask
- skew
- term structure

### Broker
- orders
- order status
- fills
- positions
- margin

Broker-specific formats remain inside adapters.

---

## 5. Canonical Data Model

Normalize external events into broker-independent contracts:

```text
QuoteEvent
TradeEvent
DepthEvent
CandleEvent
MarketStatusEvent
FutureSnapshot
OptionSnapshot
OrderEvent
FillEvent
PositionEvent
```

No intelligence, strategy, or risk component should depend directly on Upstox SDK response structures.

---

## 6. Data Quality

Every incoming event passes:

```text
timestamp valid?
      ↓
instrument valid?
      ↓
duplicate?
      ↓
out of order?
      ↓
gap/regression?
      ↓
stale?
      ↓
market session valid?
      ↓
DATA ACCEPTED
```

Quality states:

- HEALTHY
- DEGRADED
- STALE
- INVALID

Trading-critical consumers must reject unsafe stale/invalid data.

---

## 7. Storage Architecture

### Redis — hot state

- latest prices
- latest quotes/depth
- current candles
- option-chain state
- current regime
- active signals
- scanner state

### ClickHouse — market analytics

- ticks
- trades
- quotes
- depth
- candles
- futures
- options
- features
- structure events
- liquidity events
- profile data
- regimes
- signals
- scanner results

### PostgreSQL — application state

- users
- strategies
- strategy versions
- trade types
- risk profiles
- orders
- fills
- positions
- watchlists
- backtests
- models
- permissions
- audit records

### Parquet + S3/MinIO — research/archive

- raw events
- historical datasets
- order-book archives
- feature datasets
- ML datasets
- replay datasets

DuckDB may be used for local Parquet research.

---

## 8. Instrument Master

Maintain a broker-independent canonical instrument model.

Required fields include:

- instrument ID
- exchange
- segment
- symbol
- underlying
- instrument type
- expiry
- strike
- option type
- lot size
- tick size
- trading status
- broker mappings

Instrument master refresh must be versioned, validated, checksum-protected, freshness-checked, and atomically published.

---

## 9. Candle Engine

Transform normalized market events into deterministic time series:

```text
Ticks
 ↓
1s
 ↓
1m
 ↓
3m
 ↓
5m
 ↓
15m
 ↓
30m
 ↓
1H
 ↓
4H
 ↓
Daily
```

Handle:

- duplicates
- out-of-order events
- missing events
- session boundaries
- partial candles
- closed candles
- volume aggregation
- VWAP
- replay

Closed candles must be immutable after finalization.

---

## 10. Feature Engine

### Price

- returns
- ATR
- volatility
- momentum
- gap
- VWAP
- moving averages

### Volume

- RVOL
- volume anomaly
- volume acceleration
- turnover
- volume profile

### Structure

- swing highs/lows
- HH / HL / LH / LL
- BOS
- CHoCH
- MSS
- displacement
- compression
- expansion

### Liquidity

- equal highs/lows
- previous day high/low
- previous week high/low
- session high/low
- range liquidity
- liquidity sweeps

---

## 11. SMC / ICT / Wyckoff

Treat these as measurable hypotheses/lenses rather than guaranteed predictive truths.

### Liquidity sequence

```text
Liquidity Pool
      ↓
Sweep
      ↓
Reaction
      ↓
Displacement
      ↓
Structure Change
      ↓
Retest
```

### FVG features

- gap size / ATR
- displacement strength
- volume
- trend
- VWAP distance
- POC distance
- liquidity proximity
- time to fill
- partial/full fill
- reaction

### Order Block features

- liquidity event
- displacement
- volume anomaly
- structure break
- retest
- order-flow confirmation
- distance from value
- historical reaction

### Wyckoff

Quantify sequences such as:

- Spring
- Upthrust
- SOS
- SOW
- climax
- absorption
- test

---

## 12. Auction / Volume Profile

Calculate:

- POC
- VAH
- VAL
- HVN
- LVN
- initial balance
- opening range
- value migration
- acceptance
- rejection
- failed auction
- excess

Purpose: identify where the market accepts or rejects price.

---

## 13. Order Flow / Microstructure

Where data supports it, calculate:

- OFI
- CVD
- bid/ask imbalance
- microprice
- queue imbalance
- depth elasticity
- cancellation/replenishment
- Kyle lambda
- Amihud illiquidity
- price impact
- liquidity vacuum
- absorption
- exhaustion
- change-point
- entropy
- Hurst
- tail dependence

Do not manufacture order-flow information that is not supported by the underlying feed.

---

## 14. Futures Intelligence

For each underlying:

```text
Spot
 ↓
Near Future
 ↓
Next Future
 ↓
Far Future
```

Calculate:

- price change
- volume
- OI
- OI change
- basis
- premium/discount
- rollover
- contango/backwardation
- long buildup
- short buildup
- short covering
- long unwinding

---

## 15. Options Intelligence

Provide:

- full option chain
- ATM identification
- IV
- IV Rank
- IV Percentile
- expected move
- Greeks
- skew
- term structure
- call/put concentration
- unusual activity
- gamma exposure estimates

Dealer/gamma positioning must be labelled as model-derived estimates unless directly observable from authoritative data.

---

## 16. Breadth / Sector / Global Intelligence

### Breadth

- advance/decline
- up/down volume
- new highs/lows
- percentage above 20DMA
- percentage above 50DMA
- percentage above 200DMA
- F&O breadth
- momentum breadth
- divergences

### Sectors

- relative strength
- breadth
- momentum
- volume
- dispersion
- futures positioning
- options activity
- sector rotation

### Global

- US
- Europe
- Asia
- bonds/rates
- dollar
- commodities
- FX

---

## 17. Market Regime Engine

Supported regimes:

```text
TREND_UP
TREND_DOWN
RANGE
BREAKOUT
COMPRESSION
VOLATILITY_EXPANSION
VOLATILITY_CONTRACTION
PANIC
RECOVERY
MOMENTUM
MEAN_REVERSION
TRANSITION
HIGH_LIQUIDITY
LOW_LIQUIDITY
```

Start with transparent deterministic rules. Later add HMM/change-point models after sufficient validated data exists.

---

## 18. Market Intelligence Dashboard

The dashboard must answer:

1. What is the market doing?
2. Where are money, volume, OI and volatility moving?
3. Which sectors are strong/weak?
4. Which instruments show unusual activity?
5. Which qualified opportunities exist for the selected Trade Type?

Example layout:

```text
MARKET REGIME
NIFTY       TREND UP
BANKNIFTY   TREND UP
VOLATILITY  EXPANDING

BREADTH
ADV/DEC     1.8
UP VOLUME   68%
20DMA       72%
50DMA       61%

SECTORS
FINANCIALS  STRONG
IT          STRONG
ENERGY      NEUTRAL
FMCG        WEAK

DERIVATIVES
FUTURES OI  ↑
IV          EXPANDING

UNUSUAL ACTIVITY
10 instruments detected
```

---

## 19. Market Scanner

Broad Market Scanner asks:

> What is happening right now?

Automated Trading Scanner asks:

> Which setups satisfy the selected Trade Type and Strategy?

### Stage 1 — cheap filters

- price
- volume
- RVOL
- ATR
- liquidity
- spread

### Stage 2 — structure

- BOS
- CHoCH
- MSS
- FVG
- sweep
- VWAP
- profile

### Stage 3 — microstructure

- OFI
- CVD
- depth
- absorption
- liquidity

### Stage 4 — derivatives

- OI
- OI change
- IV
- skew
- futures basis
- options activity

### Stage 5 — quant ranking

- probability
- EV
- historical similarity
- regime compatibility
- execution quality
- risk

Scanner explanations must show both supporting evidence and meaningful negative evidence/penalties.

---

## 20. Scanner DSL

Scanner rules must compile into a typed AST, never arbitrary executable Python.

Support:

- AND
- OR
- NOT
- nested conditions
- thresholds
- multiple timeframes
- cross-asset conditions

Example:

```text
Daily Trend = Bullish
AND 1H BOS = True
AND 15M Liquidity Sweep = True
AND 5M Displacement = True
AND RVOL > 1.5
AND Price > VWAP
AND Sector Strength > 70
AND Futures OI increasing
```

---

## 21. Trade Type

Trade Type is a **selection/filter before automated trading**, not manual trading.

Supported examples:

- Scalping
- Intraday
- Breakout
- Momentum
- Trend Following
- Mean Reversion
- Reversal
- Range
- Swing
- Positional
- BTST
- Option Buying
- Option Selling
- Futures
- Custom

Trade Type defines:

- timeframe
- holding period
- allowed setups
- execution style
- stop logic
- target logic
- risk limits
- market session
- liquidity requirements

Conceptual separation:

```text
Trade Type = WHAT
Strategy   = HOW
Regime     = WHEN
Risk       = HOW MUCH
Execution  = HOW
```

---

## 22. Strategy Engine

Every strategy is versioned and reproducible.

```python
class Strategy:
    id: str
    version: str

    def required_features(self) -> set[str]:
        raise NotImplementedError

    def evaluate(self, state):
        raise NotImplementedError
```

Strategy evaluation must be deterministic, free of database/network calls, and protected against look-ahead bias.

---

## 23. Opportunity Engine

Canonical opportunity:

```text
Opportunity
├── instrument
├── direction
├── trade_type
├── strategy
├── regime
├── entry
├── stop
├── targets
├── structure_score
├── liquidity_score
├── volume_score
├── flow_score
├── derivatives_score
├── historical_score
├── execution_score
├── probability
├── expected_R
├── risk
└── explanation
```

Starting model weights:

```python
weights = {
    "structure": 0.18,
    "liquidity": 0.14,
    "volume": 0.10,
    "flow": 0.14,
    "derivatives": 0.10,
    "regime": 0.12,
    "historical": 0.10,
    "execution": 0.07,
    "risk": 0.05,
}
```

Weights are initial research parameters, not permanent truth. They must be validated out-of-sample.

---

## 24. Probability + Expected Value

For each qualified opportunity estimate:

```text
P(TP1)
P(TP2)
P(SL)
Expected R
Expected duration
```

Expected value:

```text
EV = Σ(probability × payoff) − transaction/execution costs
```

Costs must consider:

- brokerage
- STT
- exchange fees
- GST
- stamp duty
- spread
- slippage
- market impact
- latency

Probability models require time-aware validation and calibration using Brier score/reliability analysis.

---

## 25. Risk Engine

The Risk Engine is a mandatory hard gate between Strategy/Opportunity and OMS.

Checks:

- strategy valid
- strategy version enabled
- Trade Type enabled
- market open
- data fresh
- instrument valid
- duplicate signal/order
- current positions
- daily loss
- strategy loss
- symbol exposure
- sector exposure
- portfolio exposure
- concurrent trades
- margin
- leverage
- slippage
- broker health
- kill switch

Failed check → REJECT.

No AI or strategy may bypass this layer.

---

## 26. Position Sizing

Baseline:

```python
def position_size(account_equity, risk_fraction, entry, stop, point_value=1):
    risk_amount = account_equity * risk_fraction
    risk_per_unit = abs(entry - stop) * point_value
    if risk_per_unit <= 0:
        return 0
    return floor(risk_amount / risk_per_unit)
```

Production sizing additionally respects lot size, margin, liquidity, spread, volatility, capacity and portfolio exposure.

---

## 27. OMS

Order lifecycle:

```text
SCANNED
 ↓
CANDIDATE
 ↓
QUALIFIED
 ↓
RISK_CHECK
 ↓
ORDER_PENDING
 ↓
PARTIALLY_FILLED
 ↓
FILLED
 ↓
MANAGED
 ↓
SCALE_OUT
 ↓
EXIT
 ↓
CLOSED
```

Internal OMS is the application source of truth. Broker state is reconciled against OMS state.

Idempotency key:

```text
strategy_version:instrument_id:signal_timestamp:direction
```

Duplicate intent must return the existing intent rather than create another order.

---

## 28. Broker Adapter

```python
class BrokerAdapter:
    def place_order(self): ...
    def modify_order(self): ...
    def cancel_order(self): ...
    def get_order_status(self): ...
    def get_positions(self): ...
    def get_fills(self): ...
    def subscribe_order_updates(self): ...
```

Broker-specific logic remains isolated from the domain and strategy layers.

---

## 29. Paper Trading

Paper trading must use the same market data, strategy, risk and OMS path as eventual live execution.

```text
REAL MARKET DATA
      ↓
REAL FEATURES
      ↓
REAL STRATEGY
      ↓
REAL RISK ENGINE
      ↓
REAL OMS
      ↓
PAPER FILL MODEL
      ↓
POSITION
      ↓
P&L
```

Simulate:

- spread
- slippage
- latency
- partial fills
- rejects
- gaps
- fees
- liquidity

---

## 30. Position Manager

Responsibilities:

- stop management
- target management
- trailing logic
- scale-in/out
- exposure monitoring
- exit conditions
- broker reconciliation
- kill-switch response

Position Manager must operate through OMS controls.

---

## 31. Journal + Pattern DNA

Every trade becomes research data.

Store:

- entry market state
- feature vector
- strategy version
- signal reason
- risk decision
- execution quality
- MFE
- MAE
- R
- return
- duration
- outcome
- regime

Pattern DNA feature vector includes:

```text
trend
volatility
volume/RVOL
structure
liquidity
OFI/CVD
OI
IV/skew
breadth
sector
regime
time-of-day
```

Similarity workflow:

```text
CURRENT SETUP
      ↓
HISTORICAL SIMILAR CASES
      ↓
OUTCOME DISTRIBUTION
      ↓
PROBABILITY
      ↓
EXPECTED VALUE
```

---

## 32. Backtesting

Event-driven backtesting must mirror the production decision path:

```text
Historical Data
      ↓
Market State
      ↓
Features
      ↓
Strategy
      ↓
Risk
      ↓
Order Simulation
      ↓
Fill Model
      ↓
Position
      ↓
P&L
```

Validation:

- in-sample
- out-of-sample
- walk-forward
- parameter sensitivity
- Monte Carlo/trade randomization
- regime breakdown
- cost sensitivity
- capacity analysis

No look-ahead bias.

---

## 33. AI / ML Layer

AI sits above the quantitative engine.

### ML responsibilities

- setup classification
- outcome probability
- regime classification
- similarity
- ranking
- anomaly detection

### AI responsibilities

- explain market state
- explain opportunities
- generate scanner rules
- create research hypotheses
- analyze backtests
- summarize journal
- discover recurring patterns

AI may recommend or explain but cannot directly submit broker orders.

```text
AI
 ↓
RESEARCH / EXPLANATION
 ↓
QUANTIFIED SIGNAL
 ↓
RISK ENGINE
 ↓
OMS
```

Preferred initial ML stack:

- scikit-learn
- XGBoost / LightGBM / CatBoost

PyTorch later where justified by data and validation.

---

## 34. Frontend Blueprint

Primary navigation:

```text
Dashboard
Markets
Equities
Futures
Options
Indices
Sectors
Institutional
Global
Breadth
Heatmaps
Scanner
Opportunities
Trade Types
Strategies
Paper Trading
Positions
Orders
Journal
Pattern DNA
Backtesting
Research
Models
Settings
```

Recommended frontend stack:

- Next.js
- React
- TypeScript
- Tailwind
- shadcn/ui
- TanStack Query/Table
- Zustand
- React Hook Form + Zod
- ECharts/Recharts where appropriate
- Lightweight Charts as initial financial-chart foundation

Advanced charting can be introduced later subject to licensing/requirements.

---

## 35. Professional Chart Architecture

Chart layers:

```text
PRICE
VOLUME
VWAP
STRUCTURE
LIQUIDITY
SMC/ICT
VOLUME PROFILE
ORDER FLOW
DERIVATIVES
SIGNALS
EXECUTION
RESEARCH
```

Realtime path:

```text
Upstox WS
 ↓
Normalizer
 ↓
Tick State
 ↓
Candle Aggregator
 ↓
Feature Engine
 ↓
Chart Publisher
 ↓
Realtime Gateway
 ↓
Browser Store
 ↓
Chart Renderer
```

The chart is a consumer, not the source of truth.

User drawings are persisted separately from calculated market intelligence.

---

## 36. Security / Safety / Governance

Mandatory principles:

- PAPER by default
- secrets never committed
- broker credentials isolated
- audit every trading decision
- immutable strategy versions
- immutable closed-candle history
- idempotent order intents
- kill switch
- broker outage protection
- stale-data protection
- reconciliation
- explicit live-execution approval

Never implement:

```text
Strategy → Broker
AI → Broker
Scanner → Broker
Frontend → Broker
```

Correct path:

```text
Strategy
  ↓
Opportunity
  ↓
Risk Engine
  ↓
OMS
  ↓
Broker Adapter
```

---

## 37. Implementation Roadmap

### Phase 1 — Foundation

- repository architecture
- configuration
- domain contracts
- broker adapter boundary
- PostgreSQL/Redis/ClickHouse foundations
- PAPER-first safety

### Phase 2 — Market Data

- Upstox authentication/token handling
- instrument master
- V3 WebSocket
- protobuf decoding
- subscription management
- reconnect/resubscribe
- normalized events
- data-quality sequencing

### Phase 3 — Time-Series Engine

- candle engine
- VWAP
- volume aggregation
- session calendar
- deterministic replay
- ClickHouse market schemas

### Phase 4 — Market Intelligence

- price/structure
- liquidity
- SMC/ICT measurements
- volume profile
- order flow
- futures intelligence
- options intelligence
- breadth
- sectors
- institutional data
- global context
- regime engine

### Phase 5 — Scanner

- broad market scanner
- typed scanner DSL
- staged evaluation
- cross-asset conditions
- negative evidence

### Phase 6 — Automated Trading

- Trade Types
- strategy framework
- opportunity engine
- probability
- expected value
- risk engine
- position sizing
- OMS
- paper execution

### Phase 7 — Research

- journal
- Pattern DNA
- historical similarity
- event-driven backtester
- walk-forward validation
- Monte Carlo
- cost/capacity analysis

### Phase 8 — ML / AI

- probability calibration
- regime ML
- setup ranking
- anomaly detection
- research assistant
- market explanations

### Phase 9 — Production

- observability
- metrics
- tracing
- alerts
- broker reconciliation
- HA/disaster recovery
- operational controls
- carefully gated live execution

---

## 38. Definition of Done

A module is not complete merely because code exists.

Each milestone requires:

1. implementation
2. unit tests
3. integration tests where applicable
4. deterministic replay tests for trading-critical logic
5. failure-mode tests
6. documentation
7. architecture review
8. diff review
9. security/safety review
10. explicit statement of limitations

No claim of production readiness without evidence.

---

## 39. Final Operating Model

The platform should ultimately operate as one feedback loop:

```text
MARKET DATA
    ↓
MARKET STATE
    ↓
MARKET INTELLIGENCE
    ↓
REGIME
    ↓
SCANNER
    ↓
TRADE TYPE
    ↓
STRATEGY
    ↓
OPPORTUNITY
    ↓
PROBABILITY
    ↓
EXPECTED VALUE
    ↓
RISK
    ↓
OMS
    ↓
EXECUTION
    ↓
POSITION
    ↓
OUTCOME
    ↓
JOURNAL
    ↓
PATTERN DNA
    ↓
RESEARCH / ML
    ↓
IMPROVED INTELLIGENCE
```

## Core Principle

> **Do not build an indicator-to-order system. Build a market-understanding system whose automated trading capability is a controlled, measurable, risk-gated consumer of that intelligence.**
