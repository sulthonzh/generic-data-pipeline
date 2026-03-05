.PHONY: help build up down restart logs test test-unit test-int test-e2e clean

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build all Docker images
	docker-compose build

up: ## Start all services
	docker-compose up -d
	@echo "Waiting for services to be healthy..."
	@sleep 5

down: ## Stop all services
	docker-compose down

restart: down up ## Restart all services

logs: ## Show logs from all services
	docker-compose logs -f

logs-pipeline: ## Show logs from pipeline service
	docker-compose logs -f pipeline-service

logs-mock: ## Show logs from mock server
	docker-compose logs -f mock-server

test: ## Run all tests (unit + integration)
	docker-compose exec pipeline-service pytest tests/test_unit/ tests/test_integration/ -v

test-unit: ## Run unit tests only
	docker-compose exec pipeline-service pytest tests/test_unit/ -v

test-int: ## Run integration tests only
	docker-compose exec pipeline-service pytest tests/test_integration/ -v

test-e2e: ## Run e2e tests (requires running stack)
	pytest tests/test_e2e/ -v -m e2e

test-coverage: ## Run tests with coverage report
	docker-compose exec pipeline-service pytest tests/test_unit/ tests/test_integration/ -v --cov=. --cov-report=html --cov-report=term-missing

test-all: test ## Alias for test

clean: ## Stop and remove all containers, volumes, and test artifacts
	docker-compose down -v
	rm -f test.db
	rm -rf htmlcov/ .pytest_cache/ __pycache__ */__pycache__ */*/__pycache__

setup: build up ## Setup everything (build and start)

health: ## Check health of all services
	@echo "Mock Server:"
	@curl -s http://localhost:5001/api/health | jq .
	@echo "Pipeline Service:"
	@curl -s http://localhost:8000/api/health | jq .
	@echo "PostgreSQL:"
	@docker-compose exec -T postgres pg_isready -U postgres

ingest: ## Run data ingestion
	@curl -X POST http://localhost:8000/api/ingest | jq .

customers: ## Get all customers from database
	@curl "http://localhost:8000/api/customers?page=1&limit=10" | jq .
