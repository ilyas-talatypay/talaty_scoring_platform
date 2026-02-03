from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.config import get_settings
from api.routes import (
    datasets_router,
    feature_sets_router,
    features_router,
    health_router,
    run_specs_router,
    runs_router,
    schemas_router,
)


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Talaty Scoring API",
        version=settings.APP_VERSION,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(schemas_router)
    app.include_router(datasets_router)
    app.include_router(features_router)
    app.include_router(feature_sets_router)
    app.include_router(run_specs_router)
    app.include_router(runs_router)
    return app


app = create_app()

