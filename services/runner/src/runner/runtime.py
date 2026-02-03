import json
import os
import traceback
from datetime import datetime
from pathlib import Path
from uuid import UUID

import mlflow
import yaml
from sqlalchemy import create_engine

from core.domain.v0 import RunSpec
from core.domain.v0.enums import RunStatus
from core.storage import S3CompatibleStore, run_prefix
from runner.config import RunnerSettings
from runner.db import (
    create_run,
    dataset_version_exists,
    feature_set_version_exists,
    fetch_run_spec,
    insert_run_spec,
    update_run_status,
)


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def _upload_text(store: S3CompatibleStore, key: str, content: str, content_type: str) -> None:
    store.put_bytes(key, content.encode("utf-8"), content_type)


def _log_params(run_spec: RunSpec, settings: RunnerSettings) -> None:
    payload = run_spec.model_dump()
    for key, value in payload.items():
        if value is None:
            continue
        if isinstance(value, (dict, list)):
            mlflow.log_param(key, json.dumps(value))
        else:
            mlflow.log_param(key, str(value))
    if settings.GIT_SHA:
        mlflow.log_param("git_sha", settings.GIT_SHA)
    if settings.IMAGE_TAG:
        mlflow.log_param("image_tag", settings.IMAGE_TAG)


def get_run_spec_by_id(settings: RunnerSettings, run_spec_id: UUID) -> RunSpec | None:
    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
    with engine.begin() as conn:
        payload = fetch_run_spec(conn, run_spec_id)
        return RunSpec.model_validate(payload) if payload else None


def execute_run_spec(
    settings: RunnerSettings,
    store: S3CompatibleStore,
    run_spec: RunSpec,
) -> tuple[UUID, datetime, RunStatus]:
    log_lines: list[str] = []

    def log(message: str) -> None:
        timestamp = datetime.utcnow().isoformat()
        log_lines.append(f"{timestamp} {message}")

    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
    run_id: UUID | None = None
    run_spec_id: UUID | None = None
    artifacts_uri: str | None = None
    workdir: Path | None = None
    started_at = datetime.utcnow()
    mlflow_run_id: str | None = None
    mlflow_active = False

    try:
        with engine.begin() as conn:
            if not dataset_version_exists(conn, run_spec.dataset_version_id):
                raise ValueError("Dataset version not found")
            if not feature_set_version_exists(conn, run_spec.feature_set_version_id):
                raise ValueError("Feature set version not found")

            if run_spec.id:
                existing = fetch_run_spec(conn, run_spec.id)
                if existing:
                    run_spec_id = run_spec.id
                else:
                    run_spec_id = insert_run_spec(conn, run_spec.model_dump())
            else:
                run_spec_id = insert_run_spec(conn, run_spec.model_dump())

            run_id = create_run(conn, run_spec_id, RunStatus.QUEUED)
            artifacts_uri = f"s3://{store.bucket}/{run_prefix(str(run_id))}"

            if settings.MLFLOW_TRACKING_URI:
                mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
            if settings.MLFLOW_S3_ENDPOINT_URL:
                os.environ.setdefault("MLFLOW_S3_ENDPOINT_URL", settings.MLFLOW_S3_ENDPOINT_URL)

            mlflow_run = mlflow.start_run(run_name=str(run_id))
            mlflow_run_id = mlflow_run.info.run_id
            mlflow_active = True
            _log_params(run_spec, settings)
            update_run_status(
                conn,
                run_id,
                RunStatus.RUNNING,
                started_at=started_at,
                artifacts_uri=artifacts_uri,
                mlflow_run_id=mlflow_run_id,
            )

        workdir = Path(settings.RUN_WORKDIR) / str(run_id)
        workdir.mkdir(parents=True, exist_ok=True)

        log(f"Run created with id {run_id}")
        log("Writing artifacts to object store")

        runspec_key = f"{run_prefix(str(run_id))}runspec.yaml"
        runspec_text = yaml.safe_dump(run_spec.model_dump(), sort_keys=False)
        _write_text(workdir / "runspec.yaml", runspec_text)
        _upload_text(store, runspec_key, runspec_text, "application/x-yaml")
        if mlflow_active:
            mlflow.log_artifact(str(workdir / "runspec.yaml"))

        meta = {
            "run_id": str(run_id),
            "run_spec_id": str(run_spec_id),
            "created_at": datetime.utcnow().isoformat(),
            "git_sha": settings.GIT_SHA,
            "image_tag": settings.IMAGE_TAG,
        }
        meta_key = f"{run_prefix(str(run_id))}meta.json"
        meta_text = json.dumps(meta, indent=2)
        _write_text(workdir / "meta.json", meta_text)
        _upload_text(store, meta_key, meta_text, "application/json")
        if mlflow_active:
            mlflow.log_artifact(str(workdir / "meta.json"))

        with engine.begin() as conn:
            update_run_status(
                conn,
                run_id,
                RunStatus.SUCCEEDED,
                finished_at=datetime.utcnow(),
                artifacts_uri=artifacts_uri,
            )

        log("Run succeeded")
        log_key = f"{run_prefix(str(run_id))}logs/runner.log"
        log_text = "\n".join(log_lines) + "\n"
        _write_text(workdir / "logs" / "runner.log", log_text)
        _upload_text(store, log_key, log_text, "text/plain")
        if mlflow_active:
            mlflow.log_artifact(str(workdir / "logs" / "runner.log"))
            mlflow.end_run(status="FINISHED")
        return run_id, started_at, RunStatus.SUCCEEDED
    except Exception as exc:  # noqa: BLE001
        log(f"Run failed: {exc}")
        trace = traceback.format_exc()

        if run_id and workdir:
            trace_key = f"{run_prefix(str(run_id))}logs/stacktrace.txt"
            _write_text(workdir / "logs" / "stacktrace.txt", trace)
            _upload_text(store, trace_key, trace, "text/plain")
            log_key = f"{run_prefix(str(run_id))}logs/runner.log"
            log_text = "\n".join(log_lines) + "\n"
            _write_text(workdir / "logs" / "runner.log", log_text)
            _upload_text(store, log_key, log_text, "text/plain")
            if mlflow_active:
                mlflow.log_artifact(str(workdir / "logs" / "stacktrace.txt"))
                mlflow.log_artifact(str(workdir / "logs" / "runner.log"))
            with engine.begin() as conn:
                update_run_status(
                    conn,
                    run_id,
                    RunStatus.FAILED,
                    finished_at=datetime.utcnow(),
                    artifacts_uri=artifacts_uri,
                    mlflow_run_id=mlflow_run_id,
                    failure_reason=str(exc),
                    failure_trace_uri=trace_key,
                )
        if mlflow_active:
            mlflow.end_run(status="FAILED")
        raise
