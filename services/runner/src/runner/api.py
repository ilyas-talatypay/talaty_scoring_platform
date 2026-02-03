from datetime import datetime
from uuid import UUID

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict

from core.domain.v0 import RunSpec
from core.domain.v0.enums import RunStatus
from runner.config import get_settings
from runner.runtime import execute_run_spec, get_run_spec_by_id
from runner.store import get_store


class ExecuteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_spec_id: UUID | None = None
    run_spec: RunSpec | None = None


class ExecuteResponse(BaseModel):
    run_id: UUID
    status: RunStatus
    started_at: datetime


def create_app() -> FastAPI:
    app = FastAPI(title="Talaty Runner", version="0.1.0")

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    @app.post("/execute", response_model=ExecuteResponse)
    def execute(payload: ExecuteRequest) -> ExecuteResponse:
        if not payload.run_spec_id and not payload.run_spec:
            raise HTTPException(status_code=400, detail="Provide run_spec_id or run_spec")

        settings = get_settings()
        store = get_store(settings)

        if payload.run_spec_id:
            run_spec = get_run_spec_by_id(settings, payload.run_spec_id)
            if not run_spec:
                raise HTTPException(status_code=404, detail="Run spec not found")
        else:
            run_spec = payload.run_spec

        run_id, started_at, status = execute_run_spec(
            settings=settings,
            store=store,
            run_spec=run_spec,
        )
        return ExecuteResponse(run_id=run_id, status=status, started_at=started_at)

    return app


app = create_app()

