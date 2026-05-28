from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from podo_schemas import (
    AccountRef,
    Environment,
    OrderRequest,
    OrderSide,
    OrderType,
    TimeInForce,
    Venue,
)


def test_limit_order_request_validates():
    account = AccountRef(
        account_id=uuid4(),
        venue=Venue.UPBIT,
        environment=Environment.PAPER,
    )

    order = OrderRequest(
        account=account,
        symbol="KRW-BTC",
        side=OrderSide.BUY,
        type=OrderType.LIMIT,
        quantity=Decimal("0.01"),
        price=Decimal("100000000"),
        time_in_force=TimeInForce.DAY,
        client_order_id="paper-1",
    )

    dumped = order.model_dump(mode="json")
    assert dumped["account"]["environment"] == "paper"
    assert dumped["symbol"] == "KRW-BTC"


def test_timezone_aware_datetime_import_path():
    assert datetime.now(UTC).tzinfo is not None
