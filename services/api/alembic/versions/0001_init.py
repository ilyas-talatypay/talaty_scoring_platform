"""initial metadata tables

Revision ID: 0001_init
Revises: None
Create Date: 2026-02-03
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    dataset_status = sa.Enum("draft", "ready", "deprecated", name="dataset_status")
    feature_dtype = sa.Enum("num", "cat", "bool", "date", "text", name="feature_dtype")
    feature_origin = sa.Enum("bureau", "bank_stmt", "doc", "derived", name="feature_origin")
    run_status = sa.Enum("queued", "running", "succeeded", "failed", name="run_status")
    model_registry_state = sa.Enum(
        "draft", "registered", "deprecated", name="model_registry_state"
    )

    bind = op.get_bind()
    dataset_status.create(bind, checkfirst=True)
    feature_dtype.create(bind, checkfirst=True)
    feature_origin.create(bind, checkfirst=True)
    run_status.create(bind, checkfirst=True)
    model_registry_state.create(bind, checkfirst=True)

    op.create_table(
        "datasets",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("storage_uri", sa.Text(), nullable=False),
        sa.Column("schema_hash", sa.String(length=128), nullable=True),
        sa.Column("row_count", sa.Integer(), nullable=True),
        sa.Column("date_start", sa.Date(), nullable=True),
        sa.Column("date_end", sa.Date(), nullable=True),
        sa.Column("target_definition", sa.Text(), nullable=True),
        sa.Column("status", dataset_status, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "dataset_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("dataset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("created_by", sa.String(length=255), nullable=True),
        sa.Column("data_fingerprint", sa.String(length=128), nullable=False),
        sa.Column("statistics_summary", postgresql.JSONB(), nullable=True),
        sa.ForeignKeyConstraint(["dataset_id"], ["datasets.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "features",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("dtype", feature_dtype, nullable=False),
        sa.Column("origin", feature_origin, nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("monotonic_expectation", sa.String(length=64), nullable=True),
        sa.Column("pii_flag", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "feature_sets",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "feature_set_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("feature_set_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("created_by", sa.String(length=255), nullable=True),
        sa.Column("features", postgresql.JSONB(), nullable=True),
        sa.Column("definition_query", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["feature_set_id"], ["feature_sets.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "run_specs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("dataset_version_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("feature_set_version_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("split_policy", postgresql.JSONB(), nullable=False),
        sa.Column("model_family", sa.String(length=128), nullable=False),
        sa.Column("model_params", postgresql.JSONB(), nullable=False),
        sa.Column("evaluation_policy", postgresql.JSONB(), nullable=False),
        sa.Column("artifact_policy", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("created_by", sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(["dataset_version_id"], ["dataset_versions.id"]),
        sa.ForeignKeyConstraint(["feature_set_version_id"], ["feature_set_versions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("run_spec_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", run_status, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("mlflow_run_id", sa.String(length=128), nullable=True),
        sa.Column("artifacts_uri", sa.Text(), nullable=True),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column("failure_trace_uri", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["run_spec_id"], ["run_specs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "models",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("produced_from_run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("registry_state", model_registry_state, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["produced_from_run_id"], ["runs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("models")
    op.drop_table("runs")
    op.drop_table("run_specs")
    op.drop_table("feature_set_versions")
    op.drop_table("feature_sets")
    op.drop_table("features")
    op.drop_table("dataset_versions")
    op.drop_table("datasets")

    bind = op.get_bind()
    sa.Enum("draft", "registered", "deprecated", name="model_registry_state").drop(
        bind, checkfirst=True
    )
    sa.Enum("queued", "running", "succeeded", "failed", name="run_status").drop(
        bind, checkfirst=True
    )
    sa.Enum("bureau", "bank_stmt", "doc", "derived", name="feature_origin").drop(
        bind, checkfirst=True
    )
    sa.Enum("num", "cat", "bool", "date", "text", name="feature_dtype").drop(
        bind, checkfirst=True
    )
    sa.Enum("draft", "ready", "deprecated", name="dataset_status").drop(
        bind, checkfirst=True
    )

