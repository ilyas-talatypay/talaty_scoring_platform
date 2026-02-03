from datetime import datetime
from uuid import UUID

from core.domain.v0.common import DomainBase
from core.domain.v0.enums import ModelRegistryState


class Model(DomainBase):
    id: UUID
    name: str
    produced_from_run_id: UUID
    registry_state: ModelRegistryState = ModelRegistryState.DRAFT
    created_at: datetime | None = None

