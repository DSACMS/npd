# Makefile

# Default target
.PHONY: dev-up dev-down test clean

dev-up:
	@echo "Running containers in dev mode..."
	@docker-compose up -d --build

dev-down:
	@echo "Shutting down dev containers..."
	@docker-compose down 


test:
	@echo "Running tests..."
	@docker-compose exec django-web python manage.py test
	@echo "Tests completed!"

clean:
	@echo "Cleaning up cache files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@rm -rf artifacts/
	@echo "Cleanup done."
