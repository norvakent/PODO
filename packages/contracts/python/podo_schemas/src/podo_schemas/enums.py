from enum import StrEnum


class Environment(StrEnum):
    LIVE = "live"
    PAPER = "paper"
    BACKTEST = "backtest"
    SANDBOX = "sandbox"


class Venue(StrEnum):
    KIS = "kis"
    UPBIT = "upbit"
    BINANCE = "binance"


class AssetClass(StrEnum):
    DOMESTIC_EQUITY = "domestic_equity"
    CRYPTO_SPOT = "crypto_spot"
    CRYPTO_FUTURES = "crypto_futures"
    CASH = "cash"


class Currency(StrEnum):
    KRW = "KRW"
    USD = "USD"
    USDT = "USDT"
    BTC = "BTC"
    ETH = "ETH"


class OrderSide(StrEnum):
    BUY = "buy"
    SELL = "sell"


class OrderType(StrEnum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class TimeInForce(StrEnum):
    DAY = "day"
    GTC = "gtc"
    IOC = "ioc"
    FOK = "fok"


class OrderStatus(StrEnum):
    DRAFT = "draft"
    PENDING_POLICY = "pending_policy"
    ACCEPTED = "accepted"
    ROUTED = "routed"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"


class LiquidityType(StrEnum):
    MAKER = "maker"
    TAKER = "taker"
    UNKNOWN = "unknown"


class PolicyDecision(StrEnum):
    ALLOW = "allow"
    WARN = "warn"
    BLOCK = "block"


class Severity(StrEnum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class JobStatus(StrEnum):
    QUEUED = "queued"
    RESERVED = "reserved"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ModelTask(StrEnum):
    SUMMARY = "summary"
    CLASSIFICATION = "classification"
    SENTIMENT = "sentiment"
    ANOMALY_SCORE = "anomaly_score"
    STRATEGY_SIGNAL = "strategy_signal"
