# Makefile

# set NPD_DEVELOPMENT to "True" in your shell to skip dangerous action
# confirmation steps
NPD_DEVELOPMENT ?= no

# Default target
.PHONY: build create-db setup migrate update up down \
	test test-setup test-server \
	clean-frontend clean \
	help

# Default target
.DEFAULT_GOAL := help

help:
	@echo "Available targets:"
	@echo ""
	@echo "  build        Build Docker containers for the application"
	@echo "  create-db    Start the database server and create a development database"
	@echo "  migrate      Apply migrations to the development database"
	@echo "  setup        Set up development environment (build + create-db + migrate)"
	@echo "  update       Update development environment"
	@echo "  install-tools  Install Python development tools"
	@echo ""
	@echo "  up           Start the backend web application at http://localhost:8000 with static assets"
	@echo "  down         Stop all running backend services"
	@echo ""
	@echo "  test-setup   Set up test database (drop/create test DB + run test migrations)"
	@echo "  test         Run the full backend test suite with setup"
	@echo "  test-fast    Run the backend test suite without rerunning database setup"
	@echo "               Use ARGS=... to pass arguments."
	@echo "  test-server  Start a test server suitable for e2e testing with playwright"
	@echo ""
	@echo "  clean        Remove cache files, test artifacts, and transient frontend assets"
	@echo ""
	@echo "  lint         Check Python code against the ruff linter"
	@echo "  format       Format Python code with ruff"
	@echo ""
	@echo "  createsuperuser  Interactively set up a Django superuser account."
	@echo "                   Pass env vars to run automatically:"
	@echo "                     DJANGO_SUPERUSER_EMAIL"
	@echo "                     DJANGO_SUPERUSER_USERNAME"
	@echo "                     DJANGO_SUPERUSER_PASSWORD"
	@echo ""
	@echo "  drop-db      \033[31m[DANGEROUS]\033[0m Drop the development database"
	@echo "  reset-db     \033[31m[DANGEROUS]\033[0m Drop and fully recreate the development database"
	@echo ""
	@echo "  help         Show this help message"
	@echo ""
	@echo "Common workflows:"
	@echo "  First time setup:   make setup && make install-tools && make up"
	@echo "  Daily development:  git pull && make update && make up"
	@echo "  Before committing:  make test && make lint"
	@echo "  Run tests:          make test"
	@echo "  Run some tests:     make test-fast ARGS=npdfhir.tests"
	@echo "  Run one test:       make test-fast ARGS=provider_directory.tests.test_frontend_settings.TestFeatureFlags.test_returns_flags_json"
	@echo "  Clean shutdown:     make down && make clean"

.PHONY: install-tools
install-tools:
	@echo "Setting up local development tools using $(shell which pip)"
	@pip install ruff; \
		pip install pre-commit; \
		cd ..; \
		pre-commit install

.PHONY: lint
lint:
	@ruff check .

.PHONY: format
format:
	@ruff format

build:
	@docker compose build

drop-db:
ifneq ($(NPD_DEVELOPMENT), True)
	@printf "Are you sure you want to drop your local database? [y/N] " && read ans && ( [[ "$${ans:-N}" == y ]] || ( echo "cancelling changes" && exit 1 ) )
endif
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

reset-db:
	@echo "Resetting the development database..."
	@docker compose down db
	@$(MAKE) drop-db
	@$(MAKE) create-db
	@$(MAKE) migrate

# prepare the local working space for NPD development
setup: build create-db migrate

# only rebuild frontend assets if they don't already exist
provider_directory/static/.vite/manifest.json:
	@echo "Building frontend assets with VITE_API_BASE_URL=$(VITE_API_BASE_URL)"
	@cd ..; \
		docker compose run --rm -e VITE_API_BASE_URL=$(VITE_API_BASE_URL) web sh -c "npm install && npm run build"

build-frontend-assets: clean-frontend
	export VITE_API_BASE_URL=http://localhost:8000; \
		$(MAKE) provider_directory/static/.vite/manifest.json

update: build migrate build-frontend-assets

# build frontend assets and ensure the backend application is running
up:
	$(MAKE) build-frontend-assets
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

test-fast:
	@echo "Rerunning backend tests..."
	@docker compose -f compose.test.yml run --rm django-web python manage.py test $(ARGS)

clean-frontend:
	@echo "Cleaning up frontend assets..."
	@rm -rf provider_directory/static/*
	@rm -rf provider_directory/static/.vite

clean:
	@echo "Cleaning up cache files, test artifacts..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@rm -rf artifacts/
	$(MAKE) clean-frontend
	@echo "Cleanup done."

createsuperuser:
ifeq ($(and $(DJANGO_SUPERUSER_EMAIL),$(DJANGO_SUPERUSER_USERNAME),$(DJANGO_SUPERUSER_PASSWORD)),)
	@docker compose run --rm django-web python manage.py createsuperuser
else
	@docker compose run -e DJANGO_SUPERUSER_EMAIL="$(DJANGO_SUPERUSER_EMAIL)" \
						-e DJANGO_SUPERUSER_USERNAME="$(DJANGO_SUPERUSER_USERNAME)" \
						-e DJANGO_SUPERUSER_PASSWORD="$(DJANGO_SUPERUSER_PASSWORD)" \
						--rm django-web python manage.py createsuperuser --no-input
endif

seed-users:
	@docker compose run -e DJANGO_SUPERUSER_EMAIL="npd.admin@cms.hhs.gov" \
						-e DJANGO_SUPERUSER_USERNAME="npdadmin" \
						-e DJANGO_SUPERUSER_PASSWORD="password123" \
						--rm django-web python manage.py createsuperuser --no-input
##
# end-to-end test support
##

build-frontend-test-assets: clean-frontend
	export VITE_API_BASE_URL=http://localhost:8008; \
		$(MAKE) provider_directory/static/.vite/manifest.json

test-server: test-setup build-frontend-test-assets
	@docker compose -f compose.test.yml run --rm --publish 8008:8008 django-web python manage.py runserver 0.0.0.0:8008
