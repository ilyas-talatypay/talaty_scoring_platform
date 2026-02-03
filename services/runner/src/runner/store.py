from core.storage import S3CompatibleStore, S3Settings
from runner.config import RunnerSettings


def get_store(settings: RunnerSettings) -> S3CompatibleStore:
    return S3CompatibleStore(
        S3Settings(
            endpoint_url=settings.S3_ENDPOINT,
            access_key=settings.S3_ACCESS_KEY,
            secret_key=settings.S3_SECRET_KEY,
            bucket=settings.S3_BUCKET,
            region=settings.S3_REGION,
        )
    )

