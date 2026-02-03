from pydantic_settings import BaseSettings, SettingsConfigDict


class RunnerSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    DATABASE_URL: str = "postgresql+psycopg://talaty:talaty@localhost:5432/talaty"
    RUN_WORKDIR: str = "/tmp/talaty/runs"

    S3_ENDPOINT: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_BUCKET: str = "talaty"
    S3_REGION: str = "us-east-1"

    GIT_SHA: str | None = None
    IMAGE_TAG: str | None = None

    MLFLOW_TRACKING_URI: str | None = None
    MLFLOW_S3_ENDPOINT_URL: str | None = None


_settings = RunnerSettings()


def get_settings() -> RunnerSettings:
    return _settings

