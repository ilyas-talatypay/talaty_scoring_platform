# Talaty Scoring Platform (Foundations V1)

This repo is the V1 foundations of an internal GBM credit scoring platform:
a spec-first model development control plane with portable storage, a metadata DB,
and a minimal execution runner.

## What Is In The Current System

Services:
- `services/api`: FastAPI service with CRUD skeletons, schema endpoints, and runner trigger.
- `services/runner`: Runner API + CLI that executes a `RunSpec` and records run lifecycle.
- `services/web`: Minimal React shell for Datasets / Feature Sets / Runs / Models + dev login.

Packages:
- `packages/core`: Domain models, JSON schema exporter, and storage abstraction.
- `packages/data`: Placeholder for ingestion interfaces (empty).
- `packages/ml`: Placeholder for training/eval libs (empty).

Infra:
- `infra/compose`: Docker Compose (postgres + minio + mlflow + api + runner + web).
- `schemas/v0`: Versioned JSON schemas + OpenAPI JSON (checked in).

## Quickstart (Local)

1) Create the env file:
```
cp infra/compose/env.template infra/compose/.env
```

2) Boot services and migrate:
```
make -f infra/compose/Makefile up
make -f infra/compose/Makefile migrate
```

3) Access:
- API: `http://localhost:8000` (OpenAPI: `/docs`)
- Web: `http://localhost:5173`
- MinIO: `http://localhost:9001`
- MLflow: `http://localhost:5000`

## API Surface (Skeleton)

- Health/version: `GET /health`, `GET /version`
- Schemas: `GET /schemas/v0`, `GET /schemas/v0/{name}`
- CRUD (minimal): `datasets`, `features`, `feature-sets`, `run-specs`, `runs`
- Execution: `POST /runs/execute` (calls runner API)

## Runner V0

The runner accepts a `RunSpec` (YAML via CLI or JSON via API) and:
- validates dataset + feature set versions exist
- creates a `Run` row and transitions status
- writes artifacts to MinIO and logs to DB
- materializes a local workdir under `RUN_WORKDIR`
- logs params/artifacts to MLflow (if configured)

Example spec (`runspec.yaml`):
```
dataset_version_id: "00000000-0000-0000-0000-000000000000"
feature_set_version_id: "00000000-0000-0000-0000-000000000000"
model_family: "gbm"
model_params: {}
split_policy: {}
evaluation_policy: {}
artifact_policy: {}
```

Run it inside compose:
```
docker compose -f infra/compose/docker-compose.yml --env-file infra/compose/.env \
  run --rm runner talaty-runner run --spec /path/to/runspec.yaml
```

Trigger via API:
```
curl -X POST http://localhost:8000/runs/execute \
  -H "Content-Type: application/json" \
  -d '{"run_spec_id":"00000000-0000-0000-0000-000000000000"}'
```

## Storage Conventions

All artifacts go through the S3-compatible store (MinIO locally), using:
- `datasets/{dataset_id}/{version}/`
- `featuresets/{featureset_id}/{version}/`
- `runs/{run_id}/`
- `reports/{run_id}/`

## Schema Export

The domain models are defined in `packages/core/src/core/domain/v0`.
Schemas are exported to `schemas/v0` and served by the API.

Local export (after installing `packages/core`):
```
talaty-export-schemas
```

OpenAPI export (after installing `services/api`):
```
talaty-export-openapi
```

## Compose Notes

- Image tags are configurable with `MINIO_IMAGE_TAG` and `MINIO_MC_IMAGE_TAG`
  (defaults to `latest` if not set).
- MLflow uses a separate Postgres DB (`mlflow`) and MinIO artifacts; see
  `MLFLOW_BACKEND_STORE_URI` and `MLFLOW_ARTIFACT_ROOT` in `infra/compose/env.template`.
- `infra/compose/scripts/` includes backup/restore helpers for Postgres
  and a MinIO sync helper (requires `mc` locally).

## Auth/Login Stub

API accepts `X-User` and falls back to `DEV_USER`. The web Login page stores
`talaty.user` in localStorage and sends it as `X-User` on API requests.

## Root Tooling

Basic lint/test helpers are in the root `Makefile`:
```
make lint
make format
make test
```
