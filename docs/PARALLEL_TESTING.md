# Parallel Test Execution Guide

This document describes the parallel test execution implementation for pyOFSC, designed to achieve 4x performance improvement while maintaining test reliability and respecting API rate limits.

## Overview

The parallel testing system provides:
- **Conservative approach**: Gradual rollout with fallback mechanisms
- **Rate limiting**: Automatic 429 error handling with exponential backoff
- **Category-specific parallelism**: Optimized worker counts per test type
- **Easy toggle**: Simple enable/disable parallel execution
- **GitHub Actions integration**: CI/CD optimized execution

## Quick Start

### Running Tests in Parallel

```bash
# Run all tests with optimal parallelism
python scripts/run_tests_parallel.py --all

# Run specific test categories
python scripts/run_tests_parallel.py --unit        # Unit tests only
python scripts/run_tests_parallel.py --end-to-end # E2E tests only

# Control parallelism
python scripts/run_tests_parallel.py --unit --workers 8      # Custom worker count
python scripts/run_tests_parallel.py --all --sequential     # Force sequential

# Measure performance
python scripts/run_tests_parallel.py --all --measure
```

### Environment Variables

```bash
# Disable parallel execution entirely
export PYTEST_DISABLE_PARALLEL=true

# Set custom worker count
export PYTEST_WORKERS=4

# Enable rate limiting for live tests
export PYTEST_RATE_LIMITED=true

# Configure rate limiting
export PYTEST_MAX_CONCURRENT_REQUESTS=10
export PYTEST_RATE_LIMIT_DELAY=0.1
export PYTEST_MAX_RETRIES=3
```

## Architecture

### Test Categories and Parallelism

| Category | Worker Count | Rate Limiting | Use Case |
|----------|-------------|---------------|----------|
| Unit Tests | Up to 8 workers | No | CPU-bound, no external deps |
| Model Tests | Up to 8 workers | No | CPU-bound validation |
| Integration | Up to 4 workers | Optional | Mixed dependencies |
| End-to-End | Max 10 workers | Yes | API rate limited |
| Live Tests | Max 10 workers | Yes | Real OFSC instance |

### Rate Limiting System

The rate limiting system provides:

1. **Automatic 429 detection**: Exponential backoff on rate limit errors
2. **Configurable limits**: Max concurrent requests, retry counts, backoff times
3. **Worker coordination**: Global rate limiting across all test workers
4. **Statistics tracking**: Monitor retry rates and performance impact

### Fallback Strategy

The system automatically falls back to sequential execution when:

1. **pytest-xdist unavailable**: Missing dependency detection
2. **Worker startup failures**: Automatic detection and fallback
3. **Explicit override**: Environment variable or command-line flag
4. **Error threshold**: Too many rate limiting errors

## Usage Examples

### Basic Parallel Execution

```bash
# Install dependencies
uv sync --dev

# Run unit tests in parallel
python scripts/run_tests_parallel.py --unit

# Run with performance measurement
python scripts/run_tests_parallel.py --unit --measure
```

### Advanced Configuration

```bash
# Custom configuration for CI/CD
export PYTEST_WORKERS=4
export PYTEST_MAX_CONCURRENT_REQUESTS=5
export PYTEST_RATE_LIMIT_DELAY=0.2

python scripts/run_tests_parallel.py --end-to-end
```

### Performance Measurement

```bash
# Measure baseline performance
python scripts/measure_test_performance.py

# Compare parallel vs sequential
python scripts/run_tests_parallel.py --unit --measure
python scripts/run_tests_parallel.py --unit --sequential --measure
```

## Configuration

### pytest Configuration

The `pyproject.toml` includes parallel-specific configuration:

```toml
[tool.pytest.ini_options]
addopts = "--maxfail=3"
markers = [
    "unit: marks tests as unit tests (no external dependencies)",
    "live: marks tests as live environment tests (requires real OFSC instance)",
    "slow: marks tests as slow running tests"
]

[tool.pytest_env]
PYTEST_DISABLE_PARALLEL = "false"
PYTEST_WORKERS = ""
PYTEST_RATE_LIMITED = "false"
```

### Rate Limiting Configuration

Rate limiting can be configured via environment variables:

```bash
# Maximum concurrent requests across all workers
export PYTEST_MAX_CONCURRENT_REQUESTS=10

# Minimum delay between requests (seconds)
export PYTEST_RATE_LIMIT_DELAY=0.1

# Maximum retry attempts for 429 errors
export PYTEST_MAX_RETRIES=3

# Exponential backoff configuration
export PYTEST_BASE_BACKOFF=1.0
export PYTEST_MAX_BACKOFF=60.0
```

### Test Client Configuration

Tests automatically use rate-limited clients when running in parallel:

```python
# In test fixtures (conftest.py)
@pytest.fixture
def async_client(test_credentials, rate_limiting_enabled):
    if rate_limiting_enabled:
        from ofsc.testing import create_test_client
        return create_test_client(
            instance=test_credentials["instance"],
            client_id=test_credentials["client_id"],
            client_secret=test_credentials["client_secret"]
        )
    else:
        return OFSC(...)  # Standard client
```

## GitHub Actions Integration

The parallel testing system integrates with GitHub Actions:

```yaml
# .github/workflows/test-parallel.yml
- name: Run tests in parallel
  env:
    PYTEST_RATE_LIMITED: "true"
    PYTEST_WORKERS: "4"
  run: |
    python scripts/run_tests_parallel.py --all --workers 4 --measure
```

### Workflow Features

- **Manual dispatch**: Choose test category and parallel/sequential mode
- **Performance tracking**: Automatic performance measurement and reporting
- **Artifact collection**: Test results, performance data, and debug logs
- **Failure handling**: Graceful degradation and detailed reporting

## Performance Expectations

### Expected Improvements

| Test Category | Sequential Time | Parallel Time | Improvement |
|---------------|----------------|---------------|-------------|
| Unit Tests | ~60s | ~15s | 4x faster |
| Model Tests | ~30s | ~8s | 4x faster |
| End-to-End Tests | ~120s | ~40s | 3x faster |
| **Overall** | ~210s | ~63s | **3.3x faster** |

### Rate Limiting Impact

With rate limiting enabled:
- **Retry rate**: <5% of requests
- **Average retry delay**: 1-3 seconds
- **Success rate**: >99% after retries

## Troubleshooting

### Common Issues

1. **"pytest-xdist not available"**
   ```bash
   # Install missing dependency
   uv sync --dev
   ```

2. **Rate limiting errors**
   ```bash
   # Reduce worker count
   export PYTEST_WORKERS=2
   
   # Increase delays
   export PYTEST_RATE_LIMIT_DELAY=0.5
   ```

3. **Worker startup failures**
   ```bash
   # Fall back to sequential
   export PYTEST_DISABLE_PARALLEL=true
   ```

### Debug Information

Enable debug mode for detailed logging:

```bash
# Enable debug mode
export PYTEST_DEBUG=true

# Check rate limiting statistics
python -c "
from ofsc.testing import get_client_factory
factory = get_client_factory()
print(factory.get_config())
"
```

### Performance Issues

If parallel execution is slower than expected:

1. **Check worker count**: Too many workers can cause contention
2. **Monitor rate limiting**: Excessive retries indicate rate limit issues
3. **Validate test isolation**: Shared resources may cause serialization
4. **Review hardware**: Ensure adequate CPU and memory

## Best Practices

### Writing Parallel-Safe Tests

1. **Use monkeypatch**: For environment variable testing
   ```python
   def test_env_vars(monkeypatch):
       monkeypatch.setenv('VAR', 'value')
   ```

2. **Avoid shared state**: Each test should be independent
3. **Use unique identifiers**: Prevent resource conflicts
   ```python
   def test_create_resource(test_prefix):
       resource_name = f"{test_prefix}test_resource"
   ```

4. **Handle rate limiting**: Tests should be tolerant of delays

### Configuration Guidelines

1. **Start conservative**: Begin with lower worker counts
2. **Monitor performance**: Use measurement tools regularly
3. **Adjust for environment**: CI/CD may need different settings
4. **Document overrides**: Track custom configurations

### CI/CD Optimization

1. **Use appropriate worker counts**: Match available CPU cores
2. **Enable rate limiting**: Always for live/E2E tests
3. **Collect artifacts**: Performance data and debug logs
4. **Set timeouts**: Prevent hanging parallel jobs

## Migration Guide

### From Sequential to Parallel

1. **Install dependencies**:
   ```bash
   uv sync --dev
   ```

2. **Run baseline measurement**:
   ```bash
   python scripts/measure_test_performance.py
   ```

3. **Start with unit tests**:
   ```bash
   python scripts/run_tests_parallel.py --unit
   ```

4. **Gradually add categories**:
   ```bash
   python scripts/run_tests_parallel.py --unit --models
   python scripts/run_tests_parallel.py --all
   ```

5. **Update CI/CD**:
   - Replace `pytest` commands with `run_tests_parallel.py`
   - Add environment variables for configuration
   - Enable artifact collection

### Rollback Plan

If issues arise, easily revert to sequential execution:

```bash
# Temporary disable
export PYTEST_DISABLE_PARALLEL=true

# Or use explicit sequential flag
python scripts/run_tests_parallel.py --all --sequential

# Update CI/CD to use standard pytest
uv run pytest tests/ -v
```

## Future Enhancements

Planned improvements:

1. **Adaptive rate limiting**: Automatically adjust based on response times
2. **Smart test distribution**: Group related tests to minimize setup overhead
3. **Advanced metrics**: Detailed performance analysis and reporting
4. **Integration testing**: Enhanced support for complex integration scenarios
5. **Load balancing**: Optimize test distribution across workers