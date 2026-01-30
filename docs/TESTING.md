# Testing Guide for Cyber-AutoAgent

This guide explains how to run tests locally and in different environments.

## Quick Start

### Using Make (Recommended)

```bash
# Install dependencies and setup local environment
make setup-local

# Run all tests
make test

# Run tests with verbose output
make test-verbose

# Run tests with coverage report
make test-coverage

# Run linting
make lint

# Run all CI checks locally
make ci
```

### Using the Test Script

```bash
# Make the script executable (first time only)
chmod +x scripts/run_tests.sh

# Run all tests
./scripts/run_tests.sh

# Run with coverage
COVERAGE=true ./scripts/run_tests.sh

# Run with verbose output
VERBOSE=true ./scripts/run_tests.sh

# Run specific tests
TEST_PATH=tests/test_config.py ./scripts/run_tests.sh
```

### Using pytest Directly

```bash
# Set up environment variables
export PYTHONPATH="${PWD}/src:${PYTHONPATH}"
export LITELLM_MODE="PRODUCTION"

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_config.py -v

# Run with coverage
pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html

# Run tests matching a pattern
pytest tests/ -v -k "test_config"
```

## Environment-Specific Testing

### Local Environment

```bash
# Install dependencies
pip install pytest pytest-mock pytest-cov

# Install project in editable mode
pip install -e .

# Run tests
make test
```

### Docker Environment

```bash
# Build the Docker image
docker build -t cyber-autoagent .

# Run tests in Docker
docker run --rm cyber-autoagent pytest tests/ -v

# Or mount the source and run tests
docker run --rm -v $(pwd):/app cyber-autoagent bash -c "pip install -e . && pytest tests/ -v"
```

### CI Environment

Tests run automatically in GitHub Actions on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Manual workflow dispatch

See `.github/workflows/test.yml` for the CI configuration.

## Test Structure

```
tests/
├── conftest.py                      # Shared fixtures and configuration
├── test_config.py                   # Configuration tests
├── test_environment.py              # Environment setup tests
├── test_handlers_base.py            # Handler base class tests
├── test_prompts_factory.py          # Prompt factory tests
├── test_evaluation_manager.py       # Evaluation manager tests
└── ... (other test files)
```

## Writing Tests

### Basic Test Example

```python
#!/usr/bin/env python3
"""
Tests for the modules/example module.
"""
import pytest
from modules.example import example_function

class TestExampleFunction:
    """Test example_function."""

    def test_basic_functionality(self):
        """Test basic functionality."""
        result = example_function("input")
        assert result == "expected_output"

    def test_error_handling(self):
        """Test error handling."""
        with pytest.raises(ValueError):
            example_function(None)
```

### Using Fixtures

```python
def test_with_temp_dir(temp_data_dir):
    """Test using the temp_data_dir fixture from conftest.py."""
    test_file = os.path.join(temp_data_dir, "test.txt")
    with open(test_file, "w") as f:
        f.write("test content")
    
    assert os.path.exists(test_file)
```

### Mocking External Dependencies

```python
from unittest.mock import Mock, patch

def test_with_mock():
    """Test with mocked dependencies."""
    with patch("modules.example.external_function") as mock_func:
        mock_func.return_value = "mocked_value"
        
        result = example_function()
        
        assert result == "mocked_value"
        mock_func.assert_called_once()
```

## Test Configuration

### Environment Variables

The following environment variables are set automatically for tests:

- `LITELLM_MODE=PRODUCTION` - Prevents loading .env files during tests
- `PYTHONPATH` - Includes `src` directory for imports

### Pytest Configuration

Pytest is configured in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
pythonpath = ["src"]
```

## Coverage Reports

### Generate Coverage Report

```bash
# Run tests with coverage
make test-coverage

# View HTML report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Coverage Targets

- Aim for >80% overall code coverage
- Critical modules should have >90% coverage
- New code should include tests

## Common Issues and Solutions

### Import Errors

If you get import errors:

```bash
# Ensure PYTHONPATH is set correctly
export PYTHONPATH="${PWD}/src:${PYTHONPATH}"

# Or install the package in editable mode
pip install -e .
```

### Missing Dependencies

```bash
# Install test dependencies
pip install pytest pytest-mock pytest-cov

# Or install all dev dependencies
pip install -e .[dev]
```

### Permission Errors on Scripts

```bash
# Make scripts executable
chmod +x scripts/run_tests.sh
```

## Continuous Integration

### GitHub Actions Workflows

1. **test.yml** - Basic test workflow
   - Runs on: Push, PR, manual dispatch
   - Python version: 3.11
   - Tests all modules

2. **ci.yml** - Comprehensive CI workflow
   - Runs on: Push to main/develop, PRs
   - Python versions: 3.10, 3.11, 3.12
   - Includes linting and test coverage

3. **pr-checks.yml** - PR quality checks
   - Runs on: Pull requests
   - Enforces pylint score ≥9.5
   - Comments results on PR

### Running CI Checks Locally

```bash
# Run the same checks as CI
make ci

# Or run individual checks
make lint
make test
```

## Test Categories

### Unit Tests
- Test individual functions and classes
- Mock external dependencies
- Fast execution

### Integration Tests
- Test interactions between components
- May use real dependencies
- Slower execution

### Environment Tests
- Test environment-specific behavior
- Docker, local, CI configurations

## Best Practices

1. **Write tests first** (TDD approach recommended)
2. **Keep tests independent** - Tests should not depend on each other
3. **Use descriptive names** - Test names should describe what they test
4. **Test edge cases** - Include boundary conditions and error cases
5. **Mock external services** - Keep tests fast and reliable
6. **Update tests with code** - Keep tests in sync with implementation
7. **Aim for high coverage** - But focus on meaningful tests, not just coverage numbers

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-mock Documentation](https://pytest-mock.readthedocs.io/)
- [Python unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [Coverage.py](https://coverage.readthedocs.io/)
