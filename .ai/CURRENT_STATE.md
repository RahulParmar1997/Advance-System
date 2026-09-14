# Current Project State

Updated: 2026-09-14

## Current phase

Phase 1 — Foundation

## Working

- FastAPI API
- Next.js frontend
- Docker PostgreSQL
- Redis
- ClickHouse
- Basic chart
- Risk engine skeleton
- OMS skeleton

## Currently implementing

Upstox V3 market data ingestion.

## Next

1. Upstox authentication
2. Instrument master
3. WebSocket protobuf decoder
4. Market event normalizer
5. ClickHouse candle storage
6. Realtime chart updates

## Not implemented

- Live trading
- Production OMS reconciliation
- Options analytics
- Full order flow
- ML probability
- Production backtester

## Important decisions

- Modular monolith + workers
- Upstox behind adapter
- ClickHouse for market analytics
- PostgreSQL for application state
- Redis for realtime state
- Lightweight Charts for initial charting

## Current known issues

- WebSocket reconnect not production ready
- Broker reconciliation incomplete
- Chart currently uses demo candles
