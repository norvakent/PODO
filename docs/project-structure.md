# PODO Project Structure

## Target Monorepo Layout

```text
PODO/
├── apps/
│   ├── api-gateway/          # NestJS: operator API, order workflow, policy enforcement
│   ├── ai-service/           # FastAPI: AI, quant analytics, optimization, surveillance
│   └── web-console/          # React: operator console and chart quick-order UI
├── packages/
│   ├── contracts/
│   │   └── python/
│   │       └── podo_schemas/ # Pydantic shared DTOs for FastAPI and contract reference
│   ├── core/                 # auth, exchange router, scheduler, policy, audit
│   ├── data/                 # collectors, normalization, market/news/feature stores
│   ├── engine/               # strategy, execution, backtest, paper trading
│   └── management/           # portfolio, risk, anomaly surveillance, reporting
├── infra/
│   ├── docker/
│   ├── compose/
│   └── migrations/
├── docs/
└── scripts/
```

## Service Boundaries

`api-gateway` owns the trading control plane: operator auth, order submission, exchange adapter routing, policy enforcement, scheduling, audit writes, and websocket fan-out to the UI.

`ai-service` owns the analytics plane: Ollama-backed inference, model/training jobs, anomaly scoring, portfolio optimization, feature scoring, and reporting computations.

`web-console` owns operator workflows: chart inspection, quick order, policy preview, status monitoring, strategy management, and incident review.

`packages/contracts` is the neutral vocabulary layer. The Python package starts as the canonical model source for FastAPI. TypeScript DTOs and `.proto` files should either mirror these models or be generated from the same schema snapshots.

## Module Grouping

`core` should stay deterministic and safety-first. Anything capable of blocking order execution, changing exposure, or bypassing policy belongs here or behind explicit policy gates.

`data` normalizes raw market/news/community data into feature-ready representations. Raw venue quirks should stop at this boundary.

`engine` turns signals into proposed actions. It should emit intents and orders through normalized contracts rather than venue-specific payloads.

`management` owns portfolio allocation, risk budgets, anomaly incidents, reporting, and operator-facing governance.
