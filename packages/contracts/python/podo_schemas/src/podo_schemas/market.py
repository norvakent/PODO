from datetime import datetime
from decimal import Decimal

from pydantic import Field

from podo_schemas.base import PodoModel, RawPayload
from podo_schemas.enums import AssetClass, Currency, Venue


class Instrument(PodoModel):
    venue: Venue
    symbol: str = Field(min_length=1, max_length=64)
    base_asset: str = Field(min_length=1, max_length=32)
    quote_asset: str = Field(min_length=1, max_length=32)
    asset_class: AssetClass
    price_precision: int = Field(ge=0, le=18)
    quantity_precision: int = Field(ge=0, le=18)
    min_order_quantity: Decimal | None = None
    min_notional: Decimal | None = None
    is_active: bool = True
    raw: RawPayload | None = None


class Ticker(PodoModel):
    venue: Venue
    symbol: str
    price: Decimal
    bid: Decimal | None = None
    ask: Decimal | None = None
    volume_24h: Decimal | None = None
    quote_volume_24h: Decimal | None = None
    event_time: datetime


class Candle(PodoModel):
    venue: Venue
    symbol: str
    interval: str = Field(pattern=r"^\d+[mhdwM]$")
    opened_at: datetime
    closed_at: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
    quote_volume: Decimal | None = None


class OrderBookLevel(PodoModel):
    price: Decimal
    quantity: Decimal


class OrderBook(PodoModel):
    venue: Venue
    symbol: str
    bids: list[OrderBookLevel]
    asks: list[OrderBookLevel]
    event_time: datetime


class MarketSnapshot(PodoModel):
    venue: Venue
    symbol: str
    currency: Currency
    ticker: Ticker | None = None
    order_book: OrderBook | None = None
    latest_candle: Candle | None = None
    captured_at: datetime
