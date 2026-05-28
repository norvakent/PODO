from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import Field

from podo_schemas.base import IdentifiedModel, PodoModel
from podo_schemas.enums import Environment, PolicyDecision, Severity, Venue
from podo_schemas.trading import AccountRef, OrderRequest


class PolicyLimit(PodoModel):
    name: str = Field(min_length=1, max_length=64)
    max_order_notional: Decimal | None = Field(default=None, gt=0)
    max_daily_loss: Decimal | None = Field(default=None, gt=0)
    max_symbol_weight: Decimal | None = Field(default=None, ge=0, le=1)
    max_order_frequency_per_minute: int | None = Field(default=None, ge=1)
    allowed_venues: list[Venue] = Field(default_factory=list)


class PolicyCheckRequest(PodoModel):
    environment: Environment
    order: OrderRequest
    account_snapshot_at: datetime
    active_limits: list[PolicyLimit]


class PolicyCheckResult(PodoModel):
    decision: PolicyDecision
    violations: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    checked_at: datetime


class AnomalyScore(PodoModel):
    score: Decimal = Field(ge=0, le=1)
    severity: Severity
    reasons: list[str] = Field(default_factory=list)
    model_version: str | None = Field(default=None, max_length=128)
    scored_at: datetime


class AnomalyIncident(IdentifiedModel):
    environment: Environment
    account: AccountRef | None = None
    strategy_id: UUID | None = None
    venue: Venue | None = None
    symbol: str | None = None
    severity: Severity
    title: str = Field(min_length=1, max_length=160)
    description: str
    score: AnomalyScore | None = None
    opened_at: datetime
    closed_at: datetime | None = None


class KillSwitchRequest(PodoModel):
    environment: Environment
    scope: str = Field(pattern=r"^(venue|account|strategy|global)$")
    reason: str = Field(min_length=1, max_length=500)
    requested_by: UUID
    requested_at: datetime
