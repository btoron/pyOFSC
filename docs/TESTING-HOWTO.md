# Testing How-To Guide

This guide explains how to run tests efficiently in the pyOFSC project.

## Quick Start

### Running All Tests

```bash
# Run all tests (excludes e2e by default for speed)
uv run pytest tests/

# Run all tests including end-to-end tests
uv run pytest tests/ --include-e2e

# Run all tests with optimal parallelism (recommended)
uv run pytest tests/ --include-e2e -n 8 --dist loadfile
```

### Running Specific Test Categories

```bash
# Unit tests only
uv run pytest tests/unit/

# Model tests only  
uv run pytest tests/models/

# End-to-end tests only
uv run pytest tests/end_to_end/

# Integration tests only
uv run pytest tests/integration/
```

## Performance Optimization

### Fastest Execution Methods

1. **Separate parallel execution** (~12 seconds):
   ```bash
   # Run e2e and unit/model tests in parallel processes
   uv run pytest tests/end_to_end/ -n 8 & uv run pytest tests/unit tests/models -n 8; wait
   ```

2. **Optimized mixed execution** (~26 seconds):
   ```bash
   # All tests with optimized distribution
   uv run pytest tests/ --include-e2e -n 8 --dist loadfile
   
   # Using configuration file
   uv run pytest -c pytest-mixed.ini tests/ --include-e2e -n 8
   ```

3. **Standard mixed execution** (~53 seconds):
   ```bash
   # Default configuration (slower)
   uv run pytest tests/ --include-e2e
   ```

### Parallelism Options

```bash
# Auto-detect optimal workers
uv run pytest tests/

# Specify worker count
uv run pytest tests/ -n 4

# Disable parallel execution
uv run pytest tests/ -n 1
# or
export PYTEST_DISABLE_PARALLEL=true
```

## Test Markers

Tests are categorized using markers:

- `@pytest.mark.unit` - Unit tests (no external dependencies)
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.live` - Live environment tests
- `@pytest.mark.slow` - Slow running tests
- `@pytest.mark.e2e` - End-to-end tests

### Running Tests by Marker

```bash
# Run only unit tests
uv run pytest -m unit

# Run only live tests
uv run pytest -m live

# Run non-slow tests
uv run pytest -m "not slow"
```

## Environment Variables

### Authentication (Required for E2E Tests)

```bash
export OFSC_INSTANCE="your-instance"
export OFSC_CLIENT_ID="your-client-id"
export OFSC_CLIENT_SECRET="your-client-secret"
```

### Test Execution Control

```bash
# Disable parallel execution
export PYTEST_DISABLE_PARALLEL=true

# Set custom worker count
export PYTEST_WORKERS=4

# Enable rate limiting
export PYTEST_RATE_LIMITED=true
```

## Common Test Scenarios

### Development Testing

```bash
# Quick unit test run during development
uv run pytest tests/unit/ -n 8

# Test a specific file
uv run pytest tests/unit/test_auth.py

# Test a specific function
uv run pytest tests/unit/test_auth.py::TestBasicAuth::test_basic_auth_creation

# Run tests with verbose output
uv run pytest tests/unit/ -v

# Run tests and stop on first failure
uv run pytest tests/unit/ -x
```

### Pre-Commit Testing

```bash
# Run all tests before committing
uv run pytest tests/ --include-e2e -n 8 --dist loadfile

# Run with coverage
uv run pytest tests/ --cov=ofsc --cov-report=html
```

### CI/CD Testing

```bash
# Full test suite with performance measurement
uv run pytest tests/ --include-e2e -n 8 --dist loadfile --junit-xml=test-results.xml

# With specific environment
uv run pytest tests/ --env=staging --include-e2e
```

## Debugging Tests

### Useful Options

```bash
# Show print statements
uv run pytest tests/ -s

# Show local variables on failure
uv run pytest tests/ -l

# Drop into debugger on failure
uv run pytest tests/ --pdb

# Run last failed tests
uv run pytest tests/ --lf

# Run failed tests first, then others
uv run pytest tests/ --ff
```

### Test Output

```bash
# Shorter traceback
uv run pytest tests/ --tb=short

# No traceback
uv run pytest tests/ --tb=no

# Full traceback
uv run pytest tests/ --tb=long
```

## Performance Tips

1. **Use `--dist loadfile` for mixed tests**: Groups tests by file for better efficiency
2. **Run categories separately**: Use background processes for true parallelism
3. **Exclude e2e tests during development**: Use `--include-e2e` only when needed
4. **Monitor worker count**: Too many workers can cause contention

## Test Configuration Files

- `pyproject.toml` - Main pytest configuration
- `pytest-mixed.ini` - Optimized configuration for mixed test execution
- `tests/conftest.py` - Shared fixtures and configuration

## Troubleshooting

### Tests Hanging or Timing Out

```bash
# Check with shorter timeout
uv run pytest tests/ --timeout=60

# Disable rate limiting
export PYTEST_RATE_LIMITED=false

# Run sequentially to isolate issue
uv run pytest tests/ -n 1
```

### Authentication Errors

```bash
# Verify credentials are set
echo $OFSC_INSTANCE
echo $OFSC_CLIENT_ID

# Test with basic example
uv run pytest tests/end_to_end/test_auth.py -v
```

### Parallel Execution Issues

```bash
# Disable xdist
export PYTEST_DISABLE_PARALLEL=true

# Check available workers
python -c "import os; print(f'CPU count: {os.cpu_count()}')"

# Use fewer workers
uv run pytest tests/ -n 2
```

## Best Practices

1. **Always run tests before committing**
2. **Use parallel execution for faster feedback**
3. **Keep unit tests fast and isolated**
4. **Mock external dependencies in unit tests**
5. **Use fixtures for common test setup**
6. **Group related tests in the same file**

## See Also

- [Parallel Testing Guide](PARALLEL_TESTING.md) - Advanced parallel testing with custom scripts, rate limiting configuration, and CI/CD integration