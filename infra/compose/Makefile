.PHONY: up down reset migrate seed mlflow-db-init

POSTGRES_USER ?= talaty

COMPOSE = docker compose -f infra/compose/docker-compose.yml --env-file infra/compose/.env

up:
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) down

reset:
	$(COMPOSE) down -v

migrate:
	$(COMPOSE) run --rm api alembic upgrade head

mlflow-db-init:
	$(COMPOSE) exec -T postgres psql -U $(POSTGRES_USER) -tc "SELECT 1 FROM pg_database WHERE datname='mlflow'" | grep -q 1 || \
	$(COMPOSE) exec -T postgres psql -U $(POSTGRES_USER) -c "CREATE DATABASE mlflow;"

seed:
	@echo "Seed not implemented yet."

