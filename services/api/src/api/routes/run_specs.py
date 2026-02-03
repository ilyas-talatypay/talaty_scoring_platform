from fastapi import APIRouter, Depends, HTTPException
from api.auth import get_user
from sqlalchemy.orm import Session

from api.db import models
from api.db.session import get_session
from api.schemas import RunSpecCreate
from core.domain.v0 import RunSpec

router = APIRouter(prefix="/run-specs", tags=["run_specs"])


@router.post("/", response_model=RunSpec)
def create_run_spec(
    payload: RunSpecCreate,
    db: Session = Depends(get_session),
    user: str = Depends(get_user),
) -> RunSpec:
    dataset_version = (
        db.query(models.DatasetVersion)
        .filter(models.DatasetVersion.id == payload.dataset_version_id)
        .one_or_none()
    )
    if not dataset_version:
        raise HTTPException(status_code=404, detail="Dataset version not found")

    feature_set_version = (
        db.query(models.FeatureSetVersion)
        .filter(models.FeatureSetVersion.id == payload.feature_set_version_id)
        .one_or_none()
    )
    if not feature_set_version:
        raise HTTPException(status_code=404, detail="Feature set version not found")

    data = payload.model_dump()
    if data.get("created_by") is None:
        data["created_by"] = user
    run_spec = models.RunSpec(**data)
    db.add(run_spec)
    db.commit()
    db.refresh(run_spec)
    return RunSpec.model_validate(run_spec)


@router.get("/", response_model=list[RunSpec])
def list_run_specs(db: Session = Depends(get_session)) -> list[RunSpec]:
    run_specs = db.query(models.RunSpec).order_by(models.RunSpec.created_at.desc()).all()
    return [RunSpec.model_validate(item) for item in run_specs]

