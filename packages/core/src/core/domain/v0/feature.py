from datetime import datetime
from uuid import UUID

from core.domain.v0.common import DomainBase
from core.domain.v0.enums import FeatureDType, FeatureOrigin


class Feature(DomainBase):
    id: UUID
    name: str
    dtype: FeatureDType
    origin: FeatureOrigin
    description: str | None = None
    monotonic_expectation: str | None = None
    pii_flag: bool | None = None
    created_at: datetime | None = None


class FeatureSet(DomainBase):
    id: UUID
    name: str
    description: str | None = None
    created_at: datetime | None = None


class FeatureSetVersion(DomainBase):
    id: UUID
    feature_set_id: UUID
    version: str
    created_at: datetime | None = None
    created_by: str | None = None
    features: list[str] | None = None
    definition_query: str | None = None

