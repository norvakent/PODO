from datetime import UTC, datetime
from decimal import Decimal
from typing import Annotated, Any, Generic, TypeVar
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

NonNegativeDecimal = Annotated[Decimal, Field(ge=0)]
PositiveDecimal = Annotated[Decimal, Field(gt=0)]

T = TypeVar("T")


class PodoModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        populate_by_name=True,
        str_strip_whitespace=True,
        use_enum_values=True,
    )


class IdentifiedModel(PodoModel):
    id: UUID = Field(default_factory=uuid4)


class TimestampedModel(PodoModel):
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime | None = None

    @field_validator("created_at", "updated_at")
    @classmethod
    def require_timezone(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return value
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("datetime must be timezone-aware")
        return value


class TraceContext(PodoModel):
    correlation_id: UUID = Field(default_factory=uuid4)
    causation_id: UUID | None = None
    request_id: str | None = Field(default=None, max_length=128)
    actor_id: UUID | None = None


class PageRequest(PodoModel):
    limit: int = Field(default=50, ge=1, le=500)
    cursor: str | None = None


class Page(PodoModel, Generic[T]):
    items: list[T]
    next_cursor: str | None = None
    total: int | None = Field(default=None, ge=0)


class Money(PodoModel):
    amount: Decimal
    currency: str = Field(min_length=3, max_length=10)


class Quantity(PodoModel):
    amount: Decimal
    unit: str = Field(min_length=1, max_length=32)


class ExternalRef(PodoModel):
    source: str = Field(min_length=1, max_length=64)
    id: str = Field(min_length=1, max_length=128)


class RawPayload(PodoModel):
    provider: str = Field(min_length=1, max_length=64)
    payload: dict[str, Any]
