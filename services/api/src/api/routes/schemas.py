import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/schemas", tags=["schemas"])


def _schema_dir() -> Path:
    repo_root = Path(__file__).resolve().parents[5]
    return repo_root / "schemas" / "v0"


@router.get("/v0")
def schema_bundle() -> dict:
    path = _schema_dir() / "bundle.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Schema bundle not found")
    return json.loads(path.read_text())


@router.get("/v0/{name}")
def schema_by_name(name: str) -> dict:
    path = _schema_dir() / f"{name}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Schema not found")
    return json.loads(path.read_text())

