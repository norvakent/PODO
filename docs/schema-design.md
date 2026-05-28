# PODO Common Schema Design

## Design Goals

- Normalize KIS, Upbit, and Binance data behind one domain vocabulary.
- Preserve financial precision with `Decimal`, never binary floats for money or quantity fields.
- Tag every runtime payload with `environment` so paper trading, backtesting, and live trading cannot be confused.
- Make auditability cheap: identifiers, timestamps, strategy/account/policy references, and correlation IDs are first-class.
- Keep AI and training contracts separate from execution contracts so after-hours workloads cannot leak into intraday order paths.

## Package

```text
packages/contracts/python/podo_schemas/src/podo_schemas/
├── base.py
├── enums.py
├── market.py
├── trading.py
├── portfolio.py
├── risk.py
├── ai.py
└── events.py
```

## Model Groups

`base.py` defines strict Pydantic configuration, ID aliases, timestamps, money/quantity helper aliases, and pagination envelopes.

`market.py` defines normalized instruments, ticks, candles, order books, and market snapshots.

`trading.py` defines accounts, orders, fills, positions, cash ledger entries, and paper-trading execution snapshots.

`portfolio.py` defines optimization inputs/outputs, target weights, rebalance plans, and risk contribution outputs.

`risk.py` defines policy limits, policy decisions, anomaly scores, anomaly incidents, and kill-switch requests.

`ai.py` defines Ollama inference, news/event scoring, training job reservations, model registry records, and promotion gates.

`events.py` defines event envelopes for queues, audit logs, and cross-service callbacks.

## Contract Rules

- Exchange-specific fields go into `raw` or adapter-private objects, not common models.
- Common models use ISO timestamps and timezone-aware `datetime`.
- External API models should serialize enums as strings and decimals as JSON-safe values.
- Commands and events are immutable records once accepted. State changes create new events or snapshots.
