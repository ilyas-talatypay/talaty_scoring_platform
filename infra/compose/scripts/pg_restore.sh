#!/bin/sh
set -e

ENV_FILE=${ENV_FILE:-infra/compose/.env}
IN_FILE=${1:?Usage: pg_restore.sh <backup.sql>}

set -a
. "$ENV_FILE"
set +a

cat "$IN_FILE" | docker compose -f infra/compose/docker-compose.yml --env-file "$ENV_FILE" exec -T postgres \
  psql -U "$POSTGRES_USER" "$POSTGRES_DB"

echo "Restored from $IN_FILE"
