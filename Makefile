.PHONY: help install venv test lint fmt clean docker-up docker-down migrate seed run dev

# Default target
help:
	@echo "Available commands:"
	@echo "  install     - Install dependencies"
	@echo "  venv        - Create virtual environment"
	@echo "  test        - Run tests with coverage"
	@echo "  lint        - Run linters"
	@echo "  fmt         - Format code"
	@echo "  clean       - Clean up temporary files"
	@echo "  docker-up   - Start Docker services"
	@echo "  docker-down - Stop Docker services"
	@echo "  migrate     - Run database migrations"
	@echo "  seed        - Seed database with demo data"
	@echo "  run         - Run the application"
	@echo "  dev         - Run in development mode with auto-reload"

# Python environment
venv:
	python3.11 -m venv venv
	@echo "Virtual environment created. Run 'source venv/bin/activate' to activate."

install: venv
	. venv/bin/activate && pip install --upgrade pip
	. venv/bin/activate && pip install -r requirements.txt
	. venv/bin/activate && pip install -e .

# Code quality
lint:
	. venv/bin/activate && ruff check engram tests
	. venv/bin/activate && mypy engram

fmt:
	. venv/bin/activate && ruff check --fix engram tests
	. venv/bin/activate && black engram tests
	. venv/bin/activate && isort engram tests

# Testing
test:
	. venv/bin/activate && pytest

test-cov:
	. venv/bin/activate && pytest --cov=engram --cov-report=html --cov-report=term

# Database
migrate:
	. venv/bin/activate && alembic upgrade head

migrate-create:
	. venv/bin/activate && alembic revision --autogenerate -m "$(MSG)"

# Docker
docker-up:
	docker-compose up --build -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

# Application
run:
	. venv/bin/activate && python -m engram.api.server

dev:
	. venv/bin/activate && uvicorn engram.api.server:app --reload --host 0.0.0.0 --port 8000

# Demo data
seed:
	. venv/bin/activate && python examples/seed_demo.py

# Cleanup
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/

# Pre-commit
pre-commit-install:
	. venv/bin/activate && pre-commit install

pre-commit-run:
	. venv/bin/activate && pre-commit run --all-files

# Health check
health:
	curl -f http://localhost:8000/v1/health || echo "Service not running"

# Smoke test for second brain functionality
smoke-second-brain:
	. venv/bin/activate && python scripts/smoke_second_brain.py

# Development setup
setup-dev: install pre-commit-install migrate seed
	@echo "Development environment ready!"
	@echo "Run 'make dev' to start the development server"

# Production setup
setup-prod: install migrate
	@echo "Production environment ready!"
	@echo "Run 'make run' to start the production server"
