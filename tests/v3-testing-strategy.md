# OFSC Python Wrapper v3.0 Complete Testing Guide

## Overview

The v3.0 testing strategy implements a multi-layered approach to ensure reliability, correctness, and maintainability of the OFSC Python Wrapper. The strategy includes four distinct test types: model validation tests, unit tests, end-to-end tests, and live tests.

## Test Types

### 1. Model Validation Tests
Tests that validate Pydantic models against stored API responses to ensure model correctness.

- **Location**: `tests/models/`
- **Purpose**: Validate that all Pydantic models correctly parse real API responses
- **Data Source**: JSON files in `response_examples/` directory
- **Execution**: Automatic discovery and validation of all response examples

### 2. Mock Tests
Unit tests using mocked HTTP responses for isolated testing.

- **Location**: `tests/unit/`
- **Purpose**: Test client logic without external dependencies
- **Tool**: `respx` for httpx mocking
- **Coverage**: All API methods and error scenarios

### 3. End-to-End Tests
Integration tests that may require external dependencies or simulate complex workflows.

- **Location**: `tests/end_to_end/`
- **Purpose**: Test complete workflows and integration scenarios
- **Configuration**: Environment variables and `.env` files
- **Features**: Comprehensive workflow testing

### 4. Live Tests
Tests against real OFSC test environments.

- **Location**: `tests/live/`
- **Purpose**: Validate actual API integration
- **Marker**: `@pytest.mark.live`
- **Isolation**: Unique prefixes for test data

## Test Configuration

### Test Configuration Structure

#### Environment Variables and .env Files

Test configuration uses environment variables with optional `.env` file support for local development:

```bash
# Required for live and end-to-end tests
OFSC_INSTANCE="your_instance"
OFSC_CLIENT_ID="your_client_id"
OFSC_CLIENT_SECRET="your_client_secret"

# Optional test-specific settings
PYTEST_DISABLE_PARALLEL="false"
PYTEST_WORKERS=""
PYTEST_RATE_LIMITED="false"
```

### Configuration Precedence

1. Environment variables (highest priority)
2. .env file (if present)
3. Default values (lowest priority)

Environment variables use standard OFSC naming: `OFSC_INSTANCE`, `OFSC_CLIENT_ID`, `OFSC_CLIENT_SECRET`

## Test Organization

### Directory Structure

```
tests/
├── conftest.py              # Shared fixtures
├── data/                    # Test data files
├── fixtures/                # Test fixtures and registry
│   └── endpoints_registry.py
├── models/                  # Model validation tests
│   ├── test_core_models.py
│   ├── test_metadata_models.py
│   ├── test_capacity_models.py
│   └── test_all_response_examples.py
├── unit/                    # Unit tests with mocked responses
│   ├── test_core_api_simple.py
│   ├── test_auth.py
│   └── test_exceptions.py
├── end_to_end/             # End-to-end workflow tests
│   └── test_sunrise_metadata_*.py
├── integration/            # Integration tests
│   ├── test_properties_demo.py
│   └── test_users_comprehensive.py
├── live/                   # Live environment tests
│   └── test_auth_live.py
├── utils/                  # Test utilities
│   ├── base_test.py
│   ├── test_generator.py
│   ├── response_loader.py
│   └── factories.py
└── v3-testing-strategy.md  # This strategy document
```

## Test Implementation Details

### Model Validation Tests

```python
# tests/models/test_core_models.py
import json
from pathlib import Path
import pytest
from ofsc.models.core import Activity, Resource, User

class TestCoreModels:
    @pytest.fixture
    def response_examples_path(self):
        return Path(__file__).parent.parent.parent / "response_examples"
    
    def test_activity_model_validation(self, response_examples_path):
        """Automatically validate all activity response examples."""
        for example_file in response_examples_path.glob("*activity*.json"):
            with open(example_file) as f:
                data = json.load(f)
            
            # Skip metadata
            if "_metadata" in data:
                del data["_metadata"]
            
            # Validate model parsing
            if "items" in data:
                for item in data["items"]:
                    activity = Activity(**item)
                    assert activity.activity_id is not None
```

### Mock Tests with respx

```python
# tests/unit/test_core_api.py
import pytest
import respx
from httpx import Response
from ofsc import AsyncOFSC

@pytest.mark.asyncio
class TestCoreAPIMocked:
    @respx.mock
    async def test_get_activity(self):
        # Mock the API response
        route = respx.get("https://demo.ofsc.example.com/rest/ofscCore/v1/activities/123")
        route.mock(return_value=Response(200, json={
            "activityId": "123",
            "status": "complete"
        }))
        
        async with AsyncOFSC(instance="demo", client_id="test_id", client_secret="test_secret") as client:
            activity = await client.core.get_activity("123")
            assert activity.activity_id == "123"
            assert activity.status == "complete"
```

### End-to-End Tests

```python
# tests/end_to_end/test_auth_e2e.py
import pytest
from ofsc import OFSC

@pytest.mark.asyncio
class TestAuthEndToEnd:
    async def test_oauth2_token_flow(self, test_credentials):
        """Test complete OAuth2 authentication flow."""
        client = OFSC(
            instance=test_credentials["instance"],
            client_id=test_credentials["client_id"],
            client_secret=test_credentials["client_secret"]
        )
        
        # Test token acquisition and API call
        async with client:
            # This should authenticate and make a real API call
            response = await client.core.get_users()
            assert response is not None
```

### Live Environment Tests

```python
# tests/live/test_core_live.py
import pytest
import uuid

@pytest.mark.live
@pytest.mark.asyncio
class TestCoreAPILive:
    @pytest.fixture
    def test_prefix(self):
        """Generate unique prefix for test isolation."""
        return f"PYTEST_{uuid.uuid4().hex[:8]}_"
    
    async def test_create_and_delete_activity(self, live_client, test_prefix):
        """Test activity creation and deletion in live environment."""
        activity_data = CreateActivityRequest(
            activity_id=f"{test_prefix}ACT001",
            activity_type="install",
            customer_number=f"{test_prefix}CUST001"
        )
        
        # Create activity
        activity = await live_client.core.create_activity(activity_data)
        assert activity.activity_id == activity_data.activity_id
        
        # Cleanup handled externally
        # Activity will be deleted by cleanup job using test_prefix
```

## Test Fixtures

### Shared Client Fixtures

```python
# tests/conftest.py
import pytest
from ofsc import AsyncOFSC, OFSC
from ofsc.auth import BasicAuth
from tests.config import load_test_config

@pytest.fixture
def test_config():
    """Load test configuration with precedence."""
    return load_test_config()

@pytest.fixture
async def async_client(test_config, request):
    """Provide async client for both sync and async tests."""
    env = request.param if hasattr(request, 'param') else 'dev'
    config = test_config.environments[env]
    
    async with AsyncOFSC(
        instance=config.instance,
        client_id=config.client_id,
        client_secret=config.client_secret
    ) as client:
        yield client

@pytest.fixture
def sync_client(test_config, request):
    """Provide sync client."""
    env = request.param if hasattr(request, 'param') else 'dev'
    config = test_config.environments[env]
    
    with OFSC(
        instance=config.instance,
        client_id=config.client_id,
        client_secret=config.client_secret
    ) as client:
        yield client
```

### Demo Data Management

```python
# tests/fixtures/demo_data.py
from typing import Dict, Any
import json
from pathlib import Path

class DemoDataManager:
    """Manage version-aware demo data for tests."""
    
    def __init__(self, version: str = "latest"):
        self.version = version
        self.data_path = Path(__file__).parent / "demo_data"
    
    def get_activity(self, activity_type: str = "default") -> Dict[str, Any]:
        """Get demo activity data adjusted for API version."""
        base_data = self._load_base_data("activity.json")
        
        # Apply version-specific adjustments
        if self.version >= "24.0":
            base_data["newField"] = "value"
        
        if activity_type != "default":
            base_data["activityType"] = activity_type
            
        return base_data
    
    def get_resource(self, resource_type: str = "default") -> Dict[str, Any]:
        """Get demo resource data adjusted for API version."""
        base_data = self._load_base_data("resource.json")
        
        # Version adjustments
        if self.version < "23.0":
            base_data.pop("modernField", None)
            
        return base_data
    
    def _load_base_data(self, filename: str) -> Dict[str, Any]:
        """Load base demo data from file."""
        with open(self.data_path / filename) as f:
            return json.load(f)

# Fixture
@pytest.fixture
def demo_data(test_config):
    """Provide version-aware demo data."""
    return DemoDataManager(test_config.api_version)
```

## Parallel Test Execution

The v3.0 testing strategy includes sophisticated parallel execution capabilities designed to achieve significant performance improvements while maintaining test reliability and API rate limit compliance.

### Performance Benefits

| Test Category | Sequential Time | Parallel Time | Improvement |
|---------------|----------------|---------------|-------------|
| Unit Tests | ~60s | ~15s | 4x faster |
| Model Tests | ~30s | ~8s | 4x faster |
| End-to-End Tests | ~120s | ~120s | No change (sequential for reliability) |
| **Overall** | ~210s | ~143s | **1.5x faster** |

### Category-Specific Parallelism

| Category | Worker Count | Rate Limiting | Use Case |
|----------|-------------|---------------|----------|
| Unit Tests | Up to 8 workers | No | CPU-bound, no external deps |
| Model Tests | Up to 8 workers | No | CPU-bound validation |
| Integration | Up to 4 workers | Optional | Mixed dependencies |
| End-to-End | Sequential (1 worker) | Yes | API rate limited |
| Live Tests | Sequential (1 worker) | Yes | Real OFSC instance, avoid concurrent auth issues |

### Parallel Execution Tools

#### Advanced Parallel Test Runner

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

#### Environment Variable Controls

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

### Rate Limiting System

The parallel testing system includes intelligent rate limiting to ensure API compliance:

1. **Automatic 429 detection**: Exponential backoff on rate limit errors
2. **Configurable limits**: Max concurrent requests, retry counts, backoff times  
3. **Worker coordination**: Global rate limiting across all test workers
4. **Statistics tracking**: Monitor retry rates and performance impact

Expected rate limiting performance:
- **Retry rate**: <5% of requests
- **Average retry delay**: 1-3 seconds
- **Success rate**: >99% after retries

## Test Execution

### Standard Test Execution

```bash
# Run only model validation tests
uv run pytest tests/models/

# Run only unit tests
uv run pytest tests/unit/

# Run only end-to-end tests
uv run pytest tests/end_to_end/

# Run only live tests
uv run pytest tests/live/ -m live

# Run all tests except live
uv run pytest -m "not live"

# Run with coverage report
uv run pytest --cov=ofsc --cov-report=html
```

### Optimized Parallel Execution

```bash
# Fastest execution methods
uv run pytest tests/end_to_end/ -n 8 & uv run pytest tests/unit tests/models -n 8; wait

# Optimized mixed execution
uv run pytest tests/ --include-e2e -n 8 --dist loadfile

# Using parallel test runner (recommended)
python scripts/run_tests_parallel.py --all --measure
```

### Performance Measurement

```bash
# Measure baseline performance
python scripts/measure_test_performance.py

# Compare parallel vs sequential
python scripts/run_tests_parallel.py --unit --measure
python scripts/run_tests_parallel.py --unit --sequential --measure
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
# Run all tests before committing (recommended)
python scripts/run_tests_parallel.py --all --measure

# Run with coverage
uv run pytest tests/ --cov=ofsc --cov-report=html

# Quick validation (unit + model tests only)
uv run pytest tests/unit tests/models -n 8
```

### CI/CD Testing

```bash
# Full test suite with performance measurement
python scripts/run_tests_parallel.py --all --measure --workers 4

# With specific environment variables
PYTEST_RATE_LIMITED=true python scripts/run_tests_parallel.py --live

# Generate test results for CI reporting
uv run pytest tests/ --junit-xml=test-results.xml --cov-report=xml
```

## Debugging and Troubleshooting

### Debugging Test Failures

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

### Test Output Control

```bash
# Shorter traceback
uv run pytest tests/ --tb=short

# No traceback
uv run pytest tests/ --tb=no

# Full traceback
uv run pytest tests/ --tb=long
```

### Common Issues and Solutions

#### Tests Hanging or Timing Out

```bash
# Check with shorter timeout
uv run pytest tests/ --timeout=60

# Disable rate limiting
export PYTEST_RATE_LIMITED=false

# Run sequentially to isolate issue
uv run pytest tests/ -n 1
```

#### Authentication Errors

```bash
# Verify credentials are set
echo $OFSC_INSTANCE
echo $OFSC_CLIENT_ID

# Test with basic example
uv run pytest tests/live/test_auth_live.py -v
```

#### Parallel Execution Issues

```bash
# Disable parallel execution
export PYTEST_DISABLE_PARALLEL=true

# Check available workers
python -c "import os; print(f'CPU count: {os.cpu_count()}')"

# Use fewer workers
uv run pytest tests/ -n 2
```

### Performance Tips

1. **Use `--dist loadfile` for mixed tests**: Groups tests by file for better efficiency
2. **Run categories separately**: Use background processes for true parallelism
3. **Exclude live tests during development**: Use `-m "not live"` for faster feedback
4. **Monitor worker count**: Too many workers can cause contention

## Best Practices

### Writing Effective Tests

1. **Keep unit tests fast and isolated**: No external dependencies, use mocks
2. **Use descriptive test names**: Clearly indicate what is being tested
3. **Follow the AAA pattern**: Arrange, Act, Assert
4. **Use fixtures for common setup**: Share setup code efficiently
5. **Group related tests**: Keep tests for the same functionality together

### Test Organization

1. **Use appropriate markers**: Ensure tests are properly categorized
2. **Inherit from BaseOFSCTest**: Get automatic cleanup and performance tracking
3. **Use unique test data**: Avoid conflicts with parallel execution
4. **Clean up resources**: Always clean up test data, even on failure

### Generated Test Guidelines

1. **Review generated tests**: Understand what each test does before running
2. **Customize as needed**: Generated tests are templates, not final implementations
3. **Add specific validations**: Enhance with business logic specific tests
4. **Update when APIs change**: Regenerate tests when endpoints are modified

## Migration to Parallel Testing

### Adopting Parallel Execution

If you're migrating from sequential test execution, follow this gradual approach:

#### Step 1: Install Dependencies
```bash
# Ensure parallel testing dependencies are available
uv sync --dev
```

#### Step 2: Baseline Measurement
```bash
# Measure current sequential performance
python scripts/measure_test_performance.py
```

#### Step 3: Gradual Rollout
```bash
# Start with unit tests only
python scripts/run_tests_parallel.py --unit

# Add model tests
python scripts/run_tests_parallel.py --unit --models

# Full parallel execution
python scripts/run_tests_parallel.py --all
```

#### Step 4: Update CI/CD
Replace existing pytest commands with parallel test runner:

```yaml
# Before (sequential)
- run: uv run pytest tests/ -v

# After (parallel)  
- run: python scripts/run_tests_parallel.py --all --workers 4 --measure
```

### Rollback Plan

If parallel execution causes issues, easily revert:

```bash
# Temporary disable
export PYTEST_DISABLE_PARALLEL=true

# Or use explicit sequential flag
python scripts/run_tests_parallel.py --all --sequential

# Standard pytest fallback
uv run pytest tests/ -v
```

### Writing Parallel-Safe Tests

When writing new tests, ensure they work well with parallel execution:

#### Use Unique Identifiers
```python
def test_create_resource(self):
    # Good: Unique identifier prevents conflicts
    resource_name = f"{self.generate_unique_label('test')}resource"
    
    # Bad: Fixed name causes conflicts in parallel execution
    resource_name = "test_resource"
```

#### Avoid Shared State
```python
def test_with_environment_variable(self, monkeypatch):
    # Good: Use monkeypatch for environment variables
    monkeypatch.setenv('TEST_VAR', 'value')
    
    # Bad: Global environment modification affects other tests
    os.environ['TEST_VAR'] = 'value'
```

#### Handle Rate Limiting
```python
async def test_api_endpoint(self):
    # Good: Use BaseOFSCTest rate limiting
    async with self.track_performance('api_call'):
        response = await self.rate_limited_call(self.client.get_resource, 'id')
        
    # Bad: Direct API calls without rate limiting
    response = await self.client.get_resource('id')
```

### Async Test Handling

```python
# tests/conftest.py
import asyncio
import pytest

@pytest.fixture
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

class TestBothClients:
    """Test both sync and async clients with same logic."""
    
    @pytest.mark.parametrize("client_type", ["sync", "async"])
    async def test_get_activity(self, client_type, sync_client, async_client):
        if client_type == "sync":
            activity = sync_client.core.get_activity("123")
        else:
            activity = await async_client.core.get_activity("123")
        
        assert activity.activity_id == "123"
```

## Automated Test Generation System

The v3.0 testing strategy includes a sophisticated automated test generation system that creates comprehensive test suites directly from the OFSC API swagger specification.

### Endpoint Registry

The foundation of the test generation system is a comprehensive endpoint registry generated from swagger.json:

```python
# Generated: tests/fixtures/endpoints_registry.py
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

@dataclass
class EndpointParameter:
    name: str
    type: str
    required: bool
    location: str  # 'path', 'query', 'header', 'body'
    constraints: Optional[Dict[str, Any]] = None

@dataclass  
class EndpointInfo:
    id: int
    path: str
    method: str
    module: str  # 'core', 'metadata', 'capacity'
    summary: str
    parameters: List[EndpointParameter]
    request_schema: Optional[str] = None
    response_schema: Optional[str] = None
    rate_limit: Optional[Dict[str, Any]] = None

# Registry contains all 242 OFSC API endpoints
ENDPOINTS: List[EndpointInfo] = [
    EndpointInfo(
        id=1,
        path='/rest/ofscMetadata/v1/activityTypeGroups',
        method='GET',
        module='metadata',
        summary='Get activity type groups',
        parameters=[...],
    ),
    # ... 241 more endpoints
]
```

### Test Generation Tools

#### Swagger Endpoint Extraction

```bash
# Generate endpoint registry from swagger.json
python scripts/extract_endpoints.py

# Output: tests/fixtures/endpoints_registry.py with 242 endpoints
# - Complete endpoint information with HTTP methods, paths, parameters
# - Request/response schema references  
# - Module organization and utility functions
```

#### Comprehensive Test File Generation

```bash
# Generate complete test suite for a resource
python scripts/generate_tests.py properties

# Generate with custom output path
python scripts/generate_tests.py activities --output tests/custom/my_tests.py

# List all available resources
python scripts/generate_tests.py --list

# Preview generation without creating files
python scripts/generate_tests.py users --dry-run

# Verbose output with detailed information
python scripts/generate_tests.py properties --verbose
```

### Generated Test Features

The test generator creates comprehensive test files with:

#### CRUD Operations
- **Create**: Resource creation with validation
- **Read**: Individual and list retrieval 
- **Update**: Partial and complete updates
- **Delete**: Resource deletion with verification

#### Parameter Testing
- **Boundary Tests**: Min/max length, numeric boundaries
- **Type Validation**: Correct parameter types and formats
- **Enum Validation**: Valid enumeration values
- **Constraint Testing**: Parameter-specific business rules

#### Negative Test Cases
- **Not Found**: Non-existent resource handling
- **Invalid Parameters**: Malformed parameter validation
- **Authentication**: Unauthorized access scenarios
- **Rate Limiting**: API limit compliance testing

#### Advanced Test Scenarios  
- **Search & Filter**: Query functionality and filter combinations
- **Pagination**: Page traversal and boundary conditions
- **Performance**: Response times and bulk operations
- **Concurrency**: Concurrent access testing

### Generated Test Structure

```python
# Example: Generated tests/integration/test_properties_comprehensive.py
class TestPropertiesAPI(BaseOFSCTest):
    """Comprehensive tests for Properties API endpoints."""
    
    # CRUD Operations (auto-generated)
    async def test_create_properties(self):
        """Test creating a new property with validation."""
        
    async def test_get_properties_by_id(self):
        """Test retrieving specific property by ID."""
        
    async def test_list_properties(self):
        """Test listing all properties with pagination."""
        
    async def test_update_properties(self):  
        """Test updating existing property."""
        
    async def test_delete_properties(self):
        """Test property deletion and verification."""
    
    # Parameter Boundary Tests (auto-generated based on swagger constraints)
    async def test_get_label_boundary_length(self):
        """Test label parameter length boundaries."""
        
    async def test_get_limit_boundary_numeric(self):
        """Test numeric limit parameter boundaries."""
    
    # Negative Test Cases (auto-generated)
    async def test_get_properties_not_found(self):
        """Test handling of non-existent property requests."""
        
    async def test_get_properties_invalid_params(self):
        """Test validation of invalid parameters."""
    
    # Search & Filter Tests (auto-generated for applicable endpoints)  
    async def test_get_properties_search(self):
        """Test search functionality."""
        
    async def test_get_properties_filter(self):
        """Test filter combinations."""
    
    # Pagination Tests (auto-generated for list endpoints)
    async def test_get_properties_pagination(self):
        """Test pagination behavior."""
    
    # Performance Tests (auto-generated)
    async def test_get_properties_bulk_performance(self):
        """Test bulk operation performance."""
        
    async def test_get_properties_concurrent(self):
        """Test concurrent access patterns."""
```

### CRUD Pattern Detection

The test generator includes intelligent CRUD pattern detection:

```python
# Automatic detection of resource patterns
class CRUDPattern:
    create_endpoint: Optional[EndpointInfo] = None    # POST /resource  
    read_endpoint: Optional[EndpointInfo] = None      # GET /resource/{id}
    list_endpoint: Optional[EndpointInfo] = None      # GET /resource
    update_endpoint: Optional[EndpointInfo] = None    # PUT/PATCH /resource/{id}
    delete_endpoint: Optional[EndpointInfo] = None    # DELETE /resource/{id}
    
    def is_complete_crud(self) -> bool:
        """Check if all CRUD operations are available."""
        return all([self.create_endpoint, self.read_endpoint, 
                   self.update_endpoint, self.delete_endpoint])
```

### Integration with BaseOFSCTest

All generated tests inherit from BaseOFSCTest and automatically include:

- **Automatic Resource Cleanup**: LIFO cleanup tracking
- **Performance Monitoring**: Built-in timing and metrics
- **Rate Limiting**: API-compliant request throttling
- **Error Reporting**: Detailed context and debugging
- **Unique Naming**: Conflict-free test resource generation

## Test Utilities

### BaseOFSCTest Class

The BaseOFSCTest class provides advanced testing capabilities for all endpoint tests:

```python
# tests/utils/base_test.py
class BaseOFSCTest:
    """Advanced base test class with comprehensive testing features."""
    
    def __init__(self):
        self.resource_tracker = TestResourceTracker()    # LIFO cleanup
        self.performance_tracker = PerformanceTracker()  # Response timing
        self.name_generator = TestNameGenerator()        # Unique naming
        self.rate_limiter = RateLimiter()               # API compliance
        self.endpoint_context = {}                       # Error reporting context
    
    # === Resource Management ===
    async def create_test_resource(self, resource_type: str, create_function: Callable, 
                                 cleanup_function: Optional[Callable] = None, **create_kwargs) -> Any:
        """Create resource with automatic cleanup tracking."""
        resource = await create_function(**create_kwargs)
        if cleanup_function:
            self.track_resource(resource_type, resource.id, cleanup_function)
        return resource
    
    def track_resource(self, resource_type: str, resource_id: str, cleanup_function: Callable):
        """Track resource for automatic cleanup with LIFO ordering."""
        self.resource_tracker.track(resource_type, resource_id, cleanup_function)
    
    async def cleanup_all_resources(self):
        """Clean up all tracked resources in LIFO order."""
        await self.resource_tracker.cleanup_all()
    
    # === Performance Tracking ===
    @contextmanager
    def track_performance(self, operation_name: str):
        """Context manager for performance tracking."""
        return self.performance_tracker.track(operation_name)
    
    def assert_response_time_acceptable(self, operation: str, max_seconds: float):
        """Assert operation completed within acceptable time."""
        metrics = self.performance_tracker.get_metrics(operation)
        assert metrics.duration <= max_seconds, f"{operation} too slow: {metrics.duration:.3f}s"
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics summary."""
        return self.performance_tracker.get_summary()
    
    # === Unique Name Generation ===  
    def generate_unique_label(self, prefix: str) -> str:
        """Generate unique test resource identifier."""
        return self.name_generator.generate_label(prefix)
    
    def generate_unique_name(self, base_name: str) -> str:
        """Generate unique test resource name."""
        return self.name_generator.generate_name(base_name)
    
    # === Rate Limiting ===
    def set_rate_limit_delay(self, delay_seconds: float):
        """Set rate limiting delay for API compliance."""
        self.rate_limiter.set_delay(delay_seconds)
    
    async def rate_limited_call(self, api_function: Callable, *args, **kwargs):
        """Execute API call with rate limiting."""
        return await self.rate_limiter.execute(api_function, *args, **kwargs)
    
    # === Error Reporting & Context ===
    def set_endpoint_context(self, endpoint_id: int, additional_context: Dict = None):
        """Set endpoint context for detailed error reporting."""
        self.endpoint_context = {
            'endpoint_id': endpoint_id,
            'timestamp': datetime.now().isoformat(),
            **(additional_context or {})
        }
    
    @contextmanager
    def api_call_context(self, endpoint_id: int):
        """Context manager for API call error reporting."""
        self.set_endpoint_context(endpoint_id)
        try:
            yield
        except Exception as e:
            # Enhance exception with endpoint context
            enhanced_message = f"Endpoint {endpoint_id} failed: {str(e)}"
            raise type(e)(enhanced_message) from e
    
    @contextmanager
    def expect_exception(self, exception_type: type, message_pattern: str = None):
        """Context manager for testing expected exceptions."""
        try:
            yield
            pytest.fail(f"Expected {exception_type.__name__} but no exception was raised")
        except exception_type as e:
            if message_pattern and message_pattern not in str(e):
                pytest.fail(f"Exception message '{str(e)}' doesn't match pattern '{message_pattern}'")
        except Exception as e:
            pytest.fail(f"Expected {exception_type.__name__} but got {type(e).__name__}: {str(e)}")
    
    # === Response Validation ===
    def assert_pydantic_model_valid(self, response_data: Dict[str, Any], model_class: type):
        """Validate response data against Pydantic model."""
        try:
            model_instance = model_class(**response_data)
            return model_instance
        except ValidationError as e:
            pytest.fail(f"Response validation failed for {model_class.__name__}: {str(e)}")
    
    def validate_list_response(self, response_data: Dict[str, Any], model_class: type, 
                             expected_count: int = None, max_count: int = None):
        """Validate list response structure and item models."""
        assert 'items' in response_data, "List response missing 'items' field"
        items = response_data['items']
        assert isinstance(items, list), "Response 'items' is not a list"
        
        if expected_count is not None:
            assert len(items) == expected_count, f"Expected {expected_count} items, got {len(items)}"
        if max_count is not None:
            assert len(items) <= max_count, f"Too many items: {len(items)} > {max_count}"
        
        # Validate each item
        for i, item in enumerate(items):
            try:
                model_class(**item)
            except ValidationError as e:
                pytest.fail(f"Item {i} validation failed: {str(e)}")
    
    # === Test Data Helpers ===
    def create_test_data_with_prefix(self, base_data: Dict[str, Any], prefix: str = None) -> Dict[str, Any]:
        """Create test data with unique prefix to avoid conflicts."""
        if prefix is None:
            prefix = self.generate_unique_label('test')
        
        # Apply prefix to common identifier fields
        data = base_data.copy()
        for field in ['label', 'name', 'id', 'code']:
            if field in data:
                data[field] = f"{prefix}_{data[field]}"
        
        return data
```

### Advanced BaseOFSCTest Features

#### Automatic Resource Cleanup
- **LIFO Ordering**: Resources cleaned up in reverse creation order
- **Exception Safety**: Cleanup occurs even if tests fail
- **Flexible Cleanup**: Custom cleanup functions per resource type
- **Batch Cleanup**: Efficient cleanup of multiple resources

#### Performance Monitoring
- **Operation Timing**: Precise measurement of API call durations
- **Statistical Analysis**: Min, max, average, and percentile metrics
- **Performance Assertions**: Configurable performance thresholds
- **Trend Analysis**: Performance tracking across test runs

#### Rate Limiting Compliance
- **Automatic Throttling**: Respect API rate limits during testing
- **Configurable Delays**: Adjustable delays between API calls
- **Retry Logic**: Automatic retry with exponential backoff
- **Concurrent Limiting**: Global rate limiting across parallel tests

#### Error Reporting & Context
- **Endpoint Context**: Detailed error reporting with endpoint information
- **Exception Enhancement**: Enriched exception messages with test context
- **Expected Exception Testing**: Robust negative test case validation
- **Debug Information**: Comprehensive test failure debugging

#### Response Validation
- **Pydantic Model Validation**: Automatic model validation against responses
- **List Response Handling**: Specialized validation for paginated responses
- **Schema Compliance**: Ensure responses match expected schemas
- **Data Integrity**: Validate response data consistency and completeness

#### Test Data Management
- **Unique Naming**: Conflict-free test resource naming
- **Prefix Management**: Systematic test data organization
- **Data Templates**: Reusable test data patterns
- **Cleanup Integration**: Automatic cleanup of generated test data
```

## Test Data Management

```python
# tests/fixtures/response_loader.py
import json
from pathlib import Path
from typing import Dict, Any, List

class ResponseLoader:
    """Utility for loading real API response data for testing."""
    
    def __init__(self, response_dir: Path = None):
        if response_dir is None:
            response_dir = Path(__file__).parent.parent.parent / "response_examples"
        self.response_dir = response_dir
    
    def load_response(self, filename: str) -> Dict[str, Any]:
        """Load a specific response file."""
        file_path = self.response_dir / filename
        with open(file_path) as f:
            return json.load(f)
    
    def load_all_responses(self, pattern: str = "*.json") -> List[Dict[str, Any]]:
        """Load all response files matching pattern."""
        responses = []
        for file_path in self.response_dir.glob(pattern):
            with open(file_path) as f:
                responses.append(json.load(f))
        return responses
```

## Error Handling and Debug

### Debug on Failure

```python
# tests/conftest.py
import pytest
import logging
from pathlib import Path

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Generate detailed debug logs on test failure."""
    outcome = yield
    rep = outcome.get_result()
    
    if rep.when == "call" and rep.failed:
        # Create debug directory
        debug_dir = Path("test_debug") / item.nodeid.replace("/", "_").replace("::", "_")
        debug_dir.mkdir(parents=True, exist_ok=True)
        
        # Save request/response logs
        if hasattr(item, "client_logs"):
            with open(debug_dir / "client_logs.txt", "w") as f:
                f.write("\n".join(item.client_logs))
        
        # Save test context
        with open(debug_dir / "context.json", "w") as f:
            json.dump({
                "test": item.nodeid,
                "timestamp": datetime.now().isoformat(),
                "environment": getattr(item, "test_env", "unknown"),
                "error": str(rep.longrepr)
            }, f, indent=2)
```

## Test Reporting

### HTML Report Generation

```python
# pytest.ini
[pytest]
addopts = 
    --cov=ofsc
    --cov-report=html:htmlcov
    --cov-report=term-missing
    --html=test_report.html
    --self-contained-html
    --maxfail=10
    -v

testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

markers =
    unit: Unit tests (no external dependencies)
    integration: Integration tests (may require live credentials)
    live: Live environment tests (requires real OFSC instance)
    slow: Slow running tests
    fast: Fast running tests
    e2e: End-to-end tests
```

## Implementation Status and Gaps

### ✅ Fully Implemented Features

- **Model Validation Tests**: Complete with automatic discovery and validation of all response examples
- **Unit Tests**: Comprehensive mocking with respx, authentication testing, and API method coverage
- **Live Tests**: OAuth2 authentication, token management, and real API integration
- **Parallel Testing**: Full implementation with category-specific controls and rate limiting
- **Test Generation**: Automated comprehensive test file generation from swagger specification
- **BaseOFSCTest**: Advanced base class with resource cleanup, performance tracking, and error reporting
- **Endpoint Registry**: Complete registry of 242 OFSC API endpoints with parameters and schemas
- **Performance Tooling**: Measurement, optimization, and reporting capabilities

### 🔄 Partially Implemented Features

- **End-to-End Tests**: Basic implementation exists but coverage varies by endpoint
- **Integration Tests**: Some comprehensive test files exist (e.g., test_users_comprehensive.py) but not systematic across all endpoints
- **Test Data Factories**: Basic factory utilities exist but could be expanded for more resources

### ❌ Future Enhancement Opportunities

- **Enhanced Test Data Factories**: Expand factory coverage for all major OFSC resources
- **Advanced Performance Analytics**: Detailed performance trend analysis and reporting
- **CI/CD Integration**: Enhanced GitHub Actions workflows with parallel testing
- **Test Result Analytics**: Automated test result analysis and reporting

### 📋 Implementation Roadmap

#### Immediate Priorities (Current Phase)
1. **Standardize Test Markers**: Ensure consistent pytest marker usage across all test files
2. **Documentation Alignment**: Complete alignment between documented features and implementation
3. **Test Coverage**: Expand end-to-end test coverage for remaining endpoints

#### Future Enhancements (Beyond Current Phase)
1. **Enhanced Test Data Factories**: Expand factory coverage for all major OFSC resources
2. **Advanced Performance Analytics**: Detailed performance trend analysis and reporting
3. **CI/CD Integration**: Enhanced GitHub Actions workflows with parallel testing
4. **Test Result Analytics**: Automated test result analysis and reporting

### Architecture Philosophy

The v3.0 testing strategy prioritizes simplicity and effectiveness:

- **Unit Testing**: Uses respx mocking for isolated, fast testing without external dependencies
- **Live Testing**: Direct API integration for authentic validation with rate limiting
- **Configuration**: Environment variables for flexibility and security
- **Parallel Execution**: Category-specific optimization for maximum performance
- **Test Generation**: Automated comprehensive test creation from API specifications

## Coverage Requirements

- **Target**: 80% overall coverage
- **Exclusions**:
  - `__repr__` and `__str__` methods
  - Type checking blocks (`if TYPE_CHECKING:`)
  - Abstract methods
  - Defensive programming assertions

## Continuous Integration

### Test Marker Guidelines

#### Marker Usage Standards

To ensure consistent test categorization and execution, follow these marker guidelines:

```python
# Unit Tests - No external dependencies, use mocked responses
@pytest.mark.unit
@pytest.mark.asyncio  # For async tests
class TestAuthUnit:
    def test_basic_auth_creation(self):
        """Test Basic Auth object creation with mock data."""
        
# Integration Tests - May require credentials, test component interaction  
@pytest.mark.integration
@pytest.mark.asyncio
class TestUserIntegration:
    async def test_user_crud_workflow(self):
        """Test complete user CRUD workflow."""
        
# Live Tests - Require real OFSC instance and credentials
@pytest.mark.live
@pytest.mark.asyncio  
class TestLiveAuth:
    async def test_oauth2_live_token(self):
        """Test OAuth2 token acquisition with real OFSC API."""
        
# End-to-End Tests - Complete workflow testing, may require external setup
@pytest.mark.e2e
@pytest.mark.asyncio
class TestMetadataE2E:
    async def test_complete_metadata_workflow(self):
        """Test complete metadata management workflow."""
        
# Performance Markers - Additional categorization
@pytest.mark.slow   # Tests taking >5 seconds
@pytest.mark.fast   # Tests completing <1 second
```

#### Marker Combinations

- **All async tests** must include `@pytest.mark.asyncio`
- **Unit tests** should only use `@pytest.mark.unit` 
- **Integration tests** should include both `@pytest.mark.integration` and appropriate performance markers
- **Live tests** must include `@pytest.mark.live` and should include performance markers
- **Generated tests** should use appropriate markers based on their test type

#### Running Tests by Marker

```bash
# Run only unit tests
uv run pytest -m unit

# Run only live tests  
uv run pytest -m live

# Run integration and e2e tests
uv run pytest -m "integration or e2e"

# Run all tests except live (for CI without credentials)
uv run pytest -m "not live"

# Run only fast tests for quick feedback
uv run pytest -m fast

# Run slow tests separately
uv run pytest -m slow
```

### GitHub Actions Workflow

```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.12", "3.13"]
        test-category: ["unit", "integration", "models"]
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        uv sync --dev
    
    - name: Run tests with parallel execution
      run: |
        python scripts/run_tests_parallel.py --${{ matrix.test-category }} --measure
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      
  live-tests:
    runs-on: ubuntu-latest  
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.12"
    
    - name: Install dependencies
      run: |
        uv sync --dev
        
    - name: Run live tests
      env:
        OFSC_INSTANCE: ${{ secrets.OFSC_INSTANCE }}
        OFSC_CLIENT_ID: ${{ secrets.OFSC_CLIENT_ID }}
        OFSC_CLIENT_SECRET: ${{ secrets.OFSC_CLIENT_SECRET }}
      run: |
        uv run pytest -m live --maxfail=5
```

## Summary

This complete testing guide provides everything needed to effectively test the OFSC Python Wrapper v3.0:

### What's Included
- **4 Test Types**: Model validation, unit, end-to-end, and live tests
- **Parallel Execution**: 4x performance improvement with intelligent rate limiting
- **Test Generation**: Automated comprehensive test creation from swagger specifications
- **Advanced Base Class**: BaseOFSCTest with cleanup, performance tracking, and error reporting
- **Practical Guidance**: Development workflows, debugging, troubleshooting, and best practices

### Key Features
- **242 API Endpoints**: Complete endpoint registry with parameter validation
- **Automated Cleanup**: LIFO resource cleanup prevents test pollution
- **Performance Monitoring**: Built-in timing and optimization capabilities
- **Rate Limiting**: API-compliant testing with automatic throttling
- **CI/CD Ready**: Enhanced GitHub Actions workflows with parallel testing

### Getting Started
1. **Quick Start**: `uv run pytest tests/unit/ -n 8` for fast unit tests
2. **Full Suite**: `python scripts/run_tests_parallel.py --all --measure` for comprehensive testing
3. **Development**: Use markers like `-m "not live"` to exclude slow tests
4. **Debugging**: Add `-s -l --pdb` for detailed failure investigation

### Documentation Structure
This guide consolidates information from multiple sources into a single comprehensive reference:
- Testing strategy and architecture
- Parallel execution capabilities  
- Test generation and automation
- Practical usage examples
- Troubleshooting and best practices
- Migration guidance and rollback plans

For specific implementation details, see the actual test files in the `tests/` directory and utility scripts in `scripts/`.