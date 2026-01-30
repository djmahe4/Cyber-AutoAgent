.PHONY: help test test-verbose test-coverage lint install dev-install clean

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "Cyber-AutoAgent - Development Commands"
	@echo "======================================="
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies using pip
	pip install -e .

dev-install: ## Install development dependencies
	pip install -e .[dev]
	pip install pytest pytest-mock pytest-cov pylint

uv-install: ## Install dependencies using uv
	uv sync
	uv add --dev pytest pytest-mock pytest-cov pylint

test: ## Run tests
	@bash scripts/run_tests.sh

test-verbose: ## Run tests with verbose output
	@VERBOSE=true bash scripts/run_tests.sh

test-coverage: ## Run tests with coverage report
	@COVERAGE=true bash scripts/run_tests.sh

test-single: ## Run a single test file (usage: make test-single TEST_FILE=test_config.py)
	@export PYTHONPATH="${PWD}/src:${PYTHONPATH}" && \
	export LITELLM_MODE="PRODUCTION" && \
	pytest tests/$(TEST_FILE) -v

test-watch: ## Run tests in watch mode (requires pytest-watch)
	@export PYTHONPATH="${PWD}/src:${PYTHONPATH}" && \
	export LITELLM_MODE="PRODUCTION" && \
	ptw tests/ -- -v

lint: ## Run linting with pylint
	@export PYTHONPATH="${PWD}/src:${PYTHONPATH}" && \
	pylint src/ --fail-under=9.5

lint-report: ## Run linting and show detailed report
	@export PYTHONPATH="${PWD}/src:${PYTHONPATH}" && \
	pylint src/ --exit-zero --score=y

format-check: ## Check code formatting with black
	black --check src/ tests/

format: ## Format code with black
	black src/ tests/

clean: ## Clean up generated files
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

check-all: lint test ## Run linting and tests

ci: ## Run CI checks locally (linting + tests)
	@echo "Running CI checks locally..."
	@make lint
	@make test

setup-local: dev-install ## Setup local development environment
	@echo "Local development environment setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Run 'make test' to run tests"
	@echo "  2. Run 'make lint' to check code quality"
	@echo "  3. Run 'make help' to see all available commands"
