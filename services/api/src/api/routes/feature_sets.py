from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from api.auth import get_user
from sqlalchemy.orm import Session

from api.db import models
from api.db.session import get_session
from api.schemas import FeatureSetCreate, FeatureSetVersionCreate
from core.domain.v0 import FeatureSet, FeatureSetVersion

router = APIRouter(prefix="/feature-sets", tags=["feature_sets"])


@router.post("/", response_model=FeatureSet)
def create_feature_set(payload: FeatureSetCreate, db: Session = Depends(get_session)) -> FeatureSet:
    feature_set = models.FeatureSet(**payload.model_dump())
    db.add(feature_set)
    db.commit()
    db.refresh(feature_set)
    return FeatureSet.model_validate(feature_set)


@router.get("/", response_model=list[FeatureSet])
def list_feature_sets(db: Session = Depends(get_session)) -> list[FeatureSet]:
    feature_sets = db.query(models.FeatureSet).order_by(models.FeatureSet.created_at.desc()).all()
    return [FeatureSet.model_validate(item) for item in feature_sets]


@router.post("/{feature_set_id}/versions", response_model=FeatureSetVersion)
def create_feature_set_version(
    feature_set_id: UUID,
    payload: FeatureSetVersionCreate,
    db: Session = Depends(get_session),
    user: str = Depends(get_user),
) -> FeatureSetVersion:
    feature_set = (
        db.query(models.FeatureSet).filter(models.FeatureSet.id == feature_set_id).one_or_none()
    )
    if not feature_set:
        raise HTTPException(status_code=404, detail="Feature set not found")
    data = payload.model_dump()
    if data.get("created_by") is None:
        data["created_by"] = user
    version = models.FeatureSetVersion(feature_set_id=feature_set_id, **data)
    db.add(version)
    db.commit()
    db.refresh(version)
    return FeatureSetVersion.model_validate(version)


@router.get("/{feature_set_id}/versions", response_model=list[FeatureSetVersion])
def list_feature_set_versions(
    feature_set_id: UUID, db: Session = Depends(get_session)
) -> list[FeatureSetVersion]:
    versions = (
        db.query(models.FeatureSetVersion)
        .filter(models.FeatureSetVersion.feature_set_id == feature_set_id)
        .order_by(models.FeatureSetVersion.created_at.desc())
        .all()
    )
    return [FeatureSetVersion.model_validate(item) for item in versions]

