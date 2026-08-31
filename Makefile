SHELL := /bin/bash
.DEFAULT_GOAL := help

.PHONY: help setup validate up down logs ps backend-test backend-quality frontend-test frontend-quality frontend-install test clean

help: ## Show commands
	@awk 'BEGIN {FS = ":.*## "; printf "\nUsage: make <target>\n\n"} /^[a-zA-Z_-]+:.*## / {printf "  %-18s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Verify tools and create .env
	@./scripts/setup.sh

validate: ## Validate the standalone exported starter
	@python3 scripts/validate-starter.py .

up: ## Build and start the starter stack
	@docker compose up --build -d
	@docker compose ps

down: ## Stop the starter stack
	@docker compose down

logs: ## Follow logs
	@docker compose logs -f --tail=150

ps: ## Show service state
	@docker compose ps

backend-test: ## Run FastAPI starter tests
	@docker compose run --rm backend pytest

backend-quality: ## Lint, type-check, and test backend with coverage (container gate)
	@docker compose run --rm backend sh -c "\
		ruff check . && \
		ruff format --check . && \
		mypy app && \
		pytest --cov=app --cov-branch --cov-report=term-missing"

frontend-test: ## Run Nuxt starter type checks
	@docker compose run --rm frontend npm run typecheck

frontend-quality: ## Lint, type-check, and build frontend (container gate)
	@docker compose run --rm frontend sh -c "\
		npm run postinstall && \
		npm run lint && \
		npm run typecheck && \
		npm run build"

frontend-install: ## Install frontend npm dependencies locally
	@cd frontend && npm install

test: backend-test frontend-test ## Run starter verification

clean: ## Remove containers and the disposable database volume
	@docker compose down -v --remove-orphans
