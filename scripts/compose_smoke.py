import os
import time
from typing import Any

import boto3
import httpx
from botocore.exceptions import ClientError


API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
RUNNER_URL = os.getenv("RUNNER_URL", "http://localhost:9002")
S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://localhost:9000")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "minioadmin")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "minioadmin")
S3_BUCKET = os.getenv("S3_BUCKET", "talaty")
S3_REGION = os.getenv("S3_REGION", "us-east-1")
SMOKE_USER = os.getenv("SMOKE_USER", "smoke-user")


def wait_for(description: str, check_fn, timeout_s: int = 60, interval_s: int = 2) -> None:
    start = time.time()
    last_error: Exception | None = None
    while time.time() - start < timeout_s:
        try:
            if check_fn():
                return
        except Exception as exc:  # noqa: BLE001
            last_error = exc
        time.sleep(interval_s)
    detail = f": {last_error}" if last_error else ""
    raise RuntimeError(f"Timeout waiting for {description}{detail}")


def _s3_client():
    return boto3.client(
        "s3",
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_KEY,
        region_name=S3_REGION,
    )


def main() -> None:
    headers = {"X-User": SMOKE_USER}
    client = httpx.Client(timeout=30)

    wait_for(
        "API health",
        lambda: client.get(f"{API_BASE_URL}/health").status_code == 200,
    )
    wait_for(
        "Runner health",
        lambda: client.get(f"{RUNNER_URL}/health").status_code == 200,
    )

    s3 = _s3_client()

    def bucket_ready() -> bool:
        try:
            s3.head_bucket(Bucket=S3_BUCKET)
            return True
        except ClientError as exc:
            code = exc.response.get("ResponseMetadata", {}).get("HTTPStatusCode")
            if code == 404:
                return False
            raise

    wait_for("MinIO bucket", bucket_ready)

    dataset_payload = {"name": "smoke-dataset", "storage_uri": "s3://talaty/datasets"}
    dataset = client.post(f"{API_BASE_URL}/datasets", json=dataset_payload, headers=headers)
    dataset.raise_for_status()
    dataset_id = dataset.json()["id"]

    dataset_version_payload = {"version": "v1", "data_fingerprint": "smoke-fp"}
    dataset_version = client.post(
        f"{API_BASE_URL}/datasets/{dataset_id}/versions",
        json=dataset_version_payload,
        headers=headers,
    )
    dataset_version.raise_for_status()
    dataset_version_id = dataset_version.json()["id"]

    feature_set_payload = {"name": "smoke-feature-set"}
    feature_set = client.post(
        f"{API_BASE_URL}/feature-sets",
        json=feature_set_payload,
        headers=headers,
    )
    feature_set.raise_for_status()
    feature_set_id = feature_set.json()["id"]

    feature_set_version_payload = {"version": "v1", "features": ["f1", "f2"]}
    feature_set_version = client.post(
        f"{API_BASE_URL}/feature-sets/{feature_set_id}/versions",
        json=feature_set_version_payload,
        headers=headers,
    )
    feature_set_version.raise_for_status()
    feature_set_version_id = feature_set_version.json()["id"]

    run_spec_payload = {
        "dataset_version_id": dataset_version_id,
        "feature_set_version_id": feature_set_version_id,
        "model_family": "gbm",
        "split_policy": {},
        "model_params": {},
        "evaluation_policy": {},
        "artifact_policy": {},
    }
    run_spec = client.post(
        f"{API_BASE_URL}/run-specs",
        json=run_spec_payload,
        headers=headers,
    )
    run_spec.raise_for_status()
    run_spec_id = run_spec.json()["id"]

    execute_response = client.post(
        f"{API_BASE_URL}/runs/execute",
        json={"run_spec_id": run_spec_id},
        headers=headers,
    )
    execute_response.raise_for_status()
    run_id = execute_response.json()["run_id"]

    def run_succeeded() -> bool:
        response = client.get(f"{API_BASE_URL}/runs", headers=headers)
        response.raise_for_status()
        for item in response.json():
            if item["id"] == run_id:
                return item["status"] == "succeeded"
        return False

    wait_for("run to succeed", run_succeeded, timeout_s=120, interval_s=3)

    required_keys = {
        f"runs/{run_id}/runspec.yaml",
        f"runs/{run_id}/meta.json",
        f"runs/{run_id}/logs/runner.log",
    }

    def artifacts_ready() -> bool:
        response = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=f"runs/{run_id}/")
        keys = {item["Key"] for item in response.get("Contents", [])}
        return required_keys.issubset(keys)

    wait_for("run artifacts in MinIO", artifacts_ready, timeout_s=60, interval_s=3)

    client.close()


if __name__ == "__main__":
    main()
