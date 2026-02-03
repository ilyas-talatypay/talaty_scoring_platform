#!/bin/sh
set -e

ENV_FILE=${ENV_FILE:-infra/compose/.env}
SRC=${1:?Usage: minio_sync.sh <local_dir> [bucket_prefix]}
PREFIX=${2:-}

set -a
. "$ENV_FILE"
set +a

if ! command -v mc >/dev/null 2>&1; then
  echo "minio client (mc) not found. Install it and re-run."
  exit 1
fi

mc alias set local "$S3_ENDPOINT" "$S3_ACCESS_KEY" "$S3_SECRET_KEY"
mc mirror "$SRC" "local/$S3_BUCKET/$PREFIX"

echo "Synced $SRC to s3://$S3_BUCKET/$PREFIX"
