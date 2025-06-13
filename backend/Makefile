# Makefile - Easy commands for testing and development

.PHONY: help install test test-unit test-integration test-api test-all lint type-check security quality clean coverage report ci

# Default target
help:
	@echo "AI Tool Intelligence Platform - Development Commands"
	@echo "=================================================="
	@echo ""
	@echo "Setup Commands:"
	@echo "  install          Install all dependencies including test dependencies"
	@echo "  install-dev      Install development dependencies only"
	@echo ""
	@echo "Testing Commands:"
	@echo "  test             Run default unit tests"
	@echo "  test-unit        Run unit tests only"
	@echo "  test-integration Run integration tests"
	@echo "  test-api         Run API tests"
	@echo "  test-all         Run all tests"
	@echo "  test-fast        Run fast tests only (no slow tests)"
	@echo ""
	@echo "Quality Commands:"
	@echo "  lint             Run code linting (flake8)"
	@echo "  format           Auto-format code (black + isort)"
	@echo "  type-check       Run type checking (mypy)"
	@echo "  security         Run security checks (bandit)"
	@echo "  quality          Run all quality checks"
	@echo ""
	@echo "Coverage Commands:"
	@echo "  coverage         Generate coverage report"
	@echo "  coverage-html    Generate HTML coverage report"
	@echo "  coverage-serve   Serve HTML coverage report"
	@echo ""
	@echo "Utility Commands:"
	@echo "  clean            Clean up generated files"
	@echo "  report           Generate comprehensive test report"
	@echo "  ci               Run full CI pipeline locally"
	@echo "  benchmark        Run performance benchmarks"
	@echo ""

# Installation
install:
	pip install -r requirements.txt
	pip install -r requirements-test.txt

install-dev:
	pip install -r requirements-test.txt

# Testing
test:
	python run_tests.py --unit --verbose

test-unit:
	python -m pytest tests/ -v -m "unit" --tb=short

test-integration:
	python -m pytest tests/ -v -m "integration" --tb=short

test-api:
	python -m pytest tests/ -v -m "api" --tb=short

test-all:
	python -m pytest tests/ -v --tb=short

test-fast:
	python -m pytest tests/ -v -m "not slow" --tb=short

test-slow:
	python -m pytest tests/ -v -m "slow" --tb=short

# Quality checks
lint:
	flake8 --max-line-length=100 --exclude=tests/ .

format:
	black .
	isort .

format-check:
	black --check --diff .
	isort --check-only --diff .

type-check:
	mypy --ignore-missing-imports .

security:
	bandit -r . -x tests/

quality: lint format-check type-check security

# Coverage
coverage:
	python -m pytest tests/ --cov=. --cov-report=term-missing

coverage-html:
	python -m pytest tests/ --cov=. --cov-report=html
	@echo "Coverage report generated at htmlcov/index.html"

coverage-serve: coverage-html
	python -m http.server 8000 -d htmlcov
	@echo "Coverage report available at http://localhost:8000"

# Utilities
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf bandit-report.json
	rm -rf test_report.txt
	rm -rf .mypy_cache

report:
	python run_tests.py --report

ci:
	python run_tests.py --ci

benchmark:
	python -m pytest tests/ -v -m "slow" --benchmark-only

# Development server (if applicable)
serve:
	python app.py

# Docker commands
docker-build:
	docker build -t ai-tool-intelligence .

docker-test:
	docker build -f Dockerfile.test -t ai-tool-intelligence-test .
	docker run --rm ai-tool-intelligence-test

# Environment setup
setup-env:
	@if [ ! -f .env ]; then \
		cp ../.env.example .env; \
		echo "Created .env file from template"; \
		echo "Please edit .env and add your API keys"; \
	else \
		echo ".env file already exists"; \
	fi

# Quick development setup
setup: install setup-env
	@echo "Development environment setup complete!"
	@echo "Run 'make test' to verify everything works"

# Git hooks
install-hooks:
	@echo "Installing git hooks..."
	@echo '#!/bin/sh' > .git/hooks/pre-commit
	@echo 'make quality' >> .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit
	@echo "Git hooks installed"

# Help for specific test categories
test-help:
	@echo "Test Categories:"
	@echo "==============="
	@echo ""
	@echo "unit: Fast tests with no external dependencies"
	@echo "  - Configuration tests"
	@echo "  - Web scraper tests (mocked)"
	@echo "  - Tool logic tests (mocked)"
	@echo ""
	@echo "integration: Tests that may require external services"
	@echo "  - End-to-end tool workflows"
	@echo "  - Multi-component interactions"
	@echo ""
	@echo "api: Tests requiring actual API access"
	@echo "  - GitHub API integration"
	@echo "  - Firecrawl API integration"
	@echo "  - Free API services"
	@echo ""
	@echo "slow: Performance and stress tests"
	@echo "  - Large dataset processing"
	@echo "  - Performance benchmarks"
	@echo ""
	@echo "network: Tests requiring network connectivity"
	@echo "  - Web scraping tests"
	@echo "  - External service connectivity"

# Environment validation
validate-env:
	@echo "Validating environment..."
	python -c "from config.free_apis_config import FreeAPIConfig; print('Available APIs:', FreeAPIConfig.validate_config())"

# Database setup (if needed)
setup-db:
	python -c "from app import db; db.create_all(); print('Database tables created')"

# Full reset
reset: clean setup-db
	@echo "Environment reset complete"

# Performance monitoring
monitor:
	python -c "
	import psutil
	import time
	from enhanced_strands_agent import EnhancedStrandsAgentService
	
	print('Monitoring system performance...')
	print('CPU Usage:', psutil.cpu_percent(interval=1))
	print('Memory Usage:', psutil.virtual_memory().percent)
	
	service = EnhancedStrandsAgentService()
	status = service.get_service_status()
	print('Service Status:', status['capabilities'])
	"