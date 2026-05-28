from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import Field, model_validator

from podo_schemas.base import IdentifiedModel, PodoModel, RawPayload, TimestampedModel
from podo_schemas.enums import (
    Currency,
    Environment,
    LiquidityType,
    OrderSide,
    OrderStatus,
    OrderType,
    TimeInForce,
    Venue,
)


class AccountRef(PodoModel):
    account_id: UUID
    venue: Venue
    environment: Environment


class OrderRequest(PodoModel):
    account: AccountRef
    symbol: str
    side: OrderSide
    type: OrderType
    quantity: Decimal = Field(gt=0)
    price: Decimal | None = Field(default=None, gt=0)
    stop_price: Decimal | None = Field(default=None, gt=0)
    time_in_force: TimeInForce = TimeInForce.DAY
    client_order_id: str = Field(min_length=1, max_length=128)
    strategy_id: UUID | None = None
    policy_set_id: UUID | None = None

    @model_validator(mode="after")
    def require_limit_price(self) -> "OrderRequest":
        if self.type in {OrderType.LIMIT, OrderType.STOP_LIMIT} and self.price is None:
            raise ValueError("limit orders require price")
        if self.type in {OrderType.STOP, OrderType.STOP_LIMIT} and self.stop_price is None:
            raise ValueError("stop orders require stop_price")
        return self


class Order(IdentifiedModel, TimestampedModel):
    request: OrderRequest
    status: OrderStatus
    venue_order_id: str | None = None
    accepted_at: datetime | None = None
    completed_at: datetime | None = None
    rejection_code: str | None = None
    rejection_reason: str | None = None
    raw: RawPayload | None = None


class Fill(IdentifiedModel):
    order_id: UUID
    venue: Venue
    symbol: str
    side: OrderSide
    executed_price: Decimal = Field(gt=0)
    executed_quantity: Decimal = Field(gt=0)
    fee: Decimal = Field(ge=0)
    fee_currency: Currency
    liquidity_type: LiquidityType = LiquidityType.UNKNOWN
    executed_at: datetime
    venue_fill_id: str | None = None


class Position(PodoModel):
    account: AccountRef
    symbol: str
    quantity: Decimal
    average_entry_price: Decimal | None = None
    mark_price: Decimal | None = None
    unrealized_pnl: Decimal | None = None
    realized_pnl: Decimal | None = None
    updated_at: datetime


class CashLedgerEntry(IdentifiedModel):
    account: AccountRef
    currency: Currency
    amount: Decimal
    balance_after: Decimal
    reason: str = Field(min_length=1, max_length=64)
    related_order_id: UUID | None = None
    related_fill_id: UUID | None = None
    booked_at: datetime


class PaperExecutionSnapshot(PodoModel):
    account: AccountRef
    order: Order
    fills: list[Fill]
    positions: list[Position]
    cash_ledger_entries: list[CashLedgerEntry]
    slippage_bps: Decimal = Field(ge=0)
    simulated_at: datetime
