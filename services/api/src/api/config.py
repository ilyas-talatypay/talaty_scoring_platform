from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_VERSION: str = "0.1.0"
    GIT_SHA: str | None = None
    DATABASE_URL: str = "postgresql+psycopg://talaty:talaty@localhost:5432/talaty"

    S3_ENDPOINT: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_BUCKET: str = "talaty"
    S3_REGION: str = "us-east-1"

    RUNNER_URL: str = "http://runner:9002"
    DEV_USER: str = "dev-user"


_settings = Settings()


def get_settings() -> Settings:
    return _settings

