from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.db import models
from api.db.session import get_session
from api.schemas import FeatureCreate
from core.domain.v0 import Feature

router = APIRouter(prefix="/features", tags=["features"])


@router.post("/", response_model=Feature)
def create_feature(payload: FeatureCreate, db: Session = Depends(get_session)) -> Feature:
    feature = models.Feature(**payload.model_dump())
    db.add(feature)
    db.commit()
    db.refresh(feature)
    return Feature.model_validate(feature)


@router.get("/", response_model=list[Feature])
def list_features(db: Session = Depends(get_session)) -> list[Feature]:
    features = db.query(models.Feature).order_by(models.Feature.created_at.desc()).all()
    return [Feature.model_validate(item) for item in features]

