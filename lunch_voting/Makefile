.PHONY: help install install-dev run migrate createsuperuser seed test test-cov lint format clean docker-build docker-up docker-down docker-logs docker-shell docker-test

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install production dependencies
	pip install -r requirements.txt

install-dev: ## Install development dependencies
	pip install -r requirements-dev.txt

run: ## Run development server
	python manage.py runserver

migrate: ## Run database migrations
	python manage.py migrate

createsuperuser: ## Create a superuser
	python manage.py createsuperuser

seed: ## Seed database with sample data
	python manage.py seed_data

test: ## Run tests
	pytest

test-cov: ## Run tests with coverage report
	pytest --cov=apps --cov-report=html --cov-report=term
	@echo "Coverage report generated in htmlcov/"

lint: ## Run flake8 linter
	flake8 .

format: ## Format code (requires black)
	black apps config

clean: ## Clean up Python cache files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf htmlcov/ .pytest_cache/

docker-build: ## Build Docker containers
	docker-compose build

docker-up: ## Start Docker containers
	docker-compose up -d

docker-down: ## Stop Docker containers
	docker-compose down

docker-logs: ## Show Docker logs
	docker-compose logs -f

docker-shell: ## Open shell in Docker container
	docker-compose exec web bash

docker-test: ## Run tests in Docker
	docker-compose exec web pytest

docker-migrate: ## Run migrations in Docker
	docker-compose exec web python manage.py migrate

docker-seed: ## Seed data in Docker
	docker-compose exec web python manage.py seed_data
