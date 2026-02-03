import os
from dataclasses import dataclass

import boto3
from botocore.exceptions import ClientError

from core.storage.base import ObjectStore


@dataclass(frozen=True)
class S3Settings:
    endpoint_url: str
    access_key: str
    secret_key: str
    bucket: str
    region: str = "us-east-1"

    @classmethod
    def from_env(cls) -> "S3Settings":
        return cls(
            endpoint_url=os.environ["S3_ENDPOINT"],
            access_key=os.environ["S3_ACCESS_KEY"],
            secret_key=os.environ["S3_SECRET_KEY"],
            bucket=os.environ["S3_BUCKET"],
            region=os.getenv("S3_REGION", "us-east-1"),
        )


class S3CompatibleStore(ObjectStore):
    def __init__(self, settings: S3Settings) -> None:
        self._settings = settings
        self._client = boto3.client(
            "s3",
            endpoint_url=settings.endpoint_url,
            aws_access_key_id=settings.access_key,
            aws_secret_access_key=settings.secret_key,
            region_name=settings.region,
        )

    @property
    def bucket(self) -> str:
        return self._settings.bucket

    def put_bytes(self, key: str, data: bytes, content_type: str | None = None) -> None:
        args = {"Bucket": self.bucket, "Key": key, "Body": data}
        if content_type:
            args["ContentType"] = content_type
        self._client.put_object(**args)

    def get_bytes(self, key: str) -> bytes:
        response = self._client.get_object(Bucket=self.bucket, Key=key)
        return response["Body"].read()

    def list(self, prefix: str) -> list[str]:
        response = self._client.list_objects_v2(Bucket=self.bucket, Prefix=prefix)
        return [item["Key"] for item in response.get("Contents", [])]

    def exists(self, key: str) -> bool:
        try:
            self._client.head_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError as exc:
            if exc.response.get("ResponseMetadata", {}).get("HTTPStatusCode") == 404:
                return False
            raise

    def signed_url(self, key: str, expires_in: int = 3600) -> str:
        return self._client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expires_in,
        )

