from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from core.domain.v0.enums import DatasetStatus, FeatureDType, FeatureOrigin


class APIBase(BaseModel):
    model_config = ConfigDict(extra="forbid")


class DatasetCreate(APIBase):
    name: str
    description: str | None = None
    storage_uri: str
    schema_hash: str | None = None
    row_count: int | None = None
    date_start: date | None = None
    date_end: date | None = None
    target_definition: str | None = None
    status: DatasetStatus = DatasetStatus.DRAFT


class DatasetVersionCreate(APIBase):
    version: str
    created_by: str | None = None
    data_fingerprint: str
    statistics_summary: dict | None = None


class FeatureCreate(APIBase):
    name: str
    dtype: FeatureDType
    origin: FeatureOrigin
    description: str | None = None
    monotonic_expectation: str | None = None
    pii_flag: bool | None = None


class FeatureSetCreate(APIBase):
    name: str
    description: str | None = None


class FeatureSetVersionCreate(APIBase):
    version: str
    created_by: str | None = None
    features: list[str] | None = None
    definition_query: str | None = None


class RunSpecCreate(APIBase):
    dataset_version_id: UUID
    feature_set_version_id: UUID
    split_policy: dict = Field(default_factory=dict)
    model_family: str
    model_params: dict = Field(default_factory=dict)
    evaluation_policy: dict = Field(default_factory=dict)
    artifact_policy: dict = Field(default_factory=dict)
    created_by: str | None = None


class RunCreate(APIBase):
    run_spec_id: UUID


class RunExecuteRequest(APIBase):
    run_spec_id: UUID

