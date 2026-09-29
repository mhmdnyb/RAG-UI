.DEFAULT_GOAL := help

# Keep equal to MAX_CONCURRENT_JOBS in .env.
MAX_CONCURRENT_JOBS ?= 30

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

install:  ## Install all dependencies
	pip install -r requirements.txt -r requirements-ml.txt -r requirements-dev.txt

infra:  ## Start Postgres + Redis
	docker compose up -d db redis

dev:  ## Run the API (reload)
	uvicorn --factory app.server:create_app --reload --port 8000

worker:  ## Run a TaskIQ worker
	taskiq worker app.worker.broker:broker --max-async-tasks $(MAX_CONCURRENT_JOBS)

seed:  ## Load classes.csv into Postgres
	python -m scripts.seed_classes

test:  ## Run the test suite
	pytest -q

lint:  ## Check lint and formatting without modifying files (same as CI)
	ruff format --check app tests scripts
	ruff check app tests scripts

format:  ## Safe fixes and formatting (same as pre-commit)
	ruff check --fix app tests scripts
	ruff format app tests scripts

.PHONY: help install infra dev worker seed test lint format
