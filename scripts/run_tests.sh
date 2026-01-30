#!/bin/bash
# Local test runner script for Cyber-AutoAgent
# Supports multiple environments: local, Docker, CI

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT="${TEST_ENV:-local}"
VERBOSE="${VERBOSE:-false}"
COVERAGE="${COVERAGE:-false}"
TEST_PATH="${TEST_PATH:-tests/}"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Cyber-AutoAgent Test Runner${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Function to print status
print_status() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Set environment variables for testing
export LITELLM_MODE="PRODUCTION"
export PYTHONPATH="${PWD}/src:${PYTHONPATH}"

# Detect environment
if [ "$ENVIRONMENT" == "auto" ]; then
    if [ -f "/.dockerenv" ] || [ -d "/app" ]; then
        ENVIRONMENT="docker"
    else
        ENVIRONMENT="local"
    fi
fi

print_status "Running tests in '$ENVIRONMENT' environment"
print_status "Python path: $PYTHONPATH"

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    if ! python -m pytest --version &> /dev/null; then
        print_error "pytest is not installed!"
        echo ""
        echo "To install pytest, run one of the following:"
        echo "  pip install pytest pytest-mock"
        echo "  uv add --dev pytest pytest-mock"
        echo "  pip install -e .[dev]"
        exit 1
    fi
    PYTEST_CMD="python -m pytest"
else
    PYTEST_CMD="pytest"
fi

# Build pytest command
PYTEST_ARGS="-v"

if [ "$VERBOSE" == "true" ]; then
    PYTEST_ARGS="$PYTEST_ARGS -vv"
fi

if [ "$COVERAGE" == "true" ]; then
    PYTEST_ARGS="$PYTEST_ARGS --cov=src --cov-report=term-missing --cov-report=html"
    print_status "Coverage reporting enabled"
fi

# Add any additional pytest arguments passed to the script
PYTEST_ARGS="$PYTEST_ARGS $@"

print_status "Test command: $PYTEST_CMD $TEST_PATH $PYTEST_ARGS"
echo ""

# Run tests
$PYTEST_CMD $TEST_PATH $PYTEST_ARGS

TEST_EXIT_CODE=$?

echo ""
if [ $TEST_EXIT_CODE -eq 0 ]; then
    print_success "All tests passed!"
    
    if [ "$COVERAGE" == "true" ]; then
        echo ""
        print_status "Coverage report generated in htmlcov/index.html"
    fi
else
    print_error "Tests failed with exit code $TEST_EXIT_CODE"
fi

exit $TEST_EXIT_CODE
