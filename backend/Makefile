# Makefile

# Default target
.PHONY: build create-db setup migrate up down test test-setup clean help

# Default target
.DEFAULT_GOAL := help

help:
	@echo "Available targets:"
	@echo ""
	@echo "  build        Build Docker containers for the application"
	@echo "  create-db    Start the database server and create a development database"
	@echo "  migrate      Apply migrations to the development database"
	@echo "  setup        Set up development environment (build + create-db + migrate)"
	@echo ""
	@echo "  up           Start the backend web application (available at http://localhost:8000)"
	@echo "  down         Stop all running backend services"
	@echo ""
	@echo "  test-setup   Set up test database (drop/create test DB + run test migrations)"
	@echo "  test         Run the full test suite (includes test-setup)"
	@echo "  clean        Remove cache files and artifacts directory"
	@echo ""
	@echo "  help         Show this help message"
	@echo ""
	@echo "Common workflows:"
	@echo "  First time setup:   make setup && make up"
	@echo "  Daily development:  git pull && make migrate && make up"
	@echo "  Run tests:          make test"
	@echo "  Clean shutdown:     make down && make clean"

build:
	@docker compose build

drop-db:
	@echo "Dropping development database..."
	@docker compose up -d db
	@docker compose run --rm db sh -c 'echo "dropping $$POSTGRES_DB"; PGPASSWORD=$$POSTGRES_PASSWORD psql -h db -U $$POSTGRES_USER -d postgres -c "DROP DATABASE IF EXISTS $$POSTGRES_DB" || echo "failed to drop $$POSTGRES_DB"'

create-db:
	@echo "Creating development database..."
	@docker compose up -d db
# create development database only if it doesn't already exist
	@docker compose run --rm db sh -c 'echo "creating $$POSTGRES_DB"; PGPASSWORD=$$POSTGRES_PASSWORD psql -h db -U $$POSTGRES_USER -d postgres -c "CREATE DATABASE $$POSTGRES_DB" || echo "$$POSTGRES_DB already exists"'

migrate:
	@echo "Migrating the development database..."
	@docker compose up -d db
# run all flyway migrations for the development environment
	@docker compose run --rm db-migrations migrate

setup: build create-db migrate
# pass

up:
	@echo "Running backend..."
	@docker compose up -d django-web
	@echo "Backend is running at http://localhost:8000/fhir/"

down:
	@echo "Shutting down backend..."
	@docker compose down

test-setup:
	@echo "Setting up test database..."
	@docker compose -f compose.test.yml up -d --wait db
# drop, create, and migrate test database
	@docker compose -f compose.test.yml exec db sh -c 'echo "DROP   $$POSTGRES_DB"; PGPASSWORD=$$POSTGRES_PASSWORD psql -q -h localhost -U "$$POSTGRES_USER" -d postgres -c "DROP DATABASE IF EXISTS $$POSTGRES_DB"'
	@docker compose -f compose.test.yml exec db sh -c 'echo "CREATE $$POSTGRES_DB"; PGPASSWORD=$$POSTGRES_PASSWORD psql -q -h localhost -U "$$POSTGRES_USER" -d postgres -c "CREATE DATABASE $$POSTGRES_DB"'
	@docker compose -f compose.test.yml run --rm db-migrations migrate

test: test-setup
	@echo "Running backend tests..."
	@docker compose -f compose.test.yml run --rm django-web python manage.py test

clean:
	@echo "Cleaning up cache files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@rm -rf artifacts/
	@echo "Cleanup done."

