from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from typing import Any, Protocol
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from podo_schemas.base import RawPayload
from podo_schemas.enums import Venue
from podo_schemas.market import Candle

CcxtOhlcvRow = Sequence[int | float | str | None]

_TIMEFRAME_SECONDS: Mapping[str, int] = {
    "1m": 60,
    "3m": 180,
    "5m": 300,
    "10m": 600,
    "15m": 900,
    "30m": 1800,
    "1h": 3600,
    "4h": 14400,
    "1d": 86400,
    "1w": 604800,
    "1M": 2592000,
}


class OhlcvCollector(Protocol):
    def fetch_ohlcv(
        self,
        symbol: str,
        interval: str = "1d",
        *,
        since: datetime | None = None,
        limit: int = 100,
    ) -> list[Candle]:
        """Return normalized OHLCV candles."""


@dataclass(frozen=True)
class CcxtOhlcvCollector:
    venue: Venue
    exchange_id: str
    exchange_options: Mapping[str, Any] | None = None

    def fetch_ohlcv(
        self,
        symbol: str,
        interval: str = "1d",
        *,
        since: datetime | None = None,
        limit: int = 100,
    ) -> list[Candle]:
        exchange = self._create_exchange()
        rows = exchange.fetch_ohlcv(
            symbol,
            timeframe=interval,
            since=_to_millis(since) if since else None,
            limit=limit,
        )
        return [
            _candle_from_ccxt_row(
                venue=self.venue,
                symbol=symbol,
                interval=interval,
                row=row,
                provider=self.exchange_id,
            )
            for row in rows
        ]

    def _create_exchange(self) -> Any:
        try:
            import ccxt
        except ImportError as exc:
            raise RuntimeError("ccxt is required to use CcxtOhlcvCollector") from exc

        exchange_cls = getattr(ccxt, self.exchange_id)
        return exchange_cls(dict(self.exchange_options or {}))


@dataclass(frozen=True)
class KisOhlcvCollector:
    app_key: str
    app_secret: str
    base_url: str = "https://openapi.koreainvestment.com:9443"
    adjusted: bool = True
    market_division_code: str = "J"
    access_token: str | None = None

    def fetch_ohlcv(
        self,
        symbol: str,
        interval: str = "1d",
        *,
        since: datetime | None = None,
        limit: int = 100,
    ) -> list[Candle]:
        if interval not in {"1d", "1w", "1M"}:
            raise ValueError("KIS OHLCV collector supports 1d, 1w, and 1M intervals")

        today = datetime.now(UTC).date()
        start = (since.date() if since else today - timedelta(days=max(limit * 2, 30)))
        rows = self._daily_chart(symbol=symbol, start=start, end=today, interval=interval)
        candles = [
            self._candle_from_kis_daily_row(symbol=symbol, interval=interval, row=row)
            for row in rows
        ]
        return sorted(candles, key=lambda item: item.opened_at)[-limit:]

    def _daily_chart(
        self,
        *,
        symbol: str,
        start: date,
        end: date,
        interval: str,
    ) -> list[dict[str, Any]]:
        period = {"1d": "D", "1w": "W", "1M": "M"}[interval]
        payload = self._request_json(
            method="GET",
            path="/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice",
            tr_id="FHKST03010100",
            query={
                "FID_COND_MRKT_DIV_CODE": self.market_division_code,
                "FID_INPUT_ISCD": symbol,
                "FID_INPUT_DATE_1": start.strftime("%Y%m%d"),
                "FID_INPUT_DATE_2": end.strftime("%Y%m%d"),
                "FID_PERIOD_DIV_CODE": period,
                "FID_ORG_ADJ_PRC": "0" if self.adjusted else "1",
            },
        )
        output = payload.get("output2", [])
        if not isinstance(output, list):
            raise RuntimeError("KIS daily chart response did not include output2 rows")
        return [row for row in output if isinstance(row, dict)]

    def _candle_from_kis_daily_row(
        self,
        *,
        symbol: str,
        interval: str,
        row: Mapping[str, Any],
    ) -> Candle:
        opened_at = datetime.strptime(str(row["stck_bsop_date"]), "%Y%m%d").replace(
            tzinfo=UTC
        )
        return Candle(
            venue=Venue.KIS,
            symbol=symbol,
            interval=interval,
            opened_at=opened_at,
            closed_at=opened_at + _interval_delta(interval),
            open=_decimal(row["stck_oprc"]),
            high=_decimal(row["stck_hgpr"]),
            low=_decimal(row["stck_lwpr"]),
            close=_decimal(row["stck_clpr"]),
            volume=_decimal(row.get("acml_vol", "0")),
            quote_volume=_decimal(row["acml_tr_pbmn"])
            if row.get("acml_tr_pbmn") is not None
            else None,
            raw=RawPayload(provider="kis", payload=dict(row)),
        )

    def _request_json(
        self,
        *,
        method: str,
        path: str,
        tr_id: str | None = None,
        query: Mapping[str, str] | None = None,
        body: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        if query:
            url = f"{url}?{urlencode(query)}"

        data = json.dumps(body).encode() if body else None
        headers = {
            "content-type": "application/json; charset=utf-8",
            "authorization": f"Bearer {self.access_token or self._issue_access_token()}",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
        }
        if tr_id:
            headers["tr_id"] = tr_id

        request = Request(url, data=data, headers=headers, method=method)
        try:
            with urlopen(request, timeout=10) as response:
                return json.loads(response.read().decode())
        except HTTPError as exc:
            detail = exc.read().decode(errors="replace")
            raise RuntimeError(f"KIS request failed: {exc.code} {detail}") from exc

    def _issue_access_token(self) -> str:
        url = f"{self.base_url}/oauth2/tokenP"
        body = json.dumps(
            {
                "grant_type": "client_credentials",
                "appkey": self.app_key,
                "appsecret": self.app_secret,
            }
        ).encode()
        request = Request(
            url,
            data=body,
            headers={"content-type": "application/json; charset=utf-8"},
            method="POST",
        )
        with urlopen(request, timeout=10) as response:
            payload = json.loads(response.read().decode())
        token = payload.get("access_token")
        if not isinstance(token, str) or not token:
            raise RuntimeError("KIS token response did not include access_token")
        return token


def create_ohlcv_collector(
    venue: Venue | str,
    *,
    exchange_options: Mapping[str, Any] | None = None,
    kis_app_key: str | None = None,
    kis_app_secret: str | None = None,
    kis_access_token: str | None = None,
    kis_base_url: str = "https://openapi.koreainvestment.com:9443",
) -> OhlcvCollector:
    normalized_venue = Venue(venue)
    if normalized_venue == Venue.UPBIT:
        return CcxtOhlcvCollector(
            venue=Venue.UPBIT,
            exchange_id="upbit",
            exchange_options=exchange_options,
        )
    if normalized_venue == Venue.BINANCE:
        return CcxtOhlcvCollector(
            venue=Venue.BINANCE,
            exchange_id="binance",
            exchange_options=exchange_options,
        )
    if normalized_venue == Venue.KIS:
        if not kis_app_key or not kis_app_secret:
            raise ValueError("kis_app_key and kis_app_secret are required for KIS")
        return KisOhlcvCollector(
            app_key=kis_app_key,
            app_secret=kis_app_secret,
            base_url=kis_base_url,
            access_token=kis_access_token,
        )
    raise ValueError(f"unsupported venue: {venue}")


def fetch_ohlcv(
    venue: Venue | str,
    symbol: str,
    interval: str = "1d",
    *,
    since: datetime | None = None,
    limit: int = 100,
    **collector_options: Any,
) -> list[Candle]:
    collector = create_ohlcv_collector(venue, **collector_options)
    return collector.fetch_ohlcv(symbol, interval, since=since, limit=limit)


def _candle_from_ccxt_row(
    *,
    venue: Venue,
    symbol: str,
    interval: str,
    row: CcxtOhlcvRow,
    provider: str,
) -> Candle:
    if len(row) < 6:
        raise ValueError(
            "ccxt OHLCV rows must contain timestamp, open, high, low, close, volume"
        )
    opened_at = datetime.fromtimestamp(int(row[0]) / 1000, tz=UTC)
    return Candle(
        venue=venue,
        symbol=symbol,
        interval=interval,
        opened_at=opened_at,
        closed_at=opened_at + _interval_delta(interval),
        open=_decimal(row[1]),
        high=_decimal(row[2]),
        low=_decimal(row[3]),
        close=_decimal(row[4]),
        volume=_decimal(row[5]),
        raw=RawPayload(provider=provider, payload={"ohlcv": list(row)}),
    )


def _interval_delta(interval: str) -> timedelta:
    if interval not in _TIMEFRAME_SECONDS:
        raise ValueError(f"unsupported interval: {interval}")
    return timedelta(seconds=_TIMEFRAME_SECONDS[interval])


def _to_millis(value: datetime) -> int:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("since must be timezone-aware")
    return int(value.timestamp() * 1000)


def _decimal(value: int | float | str | None) -> Decimal:
    if value is None:
        return Decimal("0")
    return Decimal(str(value))
