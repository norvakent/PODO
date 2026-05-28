from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import Field

from podo_schemas.ai import TrainingJob
from podo_schemas.base import PodoModel, TraceContext
from podo_schemas.enums import Environment
from podo_schemas.risk import AnomalyIncident, PolicyCheckResult
from podo_schemas.trading import Fill, Order

EventPayload = Order | Fill | PolicyCheckResult | AnomalyIncident | TrainingJob


class EventEnvelope(PodoModel):
    event_id: UUID
    event_type: str = Field(min_length=1, max_length=128)
    environment: Environment
    occurred_at: datetime
    trace: TraceContext
    payload: EventPayload


class AuditLogEntry(PodoModel):
    action: str = Field(min_length=1, max_length=128)
    actor_id: UUID | None = None
    target_type: str = Field(min_length=1, max_length=64)
    target_id: UUID | str
    environment: Environment
    result: Literal["success", "failure"]
    message: str | None = None
    occurred_at: datetime
