.PHONY: install run test lint format clean docker-build docker-up docker-down

# Default target
all: install

# Install dependencies
install:
	poetry install

# Run the application
run:
	poetry run uvicorn app.main:app --reload

# Run tests
test:
	poetry run pytest

# Run linting
lint:
	poetry run flake8 app tests

# Format code
format:
	poetry run black app tests

# Clean up
clean:
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info



# Docker commands
docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

# Help
help:
	@echo "Available targets:"
	@echo "  install      Install dependencies"
	@echo "  run          Run the application"
	@echo "  test         Run tests"
	@echo "  lint         Run linting"
	@echo "  format       Format code"
	@echo "  clean        Clean up generated files"
	@echo "  docker-build Build Docker containers"
	@echo "  docker-up    Start Docker containers"
	@echo "  docker-down  Stop Docker containers"
	@echo "  help         Show this help message" 