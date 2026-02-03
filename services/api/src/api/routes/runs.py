from datetime import datetime

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.config import get_settings
from api.db import models
from api.db.session import get_session
from api.schemas import RunCreate, RunExecuteRequest
from core.domain.v0 import Run, RunStatus

router = APIRouter(prefix="/runs", tags=["runs"])


@router.post("/", response_model=Run)
def create_run(payload: RunCreate, db: Session = Depends(get_session)) -> Run:
    run_spec = (
        db.query(models.RunSpec).filter(models.RunSpec.id == payload.run_spec_id).one_or_none()
    )
    if not run_spec:
        raise HTTPException(status_code=404, detail="Run spec not found")

    run = models.Run(
        run_spec_id=payload.run_spec_id,
        status=RunStatus.QUEUED,
        created_at=datetime.utcnow(),
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return Run.model_validate(run)


@router.get("/", response_model=list[Run])
def list_runs(db: Session = Depends(get_session)) -> list[Run]:
    runs = db.query(models.Run).order_by(models.Run.created_at.desc()).all()
    return [Run.model_validate(item) for item in runs]


@router.post("/execute")
def execute_run(payload: RunExecuteRequest) -> dict:
    settings = get_settings()
    try:
        response = httpx.post(
            f"{settings.RUNNER_URL}/execute",
            json={"run_spec_id": str(payload.run_spec_id)},
            timeout=30,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Runner error: {exc}") from exc
    return response.json()

