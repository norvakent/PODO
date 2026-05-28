from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import Field

from podo_schemas.base import IdentifiedModel, PodoModel
from podo_schemas.enums import Environment, JobStatus, ModelTask


class InferenceRequest(PodoModel):
    task: ModelTask
    model: str = Field(min_length=1, max_length=128)
    prompt: str = Field(min_length=1)
    context: dict[str, str | int | float | bool] = Field(default_factory=dict)
    max_tokens: int | None = Field(default=None, ge=1)
    temperature: Decimal | None = Field(default=None, ge=0, le=2)


class InferenceResult(PodoModel):
    task: ModelTask
    model: str
    output: str
    confidence: Decimal | None = Field(default=None, ge=0, le=1)
    latency_ms: int = Field(ge=0)
    generated_at: datetime


class MarketTextSignal(PodoModel):
    source: str = Field(min_length=1, max_length=64)
    symbol: str | None = None
    headline: str | None = None
    summary: str
    sentiment_score: Decimal | None = Field(default=None, ge=-1, le=1)
    event_labels: list[str] = Field(default_factory=list)
    model_version: str
    observed_at: datetime


class TrainingReservation(IdentifiedModel):
    environment: Environment
    dataset_version: str = Field(min_length=1, max_length=128)
    model_recipe: str = Field(min_length=1, max_length=128)
    not_before: datetime
    not_after: datetime
    cpu_cores: Decimal | None = Field(default=None, gt=0)
    gpu_required: bool = False
    memory_gb: Decimal | None = Field(default=None, gt=0)
    priority: int = Field(default=100, ge=0, le=1000)


class TrainingJob(IdentifiedModel):
    reservation_id: UUID
    status: JobStatus
    started_at: datetime | None = None
    finished_at: datetime | None = None
    metrics: dict[str, Decimal] = Field(default_factory=dict)
    artifact_uri: str | None = None
    error_message: str | None = None


class ModelRegistryRecord(IdentifiedModel):
    model_name: str = Field(min_length=1, max_length=128)
    version: str = Field(min_length=1, max_length=128)
    task: ModelTask
    artifact_uri: str
    promoted: bool = False
    latency_p95_ms: int | None = Field(default=None, ge=0)
    quality_score: Decimal | None = Field(default=None, ge=0, le=1)
    drift_score: Decimal | None = Field(default=None, ge=0, le=1)
    registered_at: datetime
