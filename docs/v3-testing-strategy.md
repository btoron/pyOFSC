# OFSC Python Wrapper v3.0 Testing Strategy

## Overview

The v3.0 testing strategy implements a multi-layered approach to ensure reliability, correctness, and maintainability of the OFSC Python Wrapper. The strategy includes four distinct test types: model validation tests, mock tests, live mock server tests, and live integration tests.

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

### 3. Live Mock Server Tests
Integration tests against a custom mock server that simulates OFSC API.

- **Location**: `tests/integration/`
- **Purpose**: Test full request/response cycle with realistic API behavior
- **Configuration**: `config.test.toml` with mock server details
- **Features**: Record/replay capability for consistent testing

### 4. Live Tests
End-to-end tests against real OFSC test environments.

- **Location**: `tests/live/`
- **Purpose**: Validate actual API integration
- **Marker**: `@pytest.mark.live`
- **Isolation**: Unique prefixes for test data

## Test Configuration

### Test Configuration Structure

#### config.test.toml (Test-Specific Configuration)

Test configuration is maintained separately from main application configuration to ensure isolation and prevent test settings from affecting production.

```toml
[test]
# Global test settings
coverage_target = 80
report_format = "html"
debug_on_failure = true

[test.environments.dev]
url = "https://dev.ofsc.example.com"
client_id = "dev_client_id"
client_secret = "dev_client_secret"
instance = "dev_instance"

[test.environments.staging]
url = "https://staging.ofsc.example.com"
client_id = "staging_client_id"
client_secret = "staging_client_secret"
instance = "staging_instance"

[test.environments.prod]
url = "https://prod.ofsc.example.com"
client_id = "prod_client_id"
client_secret = "prod_client_secret"
instance = "prod_instance"

[test.mock_server]
url = "http://localhost:8080"
client_id = "mock_client_id"
client_secret = "mock_client_secret"
record_mode = "replay"  # record, replay, or passthrough
storage_path = "tests/mock_recordings"

[test.async]
max_concurrent = 10
timeout = 30
retry_count = 3
retry_delay = 1
```

#### Main Application Configuration (config.toml)

Main application configuration is separate and contains only production credentials:

```toml
[credentials]
instance = "your_instance"
client_id = "your_client_id"
client_secret = "your_client_secret"

[credentials.oauth2]
# Optional OAuth2 settings
token_url = "custom_token_url"
scope = "custom_scope"
```

### Configuration Precedence

1. Environment variables (highest priority)
2. .env file (if present)
3. config.test.toml file
4. Default values (lowest priority)

Environment variables follow the pattern: `OFSC_TEST_{SECTION}_{KEY}`
Example: `OFSC_TEST_ENVIRONMENTS_DEV_INSTANCE`

The test suite supports both config.test.toml and .env files for flexibility.

## Test Organization

### Directory Structure

```
tests/
├── conftest.py              # Shared fixtures
├── config.test.toml         # Test configuration
├── data/                    # Test data files
├── mock_recordings/         # Recorded API responses
├── models/                  # Model validation tests
│   ├── test_core_models.py
│   ├── test_metadata_models.py
│   └── test_capacity_models.py
├── unit/                    # Mock tests
│   ├── test_core_api.py
│   ├── test_metadata_api.py
│   ├── test_capacity_api.py
│   └── test_auth.py
├── integration/             # Live mock server tests
│   ├── test_core_integration.py
│   ├── test_metadata_integration.py
│   └── test_capacity_integration.py
└── live/                    # Live environment tests
    ├── test_core_live.py
    ├── test_metadata_live.py
    └── test_capacity_live.py
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

### Live Mock Server Tests

```python
# tests/integration/conftest.py
import pytest
from tests.mock_server import OFSCMockServer

@pytest.fixture(scope="session")
def mock_server():
    """Start mock server for integration tests."""
    server = OFSCMockServer(port=8080)
    server.start()
    yield server
    server.stop()

# tests/integration/test_core_integration.py
@pytest.mark.integration
class TestCoreAPIIntegration:
    async def test_activity_lifecycle(self, mock_server, test_client):
        """Test complete activity lifecycle against mock server."""
        # Create activity
        activity = await test_client.core.create_activity(
            CreateActivityRequest(
                activity_type="install",
                customer_number="TEST-001"
            )
        )
        assert activity.activity_id.startswith("TEST-")
        
        # Update activity
        updated = await test_client.core.update_activity(
            activity.activity_id,
            UpdateActivityRequest(status="complete")
        )
        assert updated.status == "complete"
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

## Test Execution

### Running Specific Test Types

```bash
# Run only model validation tests
pytest tests/models/

# Run only mock tests
pytest tests/unit/

# Run only integration tests (mock server)
pytest tests/integration/ -m integration

# Run only live tests
pytest tests/live/ -m live

# Run all tests except live
pytest -m "not live"

# Run tests for specific environment
pytest --env staging

# Run with coverage report
pytest --cov=ofsc --cov-report=html
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

## Mock Server Implementation

### Custom Mock Server

```python
# tests/mock_server/server.py
from aiohttp import web
import json
from pathlib import Path

class OFSCMockServer:
    """Custom mock server for OFSC API simulation."""
    
    def __init__(self, port: int = 8080):
        self.port = port
        self.app = web.Application()
        self.recordings = {}
        self.setup_routes()
    
    def setup_routes(self):
        """Setup API routes."""
        self.app.router.add_route('*', '/rest/ofscCore/v1/{path:.*}', self.handle_core_api)
        self.app.router.add_route('*', '/rest/ofscMetadata/v1/{path:.*}', self.handle_metadata_api)
        self.app.router.add_route('*', '/rest/ofscCapacity/v1/{path:.*}', self.handle_capacity_api)
    
    async def handle_core_api(self, request):
        """Handle core API requests."""
        path = request.match_info['path']
        method = request.method
        
        # Check recordings
        key = f"{method}:{path}"
        if key in self.recordings:
            return web.json_response(self.recordings[key])
        
        # Generate mock response
        if path.startswith("activities/"):
            activity_id = path.split('/')[-1]
            return web.json_response({
                "activityId": activity_id,
                "status": "pending",
                "activityType": "install"
            })
        
        return web.json_response({"error": "Not found"}, status=404)
    
    def record_response(self, method: str, path: str, response: dict):
        """Record API response for replay."""
        key = f"{method}:{path}"
        self.recordings[key] = response
    
    def load_recordings(self, path: Path):
        """Load recorded responses from disk."""
        for file in path.glob("*.json"):
            with open(file) as f:
                data = json.load(f)
                self.recordings[data["key"]] = data["response"]
    
    def start(self):
        """Start the mock server."""
        web.run_app(self.app, host='localhost', port=self.port)
```

## Test Data Factory

```python
# tests/factories.py
import factory
from faker import Faker
from ofsc.models import Activity, Resource, User

fake = Faker()

class ActivityFactory(factory.Factory):
    """Factory for creating test activities."""
    class Meta:
        model = Activity
    
    activity_id = factory.LazyFunction(lambda: f"TEST_{fake.uuid4()[:8]}")
    activity_type = factory.Faker('random_element', elements=['install', 'repair', 'delivery'])
    status = 'pending'
    customer_name = factory.Faker('name')
    customer_number = factory.LazyFunction(lambda: f"CUST_{fake.random_number(5)}")
    
    @factory.post_generation
    def set_dates(obj, create, extracted, **kwargs):
        """Set activity dates based on test requirements."""
        if create:
            obj.date = fake.future_date()
            obj.start_time = "09:00"
            obj.end_time = "17:00"

class ResourceFactory(factory.Factory):
    """Factory for creating test resources."""
    class Meta:
        model = Resource
    
    resource_id = factory.LazyFunction(lambda: f"TECH_{fake.uuid4()[:8]}")
    name = factory.Faker('name')
    email = factory.Faker('email')
    phone = factory.Faker('phone_number')
    resource_type = 'FT'
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
    live: Live environment tests (requires real OFSC instance)
    integration: Integration tests (requires mock server)
    slow: Slow running tests
    unit: Unit tests with mocked responses
```

## Coverage Requirements

- **Target**: 80% overall coverage
- **Exclusions**:
  - `__repr__` and `__str__` methods
  - Type checking blocks (`if TYPE_CHECKING:`)
  - Abstract methods
  - Defensive programming assertions

## Continuous Integration

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
        test-type: ["unit", "integration", "models"]
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -e ".[test]"
    
    - name: Run tests
      run: |
        pytest tests/${{ matrix.test-type }} --cov=ofsc
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```