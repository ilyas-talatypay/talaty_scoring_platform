from fastapi import APIRouter

from api.config import get_settings

router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.get("/version")
def version() -> dict:
    settings = get_settings()
    return {"version": settings.APP_VERSION, "git_sha": settings.GIT_SHA}

