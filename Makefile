# AI Tool Intelligence Platform - Development Automation
.PHONY: help install install-dev test test-unit test-integration test-e2e lint format clean start stop restart docs build deploy

# Default target
help: ## Show this help message
	@echo "AI Tool Intelligence Platform - Development Commands"
	@echo "======================================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Installation targets
install: ## Install production dependencies
	@echo "🔧 Installing production dependencies..."
	pip install -r requirements.txt
	cd frontend && npm ci --only=production
	cd tests && npm ci --only=production

install-dev: ## Install development dependencies
	@echo "🔧 Installing development dependencies..."
	pip install -r requirements-dev.txt
	cd frontend && npm ci
	cd tests && npm ci
	npx playwright install --with-deps

setup: ## Complete project setup for new machine
	@echo "🚀 Setting up AI Tool Intelligence Platform..."
	@echo "📋 Follow the complete guide: docs/setup/ONBOARDING_COMPLETE_GUIDE.md"
	@echo ""
	@echo "🔧 Quick setup starting..."
	@echo ""
	@echo "📦 Installing backend dependencies..."
	cd backend && python3 -m venv venv
	cd backend && source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt
	@echo ""
	@echo "⚛️ Installing frontend dependencies..."
	cd frontend && npm install
	@echo ""
	@echo "🧪 Installing test dependencies..."
	cd tests && npm install && npx playwright install --with-deps
	@echo ""
	@echo "📝 Creating environment file..."
	@if [ ! -f .env ]; then cp .env.example .env; fi
	@echo ""
	@echo "✅ Setup complete! Next steps:"
	@echo "1. Edit .env with your AWS credentials"
	@echo "2. Enable Claude 3.5 Sonnet in AWS Bedrock (us-east-1 region)"
	@echo "3. Run 'make start' to launch the platform"
	@echo ""
	@echo "📚 Read the complete guide: docs/setup/ONBOARDING_COMPLETE_GUIDE.md"

# Testing targets
test: ## Run all tests
	@echo "🧪 Running complete test suite..."
	$(MAKE) test-unit
	$(MAKE) test-integration
	$(MAKE) test-e2e

test-unit: ## Run unit tests
	@echo "🧪 Running unit tests..."
	cd backend && python -m pytest tests/ -v -m "unit"

test-integration: ## Run integration tests
	@echo "🧪 Running integration tests..."
	cd backend && python -m pytest tests/ -v -m "integration"

test-e2e: ## Run end-to-end tests
	@echo "🧪 Running E2E tests..."
	cd tests && npx playwright test

test-performance: ## Run performance tests
	@echo "⚡ Running performance tests..."
	cd tests && npx playwright test performance/

test-coverage: ## Run tests with coverage report
	@echo "📊 Running tests with coverage..."
	cd backend && python -m pytest tests/ --cov=src --cov-report=html --cov-report=term

# Code quality targets
lint: ## Run linting on all code
	@echo "🔍 Running linters..."
	cd backend && black --check src/
	cd backend && isort --check-only src/
	cd backend && flake8 src/
	cd backend && mypy src/
	cd frontend && npm run lint

format: ## Format all code
	@echo "✨ Formatting code..."
	cd backend && black src/
	cd backend && isort src/
	cd frontend && npm run format || echo "No format script found"

security: ## Run security checks
	@echo "🛡️ Running security checks..."
	cd backend && bandit -r src/
	cd backend && safety check -r requirements.txt
	cd frontend && npm audit --audit-level=high

# Development targets
start: ## Start development servers
	@echo "🚀 Starting development servers..."
	@echo "📍 Backend: http://localhost:5000"
	@echo "📍 Frontend: http://localhost:3000"
	@echo ""
	@echo "🐍 Starting backend..."
	@cd backend && source venv/bin/activate && python app.py &
	@sleep 3
	@echo "⚛️ Starting frontend..."
	@cd frontend && npm start &
	@echo ""
	@echo "✅ Platform started! Open http://localhost:3000"
	@echo "🔧 To stop: make stop"

start-backend: ## Start backend server only
	@echo "🐍 Starting backend server..."
	cd backend && source venv/bin/activate && python app.py

start-frontend: ## Start frontend server only
	@echo "⚛️ Starting frontend server..."
	cd frontend && npm start

stop: ## Stop all development servers
	@echo "🛑 Stopping servers..."
	pkill -f "python.*main.py" || true
	pkill -f "npm.*start" || true
	pkill -f "react-scripts" || true

restart: ## Restart development servers
	@echo "🔄 Restarting servers..."
	$(MAKE) stop
	sleep 2
	$(MAKE) start

# Database targets
db-migrate: ## Run database migrations
	@echo "📊 Running database migrations..."
	cd backend && python -c "from src.ai_tool_intelligence.models.database import db; db.create_all()"

db-reset: ## Reset database (WARNING: Destroys data)
	@echo "⚠️ Resetting database..."
	cd backend && rm -f instance/ai_tools.db
	$(MAKE) db-migrate

db-seed: ## Seed database with sample data
	@echo "🌱 Seeding database..."
	cd backend && python scripts/development/seed-database.py

# Documentation targets
docs: ## Generate documentation
	@echo "📚 Generating documentation..."
	cd docs && sphinx-build -b html . _build/html

docs-serve: ## Serve documentation locally
	@echo "📖 Serving documentation..."
	cd docs/_build/html && python -m http.server 8080

# Build targets
build: ## Build for production
	@echo "🏗️ Building for production..."
	cd frontend && npm run build
	cd backend && python -m build

build-docker: ## Build Docker images
	@echo "🐳 Building Docker images..."
	docker-compose build

# Deployment targets
deploy-dev: ## Deploy to development environment
	@echo "🚀 Deploying to development..."
	docker-compose -f docker-compose.dev.yml up -d

deploy-prod: ## Deploy to production environment
	@echo "🚀 Deploying to production..."
	docker-compose -f docker-compose.prod.yml up -d

# Utility targets
clean: ## Clean temporary files and caches
	@echo "🧹 Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + || true
	cd frontend && rm -rf node_modules/.cache
	cd tests && rm -rf node_modules/.cache

clean-all: clean ## Clean everything including node_modules
	@echo "🧹 Deep cleaning..."
	cd frontend && rm -rf node_modules
	cd tests && rm -rf node_modules
	cd backend && rm -rf venv

logs: ## Show application logs
	@echo "📋 Showing application logs..."
	tail -f backend/instance/logs/*.log

monitor: ## Monitor system health
	@echo "📊 Monitoring system health..."
	./scripts/monitoring/monitor-system.py

backup: ## Create system backup
	@echo "💾 Creating system backup..."
	./scripts/deployment/backup.sh

# Research and tools
research: ## Run research on specific tool (usage: make research TOOL="Cursor")
	@echo "🔬 Researching tool: $(TOOL)"
	cd backend && python -c "from src.ai_tool_intelligence.core.research.research_tools import research_tool; research_tool('$(TOOL)')"

research-bulk: ## Run bulk research (usage: make research-bulk TOOLS="Cursor,GitHub Copilot")
	@echo "🔬 Running bulk research..."
	./scripts/development/research.sh process "$(TOOLS)"

# Quality assurance
qa: ## Run complete quality assurance pipeline
	@echo "🎯 Running QA pipeline..."
	$(MAKE) lint
	$(MAKE) security
	$(MAKE) test-unit
	$(MAKE) test-integration

ci: ## Run CI pipeline locally
	@echo "🤖 Running CI pipeline..."
	$(MAKE) install-dev
	$(MAKE) qa
	$(MAKE) test-e2e

# Environment management
env-check: ## Check environment configuration
	@echo "🔍 Checking environment..."
	python scripts/development/check-environment.py

env-create: ## Create environment file from template
	@echo "📝 Creating environment file..."
	cp .env.example .env
	@echo "Please edit .env with your configuration"

# Performance
perf: ## Run performance profiling
	@echo "⚡ Running performance profiling..."
	cd backend && python -m cProfile -o profile.stats src/ai_tool_intelligence/main.py

# Development helpers
shell: ## Open Python shell with application context
	@echo "🐍 Opening Python shell..."
	cd backend && python -c "from src.ai_tool_intelligence.main import create_app; app = create_app(); app.app_context().push(); print('Application context loaded')"

deps-update: ## Update dependencies
	@echo "⬆️ Updating dependencies..."
	pip install --upgrade pip
	pip-review --local --auto
	cd frontend && npm update
	cd tests && npm update

deps-audit: ## Audit dependencies for vulnerabilities
	@echo "🔒 Auditing dependencies..."
	pip-audit
	cd frontend && npm audit
	cd tests && npm audit

# Project information
info: ## Show project information
	@echo "📊 AI Tool Intelligence Platform Information"
	@echo "=========================================="
	@echo "Backend: Python Flask API"
	@echo "Frontend: React Application"
	@echo "Testing: Pytest + Playwright"
	@echo "Database: SQLite (dev) / PostgreSQL (prod)"
	@echo "AI: AWS Bedrock + Claude 3.5 Sonnet"
	@echo ""
	@echo "📁 Project Structure:"
	@echo "  backend/src/ai_tool_intelligence/  - Main application code"
	@echo "  frontend/                          - React frontend"
	@echo "  tests/                             - E2E and integration tests"
	@echo "  docs/                              - Documentation"
	@echo "  scripts/                           - Automation scripts"
	@echo ""
	@echo "🔗 Key URLs:"
	@echo "  Frontend: http://localhost:3000"
	@echo "  Backend API: http://localhost:5000"
	@echo "  Documentation: file://$(PWD)/docs/_build/html/index.html"