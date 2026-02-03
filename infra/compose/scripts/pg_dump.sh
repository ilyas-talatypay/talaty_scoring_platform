#!/bin/sh
set -e

ENV_FILE=${ENV_FILE:-infra/compose/.env}
OUT_FILE=${1:-backup.sql}

set -a
. "$ENV_FILE"
set +a

docker compose -f infra/compose/docker-compose.yml --env-file "$ENV_FILE" exec -T postgres \
  pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > "$OUT_FILE"

echo "Wrote backup to $OUT_FILE"
