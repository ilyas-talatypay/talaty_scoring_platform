from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from api.auth import get_user
from sqlalchemy.orm import Session

from api.db import models
from api.db.session import get_session
from api.schemas import DatasetCreate, DatasetVersionCreate
from core.domain.v0 import Dataset, DatasetVersion

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.post("/", response_model=Dataset)
def create_dataset(payload: DatasetCreate, db: Session = Depends(get_session)) -> Dataset:
    dataset = models.Dataset(**payload.model_dump())
    db.add(dataset)
    db.commit()
    db.refresh(dataset)
    return Dataset.model_validate(dataset)


@router.get("/", response_model=list[Dataset])
def list_datasets(db: Session = Depends(get_session)) -> list[Dataset]:
    datasets = db.query(models.Dataset).order_by(models.Dataset.created_at.desc()).all()
    return [Dataset.model_validate(item) for item in datasets]


@router.get("/{dataset_id}", response_model=Dataset)
def get_dataset(dataset_id: UUID, db: Session = Depends(get_session)) -> Dataset:
    dataset = db.query(models.Dataset).filter(models.Dataset.id == dataset_id).one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return Dataset.model_validate(dataset)


@router.post("/{dataset_id}/versions", response_model=DatasetVersion)
def create_dataset_version(
    dataset_id: UUID,
    payload: DatasetVersionCreate,
    db: Session = Depends(get_session),
    user: str = Depends(get_user),
) -> DatasetVersion:
    dataset = db.query(models.Dataset).filter(models.Dataset.id == dataset_id).one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    data = payload.model_dump()
    if data.get("created_by") is None:
        data["created_by"] = user
    version = models.DatasetVersion(dataset_id=dataset_id, **data)
    db.add(version)
    db.commit()
    db.refresh(version)
    return DatasetVersion.model_validate(version)


@router.get("/{dataset_id}/versions", response_model=list[DatasetVersion])
def list_dataset_versions(dataset_id: UUID, db: Session = Depends(get_session)) -> list[DatasetVersion]:
    versions = (
        db.query(models.DatasetVersion)
        .filter(models.DatasetVersion.dataset_id == dataset_id)
        .order_by(models.DatasetVersion.created_at.desc())
        .all()
    )
    return [DatasetVersion.model_validate(item) for item in versions]

