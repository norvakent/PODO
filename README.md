# PODO

PODO is a hybrid trading operations platform for market data collection, strategy validation, paper trading, controlled live execution, AI-assisted analytics, and portfolio/risk management.

The initial repository shape follows the planning documents in the `description/readme` branch:

- `apps/api-gateway`: NestJS operator API, exchange routing, order workflow, policy enforcement
- `apps/ai-service`: FastAPI analytics, AI inference, training orchestration, portfolio optimization
- `apps/web-console`: React operator console and chart-based quick order UI
- `packages/contracts`: shared API/data contracts across services
- `packages/core`: auth, exchange router, scheduler, policy engine, audit, observability
- `packages/data`: collectors, normalization, market store, news pipeline, feature store
- `packages/engine`: strategy engine, execution engine, backtester, paper trader
- `packages/management`: portfolio manager, risk manager, anomaly surveillance, reporting
- `infra`: Docker, compose, and database migration assets
- `docs`: architecture and implementation design documents

## Current Scaffold

The first concrete contract package is:

```text
packages/contracts/python/podo_schemas
```

It contains Pydantic v2 models for normalized market data, trading, portfolio, risk, AI/training, and event payloads. FastAPI can import these models directly, while NestJS DTOs and gRPC proto contracts can be generated or mirrored from the same domain vocabulary.

See [docs/project-structure.md](/Users/norvakent/dev/PODO/docs/project-structure.md) and [docs/schema-design.md](/Users/norvakent/dev/PODO/docs/schema-design.md).
