from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from podo_schemas import (
    AccountRef,
    CcxtOhlcvCollector,
    Environment,
    KisOhlcvCollector,
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


def test_ccxt_ohlcv_collector_returns_common_candle(monkeypatch):
    class FakeExchange:
        def fetch_ohlcv(self, symbol, timeframe, since=None, limit=None):
            assert symbol == "BTC/USDT"
            assert timeframe == "1m"
            assert since == 1714521600000
            assert limit == 1
            return [[1714521600000, 60000.1, 61000.2, 59000.3, 60500.4, 12.5]]

    monkeypatch.setattr(
        CcxtOhlcvCollector,
        "_create_exchange",
        lambda self: FakeExchange(),
    )

    collector = CcxtOhlcvCollector(venue=Venue.BINANCE, exchange_id="binance")
    candles = collector.fetch_ohlcv(
        "BTC/USDT",
        "1m",
        since=datetime(2024, 5, 1, tzinfo=UTC),
        limit=1,
    )

    assert len(candles) == 1
    assert candles[0].venue == "binance"
    assert candles[0].open == Decimal("60000.1")
    assert candles[0].volume == Decimal("12.5")
    assert candles[0].raw.provider == "binance"


def test_kis_daily_rows_return_common_candle(monkeypatch):
    monkeypatch.setattr(
        KisOhlcvCollector,
        "_daily_chart",
        lambda self, symbol, start, end, interval: [
            {
                "stck_bsop_date": "20240502",
                "stck_oprc": "70000",
                "stck_hgpr": "72000",
                "stck_lwpr": "69000",
                "stck_clpr": "71000",
                "acml_vol": "123456",
                "acml_tr_pbmn": "8765432100",
            }
        ],
    )

    collector = KisOhlcvCollector(app_key="key", app_secret="secret")
    candles = collector.fetch_ohlcv(
        "005930",
        "1d",
        since=datetime(2024, 5, 1, tzinfo=UTC),
        limit=1,
    )

    assert len(candles) == 1
    assert candles[0].venue == "kis"
    assert candles[0].symbol == "005930"
    assert candles[0].close == Decimal("71000")
    assert candles[0].quote_volume == Decimal("8765432100")
    assert candles[0].raw.provider == "kis"
