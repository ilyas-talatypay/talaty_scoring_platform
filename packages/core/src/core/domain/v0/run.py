from datetime import datetime
from uuid import UUID

from pydantic import Field

from core.domain.v0.common import DomainBase
from core.domain.v0.enums import RunStatus


class RunSpec(DomainBase):
    id: UUID | None = None
    dataset_version_id: UUID
    feature_set_version_id: UUID
    split_policy: dict = Field(default_factory=dict)
    model_family: str
    model_params: dict = Field(default_factory=dict)
    evaluation_policy: dict = Field(default_factory=dict)
    artifact_policy: dict = Field(default_factory=dict)
    created_at: datetime | None = None
    created_by: str | None = None


class Run(DomainBase):
    id: UUID
    run_spec_id: UUID
    status: RunStatus = RunStatus.QUEUED
    created_at: datetime | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    mlflow_run_id: str | None = None
    artifacts_uri: str | None = None
    failure_reason: str | None = None
    failure_trace_uri: str | None = None

