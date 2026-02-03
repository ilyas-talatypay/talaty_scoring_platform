from datetime import date, datetime
from uuid import UUID

from pydantic import Field

from core.domain.v0.common import DomainBase
from core.domain.v0.enums import DatasetStatus


class Dataset(DomainBase):
    id: UUID
    name: str
    description: str | None = None
    storage_uri: str = Field(..., description="S3-compatible path to raw data.")
    schema_hash: str | None = None
    row_count: int | None = None
    date_start: date | None = None
    date_end: date | None = None
    target_definition: str | None = None
    status: DatasetStatus = DatasetStatus.DRAFT
    created_at: datetime | None = None
    updated_at: datetime | None = None


class DatasetVersion(DomainBase):
    id: UUID
    dataset_id: UUID
    version: str
    created_at: datetime | None = None
    created_by: str | None = None
    data_fingerprint: str = Field(..., description="Immutable data fingerprint/hash.")
    statistics_summary: dict | None = None

