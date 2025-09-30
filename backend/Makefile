# Makefile

# Default target
.PHONY: build setup up down test test-setup clean

build: 
	@docker compose build

setup: build
	@echo "Setting up development database..."
	@docker compose up -d db
# create development database only if it doesn't already exist
	@docker compose run --rm -e PGPASSWORD=postgres db sh -c 'psql -h db -U $$NPD_DB_USER -tc "SELECT 1 FROM pg_database WHERE datname = '"'"'$$NPD_DB_NAME'"'"';" | grep -q 1 || psql -h db -U $$NPD_DB_USER -c "CREATE DATABASE $$NPD_DB_NAME"'
# run all flyway migrations for the development environment
	@docker compose run --rm db-migrations migrate -environment=development

up:
	@echo "Running backend..."
	@docker compose up -d
	@echo "Backend is running at http://localhost:8000"

down:
	@echo "Shutting down backend..."
	@docker compose down 

test-setup:
	@echo "Setting up test database..."
	@docker compose up -d db
# drop and create test database
	@docker compose run --rm --env-from-file ./test.env -e PGPASSWORD=postgres db sh -c 'echo "DROP   $$NPD_DB_NAME"; psql -q -h db -U "$$NPD_DB_USER" -c "DROP DATABASE IF EXISTS $$NPD_DB_NAME"' 
	@docker compose run --rm --env-from-file ./test.env -e PGPASSWORD=postgres db sh -c 'echo "CREATE $$NPD_DB_NAME"; psql -q -h db -U "$$NPD_DB_USER" -c "CREATE DATABASE $$NPD_DB_NAME"' 
# run only migrations for the test environment, not bulk data inserts
	@docker compose run --rm db-migrations migrate -environment=test -locations="filesystem:/flyway/sql/migrations"

test: test-setup
	@echo "Running backend tests..."
	@docker compose run --rm --env-from-file test.env django-web python manage.py test

clean:
	@echo "Cleaning up cache files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@rm -rf artifacts/
	@echo "Cleanup done."
