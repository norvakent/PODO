from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import Field

from podo_schemas.base import IdentifiedModel, PodoModel
from podo_schemas.enums import Environment
from podo_schemas.trading import AccountRef, OrderRequest


class AssetForecast(PodoModel):
    symbol: str
    expected_return: Decimal
    volatility: Decimal = Field(ge=0)
    signal_score: Decimal | None = Field(default=None, ge=-1, le=1)


class PortfolioConstraint(PodoModel):
    symbol: str | None = None
    min_weight: Decimal = Field(default=Decimal("0"), ge=0, le=1)
    max_weight: Decimal = Field(default=Decimal("1"), ge=0, le=1)
    max_turnover: Decimal | None = Field(default=None, ge=0, le=1)


class OptimizationRequest(PodoModel):
    environment: Environment
    account: AccountRef
    strategy_id: UUID | None = None
    as_of: datetime
    assets: list[AssetForecast] = Field(min_length=1)
    covariance: list[list[Decimal]]
    current_weights: dict[str, Decimal] = Field(default_factory=dict)
    constraints: list[PortfolioConstraint] = Field(default_factory=list)
    objective: str = Field(default="mean_variance", max_length=64)


class TargetWeight(PodoModel):
    symbol: str
    weight: Decimal = Field(ge=0, le=1)
    expected_return: Decimal | None = None
    risk_contribution: Decimal | None = Field(default=None, ge=0)


class OptimizationResult(IdentifiedModel):
    request_id: UUID
    feasible: bool
    target_weights: list[TargetWeight]
    expected_return: Decimal | None = None
    expected_volatility: Decimal | None = Field(default=None, ge=0)
    expected_drawdown: Decimal | None = Field(default=None, ge=0)
    diagnostics: list[str] = Field(default_factory=list)
    generated_at: datetime


class RebalancePlan(IdentifiedModel):
    optimization_result_id: UUID
    account: AccountRef
    orders: list[OrderRequest]
    estimated_turnover: Decimal = Field(ge=0)
    estimated_cost: Decimal = Field(ge=0)
    generated_at: datetime
