## pyOFSC

**Oracle Fusion Field Service** (formerly Oracle Field Service Cloud, formerly ETAdirect) is a cloud-based field service management platform for scheduling, dispatching, and managing mobile workforces.

**pyOFSC** is a Python wrapper for its REST API, providing both synchronous and asynchronous clients with Pydantic model-based validation. See the [official Oracle Fusion Field Service documentation](https://docs.oracle.com/en/cloud/saas/field-service/index.html) for API details.

## Async Client

Starting with version 2.19, pyOFSC includes an async client (`AsyncOFSC`) that provides asynchronous API access using `httpx` and Python's `async`/`await` patterns.

**Implementation Status**: The async client is being implemented progressively. Currently available async methods are marked with `[Sync & Async]` tags in [docs/ENDPOINTS.md](docs/ENDPOINTS.md).

### Usage Example
```python
from ofsc.async_client import AsyncOFSC
async with AsyncOFSC(clientID="...", secret="...", companyName="...") as client:
    workzones = await client.metadata.get_workzones()
```

### Key Features
- **Async/Await Support**: Full async/await pattern support for non-blocking I/O
- **Same Models**: Reuses all existing Pydantic models from the sync version
- **Context Manager**: Must be used as an async context manager to properly manage HTTP client lifecycle
- **Simplified API**: Async methods always return Pydantic models (no `response_type` parameter)
- **Request/Response Logging**: Optional httpx event hooks for automatic API call tracing

### Enabling Request/Response Logging

Pass `enable_logging=True` to automatically log all HTTP requests and responses via Python's standard logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

async with AsyncOFSC(clientID="...", secret="...", companyName="...", enable_logging=True) as client:
    workzones = await client.metadata.get_workzones()
    # DEBUG: Request: GET https://company.fs.ocs.oraclecloud.com/rest/ofscMetadata/v1/workZones
    # DEBUG: Response: GET https://company.fs.ocs.oraclecloud.com/rest/ofscMetadata/v1/workZones 200
```

Logs are emitted under the `ofsc.async_client` logger. HTTP errors (4xx/5xx) are also logged at WARNING level. Disabled by default with zero overhead.

## Models

All API entities use Pydantic v2 models. See `ofsc/models/` for available models.

## Testing

pyOFSC includes a comprehensive test suite with 500+ tests. Tests run in parallel by default using pytest-xdist for 10x faster execution.

### Running Tests

```bash
# Run all tests (parallel for safe tests, sequential for serial tests)
uv run pytest

# Run tests with specific number of workers
uv run pytest -n 4 -m "not serial"

# Run all tests sequentially (disable parallel execution)
uv run pytest -n 0

# Run only serial tests (sequential execution)
uv run pytest -m serial -n 0

# Run only mocked tests (no API credentials needed)
uv run pytest -m "not uses_real_data"

# Run specific test file
uv run pytest tests/async/test_async_workzones.py
```

**Note:** By default, tests marked with `@pytest.mark.serial` are excluded from parallel execution to prevent conflicts when modifying shared API state. To run all tests including serial ones, use: `uv run pytest -m "" -n auto && uv run pytest -m serial -n 0`

### Test Requirements

- **Mocked tests**: No special requirements, use saved API responses
- **Live tests** (marked with `@pytest.mark.uses_real_data`): Require API credentials in `.env` file:
  ```
  OFSC_CLIENT_ID=your_client_id
  OFSC_COMPANY=your_company
  OFSC_CLIENT_SECRET=your_secret
  ```

### Test Markers

- `@pytest.mark.uses_real_data` - Tests that require API credentials
- `@pytest.mark.serial` - Tests that must run sequentially (automatically excluded from parallel execution)
- `@pytest.mark.slow` - Slow-running tests
- `@pytest.mark.integration` - Integration tests

## Implemented Functions

**195 async endpoints** (80% coverage) and **89 sync endpoints** (37% coverage) across Core, Metadata, Capacity, Statistics, and Auth modules.

See [docs/ENDPOINTS.md](docs/ENDPOINTS.md) for the full implementation status table.

## Usage Examples

**Sync:**
```python
from ofsc import OFSC
instance = OFSC(clientID="...", secret="...", companyName="...")
workzones = instance.metadata.get_workzones()
```

**Async:**
```python
from ofsc.async_client import AsyncOFSC
async with AsyncOFSC(clientID="...", secret="...", companyName="...") as client:
    workzones = await client.metadata.get_workzones()
```

See the [examples/](examples/) directory for comprehensive sync and async usage examples.

## Test History

OFS REST API Version | PyOFSC
------------ | -------------
20C| 1.7
21A| 1.8, 1.8,1, 1.9
21D| 1.15
22B| 1.16, 1.17
22D| 1.18
24C| 2.0
25B| 2.12
26A| 2.24.0

## Future Deprecation Notice - OFSC 3.0

**Important**: Starting with Oracle Fusion Field Service 3.0, the synchronous client (`OFSC`) will be deprecated in favor of the async client (`AsyncOFSC`).

### Migration Path
- The async client (`AsyncOFSC`) is the recommended approach for all new development
- OFSC 3.0 will provide a **compatibility wrapper** to allow existing synchronous code to continue working without modifications
- The compatibility wrapper will internally use the async client with synchronous adapters
- We recommend gradually migrating to the async client to take advantage of better performance and scalability

### Timeline
- **OFSC 2.x**: Both sync and async clients fully supported
- **OFSC 3.0**: Sync client deprecated, compatibility wrapper provided
- **OFSC 4.0**: Sync client may be removed (compatibility wrapper will remain for at least one major version)
