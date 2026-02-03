import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, MetaData, String, Table, select, update
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.engine import Connection

from core.domain.v0.enums import RunStatus


metadata = MetaData()

dataset_versions = Table(
    "dataset_versions",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("dataset_id", UUID(as_uuid=True), nullable=False),
    Column("version", String(length=64), nullable=False),
    Column("created_at", DateTime, nullable=False),
)

feature_set_versions = Table(
    "feature_set_versions",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("feature_set_id", UUID(as_uuid=True), nullable=False),
    Column("version", String(length=64), nullable=False),
    Column("created_at", DateTime, nullable=False),
)

run_specs = Table(
    "run_specs",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("dataset_version_id", UUID(as_uuid=True), nullable=False),
    Column("feature_set_version_id", UUID(as_uuid=True), nullable=False),
    Column("split_policy", JSONB, nullable=False),
    Column("model_family", String(length=128), nullable=False),
    Column("model_params", JSONB, nullable=False),
    Column("evaluation_policy", JSONB, nullable=False),
    Column("artifact_policy", JSONB, nullable=False),
    Column("created_at", DateTime, nullable=False),
    Column("created_by", String(length=255), nullable=True),
)

runs = Table(
    "runs",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("run_spec_id", UUID(as_uuid=True), nullable=False),
    Column("status", Enum(RunStatus, name="run_status"), nullable=False),
    Column("created_at", DateTime, nullable=False),
    Column("started_at", DateTime, nullable=True),
    Column("finished_at", DateTime, nullable=True),
    Column("mlflow_run_id", String(length=128), nullable=True),
    Column("artifacts_uri", String(length=512), nullable=True),
    Column("failure_reason", String(length=2048), nullable=True),
    Column("failure_trace_uri", String(length=512), nullable=True),
)


def dataset_version_exists(conn: Connection, dataset_version_id: uuid.UUID) -> bool:
    result = conn.execute(
        select(dataset_versions.c.id).where(dataset_versions.c.id == dataset_version_id)
    ).first()
    return result is not None


def feature_set_version_exists(conn: Connection, feature_set_version_id: uuid.UUID) -> bool:
    result = conn.execute(
        select(feature_set_versions.c.id).where(
            feature_set_versions.c.id == feature_set_version_id
        )
    ).first()
    return result is not None


def fetch_run_spec(conn: Connection, run_spec_id: uuid.UUID) -> dict | None:
    result = conn.execute(select(run_specs).where(run_specs.c.id == run_spec_id)).mappings().first()
    return dict(result) if result else None


def insert_run_spec(conn: Connection, payload: dict) -> uuid.UUID:
    run_spec_id = payload.get("id") or uuid.uuid4()
    created_at = payload.get("created_at") or datetime.utcnow()
    conn.execute(
        run_specs.insert().values(
            id=run_spec_id,
            dataset_version_id=payload["dataset_version_id"],
            feature_set_version_id=payload["feature_set_version_id"],
            split_policy=payload.get("split_policy", {}),
            model_family=payload["model_family"],
            model_params=payload.get("model_params", {}),
            evaluation_policy=payload.get("evaluation_policy", {}),
            artifact_policy=payload.get("artifact_policy", {}),
            created_at=created_at,
            created_by=payload.get("created_by"),
        )
    )
    return run_spec_id


def create_run(conn: Connection, run_spec_id: uuid.UUID, status: RunStatus) -> uuid.UUID:
    run_id = uuid.uuid4()
    conn.execute(
        runs.insert().values(
            id=run_id,
            run_spec_id=run_spec_id,
            status=status,
            created_at=datetime.utcnow(),
        )
    )
    return run_id


def update_run_status(
    conn: Connection,
    run_id: uuid.UUID,
    status: RunStatus,
    started_at: datetime | None = None,
    finished_at: datetime | None = None,
    artifacts_uri: str | None = None,
    mlflow_run_id: str | None = None,
    failure_reason: str | None = None,
    failure_trace_uri: str | None = None,
) -> None:
    values: dict = {"status": status}
    if started_at is not None:
        values["started_at"] = started_at
    if finished_at is not None:
        values["finished_at"] = finished_at
    if artifacts_uri is not None:
        values["artifacts_uri"] = artifacts_uri
    if mlflow_run_id is not None:
        values["mlflow_run_id"] = mlflow_run_id
    if failure_reason is not None:
        values["failure_reason"] = failure_reason
    if failure_trace_uri is not None:
        values["failure_trace_uri"] = failure_trace_uri
    conn.execute(update(runs).where(runs.c.id == run_id).values(**values))

