# ─────────────────────────────────────────────────────────────────────────────
# Makefile — Developer shortcuts
# Usage: make <target>
# ─────────────────────────────────────────────────────────────────────────────

.PHONY: help install run shell migrate test coverage lint clean docker-up docker-down

# Default target
help:
	@echo ""
	@echo "  Flask Template — Available Commands"
	@echo "  ─────────────────────────────────────"
	@echo "  make install       Install Python dependencies"
	@echo "  make run           Start the Flask development server"
	@echo "  make shell         Open Flask shell"
	@echo "  make migrate       Run database migrations"
	@echo "  make test          Run test suite"
	@echo "  make coverage      Run tests with coverage report"
	@echo "  make lint          Run flake8 linter"
	@echo "  make clean         Remove .pyc files and caches"
	@echo "  make docker-up     Start all services with Docker Compose"
	@echo "  make docker-down   Stop Docker Compose services"
	@echo ""

install:
	pip install -r requirements.txt

run:
	FLASK_ENV=development flask run --debug

shell:
	flask shell

migrate:
	flask db upgrade

migrate-init:
	flask db init

migrate-gen:
	flask db migrate -m "$(msg)"

test:
	FLASK_ENV=testing pytest tests/ -v

coverage:
	FLASK_ENV=testing coverage run -m pytest tests/ -v
	coverage report -m
	coverage html
	@echo "\nHTML report: htmlcov/index.html"

lint:
	flake8 app/ tests/ --max-line-length=100 --exclude=migrations/

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -name ".coverage" -delete

docker-up:
	docker-compose up --build

docker-down:
	docker-compose down
