from enum import Enum


class DatasetStatus(str, Enum):
    DRAFT = "draft"
    READY = "ready"
    DEPRECATED = "deprecated"


class FeatureDType(str, Enum):
    NUM = "num"
    CAT = "cat"
    BOOL = "bool"
    DATE = "date"
    TEXT = "text"


class FeatureOrigin(str, Enum):
    BUREAU = "bureau"
    BANK_STMT = "bank_stmt"
    DOC = "doc"
    DERIVED = "derived"


class RunStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class ModelRegistryState(str, Enum):
    DRAFT = "draft"
    REGISTERED = "registered"
    DEPRECATED = "deprecated"

