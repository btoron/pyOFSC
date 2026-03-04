# TEST EXECUTION SUMMARY

**Project:** pyOFSC - Python wrapper for Oracle Field Service Cloud (OFSC) REST API
**Version:** 2.24.0
**Report Date:** 2026-03-04
**Executed By:** QA Automation (Claude Code - Sonnet 4.6)
**Branch:** release/2.24.0

---

## 1. EXECUTIVE SUMMARY

| Metric | Value |
|--------|-------|
| Total tests collected | 888 |
| Total tests run (mocked only) | 553 |
| Passed | 543 |
| Failed | 2 |
| Skipped | 8 |
| Overall mocked pass rate | 98.2% |
| Total code coverage (full suite) | 63.5% |
| Async-only coverage | 59.0% |
| Minimum required coverage (80%) | NOT MET |

---

## 2. TEST SUITE BREAKDOWN

### 2.1 Tests by Directory

| Directory | Total Tests | Mocked Tests | Real Data Tests | Mocked Pass | Mocked Fail | Mocked Skip |
|-----------|-------------|--------------|-----------------|-------------|-------------|-------------|
| `tests/async/` | 659 | 434 | 225 | 432 | 0 | 2 |
| `tests/core/` | 59 | 4 | 55 | 4 | 0 | 0 |
| `tests/metadata/` | 82 | 40 | 42 | 36 | 0 | 4 |
| `tests/capacity/` | 51 | 41 | 10 | 30 | 2 | 11 |
| `tests/` (root) | 37 | 34 | 3 | 34 | 0 | 0 |
| **TOTAL** | **888** | **553** | **335** | **536** | **2** | **17** |

Notes:
- "Mocked Tests" = tests NOT marked `uses_real_data`
- 20 integration tests in `tests/capacity/test_quota_integration.py` are marked `@pytest.mark.integration` but NOT `@pytest.mark.uses_real_data`
- The 2 failures occur exclusively when `.env` credentials are present AND tests are run with `pytest-xdist` parallel execution across the full suite

### 2.2 Marker Distribution

| Marker | Count |
|--------|-------|
| `uses_real_data` | 335 |
| `integration` | 20 |
| `serial` | (excluded from default runs by addopts) |
| Unmarked (pure mocked) | ~533 |

---

## 3. TEST FAILURES - ROOT CAUSE ANALYSIS

### 3.1 FAILURE 1: `test_quota_with_boolean_parameters`
**File:** `tests/capacity/test_quota_integration.py::TestQuotaAPIIntegration::test_quota_with_boolean_parameters`

**Category:** Logic Error / API Constraint

**Root Cause:** The test sends `aggregateResults=True` with `areas=["FLUSA", "CAUSA"]` to the real OFSC API. The API rejects the request with HTTP 400:
```
'Attemption to aggregate capacity areas with different booking type: Time Slot Based - 1; Booking Interval Based - 1'
```
These two capacity areas have incompatible booking types and cannot be aggregated together. The test assumes aggregation works for any combination of areas.

**Trigger Condition:** This test runs (rather than being skipped) when:
1. A `.env` file exists with valid OFSC credentials, AND
2. The test fixture `ofsc_instance` uses `load_dotenv()` to pick up those credentials

**Classification:** Integration test marking issue. The test is decorated with `@pytest.mark.integration` but NOT `@pytest.mark.uses_real_data`. Therefore it is NOT deselected by `-m "not uses_real_data"`.

**Remediation (without modifying source code):**
- Test should be marked with BOTH `@pytest.mark.integration` AND `@pytest.mark.uses_real_data`
- OR the test assertion should handle the incompatible-area constraint gracefully
- The `addopts` in `pyproject.toml` deselects `serial` but not `integration`

### 3.2 FAILURE 2: `test_quota_error_handling`
**File:** `tests/capacity/test_quota_integration.py::TestQuotaAPIIntegration::test_quota_error_handling`

**Category:** Test Design Bug / OFSAPIException String Representation Gap

**Root Cause:** The test expects that `str(exception)` contains meaningful text like "area" or "not found". However, `OFSAPIException` is instantiated with keyword arguments (`**response.json()`) and its `__init__` stores them as attributes rather than passing them to `super().__init__()` as the message string. As a result, `str(OFSAPIException(**kwargs))` returns an empty string `''`.

**Trace:**
```python
# ofsc/common.py line 67
raise OFSAPIException(**response.json())
# kwargs = {"type": "...", "title": "Not Found", "status": "404", "detail": "Unknown capacity area..."}

# ofsc/exceptions.py
class OFSAPIException(Exception):
    def __init__(self, *args: object, **kwargs) -> None:
        super().__init__(*args)  # args=() so message is empty
        # kwargs stored as attributes, never passed to super().__init__
```

**Impact:** `str(OFSAPIException(...))` always returns `''` making the assertion `assert "area" in str(e).lower()` fail even when the exception contains the expected detail in `e.detail`.

**Classification:** This reveals a genuine defect in the `OFSAPIException` class: error details passed via `**kwargs` are silently ignored by the string representation. This is a real quality issue.

**Note:** The `OFSCApiError` subclass (used by async client) takes a `message` string parameter and behaves correctly. The old-style `OFSAPIException(**response.json())` pattern in `ofsc/common.py` (sync client) does not produce a human-readable string representation.

---

## 4. CODE COVERAGE ANALYSIS

### 4.1 Coverage by Module (Full Mocked Suite)

| Module | Statements | Covered | Missed | Coverage | Status |
|--------|-----------|---------|--------|----------|--------|
| `ofsc/models/inventories.py` | 42 | 42 | 0 | 100% | PASS |
| `ofsc/models/statistics.py` | 68 | 68 | 0 | 100% | PASS |
| `ofsc/exceptions.py` | 40 | 40 | 0 | 100% | PASS |
| `ofsc/capacity.py` | 45 | 45 | 0 | 100% | PASS |
| `ofsc/async_client/core/__init__.py` | 7 | 7 | 0 | 100% | PASS |
| `ofsc/models/__init__.py` | 165 | 165 | 0 | 100% | PASS |
| `ofsc/models/users.py` | 51 | 50 | 1 | 98% | PASS |
| `ofsc/async_client/__init__.py` | 74 | 73 | 1 | 99% | PASS |
| `ofsc/models/capacity.py` | 226 | 219 | 7 | 97% | PASS |
| `ofsc/exceptions.py` | 40 | 40 | 0 | 95% | PASS |
| `ofsc/models/resources.py` | 208 | 194 | 14 | 93% | PASS |
| `ofsc/models/metadata.py` | 689 | 637 | 52 | 92% | PASS |
| `ofsc/oauth.py` | 7 | 6 | 1 | 86% | PASS |
| `ofsc/models/_base.py` | 161 | 136 | 25 | 84% | PASS |
| `ofsc/common.py` | 56 | 45 | 11 | 80% | PASS |
| `ofsc/async_client/oauth.py` | 46 | 38 | 8 | 83% | PASS |
| `ofsc/async_client/statistics.py` | 141 | 114 | 27 | 81% | PASS |
| `ofsc/__init__.py` | 60 | 45 | 15 | 75% | FAIL |
| `ofsc/async_client/core/inventories.py` | 114 | 85 | 29 | 75% | FAIL |
| `ofsc/metadata.py` | 272 | 179 | 93 | 66% | FAIL |
| `ofsc/async_client/capacity.py` | 213 | 142 | 71 | 67% | FAIL |
| `ofsc/async_client/core/users.py` | 150 | 77 | 73 | 51% | FAIL |
| `ofsc/async_client/metadata.py` | 1349 | 747 | 602 | 55% | FAIL |
| `ofsc/async_client/core/resources.py` | 590 | 216 | 374 | 37% | FAIL |
| `ofsc/core.py` | 376 | 129 | 247 | 34% | FAIL |
| `ofsc/async_client/core/_base.py` | 473 | 73 | 400 | 15% | FAIL |
| **TOTAL** | **5623** | **3572** | **2051** | **63.5%** | **FAIL** |

### 4.2 Critical Coverage Gaps

**1. `ofsc/async_client/core/_base.py` - 15.4% coverage**
This is the most severely under-tested file. It contains 40 async methods for core activity operations. Only `get_events`, `get_subscriptions`, `create_subscription`, `delete_subscription`, `get_daily_extract_dates`, `get_daily_extract_file`, and a handful of others have any mocked test coverage. The following methods have **zero mocked tests**:
- `get_activities` (the mocked tests call `pytest.skip()` unconditionally)
- `get_activity_link`, `set_activity_link`, `delete_activity_link`
- `get_all_activities` (utility method)
- `get_all_properties` (utility method)
- `search_activities`
- `move_activity`
- `bulk_update`

**2. `ofsc/core.py` - 34.3% coverage**
The synchronous core client has minimal mocked coverage. Nearly all 45 methods are only tested via `uses_real_data` tests. Only user management methods (`get_users`, `get_user`, `update_user`, `create_user`) have mocked coverage, totaling just 4 mocked tests.

**3. `ofsc/async_client/core/resources.py` - 36.6% coverage**
Despite having 41 methods and a substantial test file (`test_async_resources_write.py`), error paths and 4 specific methods have no mocked coverage:
- `get_resource_location` (single location by ID)
- Error handling paths for `create_resource`, `get_resource_plans`, `get_resource_assistants`, `get_resource_calendar`

**4. `ofsc/async_client/metadata.py` - 55.4% coverage**
The largest source file (1349 statements) has 602 missed lines. The uncovered lines are concentrated in error paths:
- HTTP error handlers (every method has a `_handle_http_error` call that is only exercised in certain tests)
- Write operations for: activity type groups, activity types, applications, capacity categories, forms, inventory types, link templates, map layers, plugins, shifts

**5. `ofsc/async_client/core/users.py` - 51.3% coverage**
User management error paths are largely untested:
- `get_user_collaboration_groups` error paths
- `create_collaboration_group` and `delete_collaboration_group` error paths
- `get_user_file_property`, `set_user_file_property`, `delete_user_file_property` partial coverage

**6. `ofsc/metadata.py` - 65.8% coverage (sync)**
The synchronous metadata client has many methods only tested with real API data. No mocked tests exist for bulk write operations, workskill conditions PUT, or several routing profile methods.

---

## 5. TEST QUALITY ASSESSMENT

### 5.1 Strengths

1. **Model validation coverage is excellent.** All Pydantic models in `ofsc/models/` achieve 84-100% coverage. Saved-response validation tests provide high confidence in model correctness.

2. **Async client metadata tests are comprehensive.** The `tests/async/` directory with 659 tests is the most mature part of the test suite, reflecting the project's migration priority toward the async client.

3. **Exception hierarchy testing is thorough.** `test_async_exceptions.py` and the exceptions module itself achieve 100% coverage (full suite including real-data tests).

4. **Consistent test patterns.** Tests follow a consistent structure: Live tests (uses_real_data), Model validation tests (mocked), and SavedResponses tests (offline). This is a strong architectural pattern.

5. **Saved response infrastructure** (`tests/saved_responses/`) allows authentic model validation without API calls. Models like `ActivityListResponse`, `WorkzoneListResponse`, `RoutingProfileListResponse` are validated against real response structures.

### 5.2 Weaknesses and Issues

**ISSUE-001: Marker Inconsistency for Integration Tests**
`TestQuotaAPIIntegration` and `TestQuotaAPIPerformance` are marked `@pytest.mark.integration` but NOT `@pytest.mark.uses_real_data`. The project's standard convention (per CLAUDE.md) is to use `uses_real_data` to identify tests requiring API credentials. The `integration` marker exists but is not in the `addopts` deselection filter. This causes these tests to:
- Run when credentials are present in `.env`
- Fail if the API state doesn't match test assumptions
- Create false CI failures when running `-m "not uses_real_data"`

**ISSUE-002: Unconditional `pytest.skip()` in Mocked Tests**
Two tests in `test_async_activities.py` call `pytest.skip()` unconditionally:
```python
async def test_get_activities_returns_model(self, async_instance: AsyncOFSC):
    pytest.skip("Requires API credentials and specific date range")

async def test_get_activities_pagination(self, async_instance: AsyncOFSC):
    pytest.skip("Requires API credentials and specific date range")
```
These were written as stubs but never implemented. They contribute to the critically low coverage of `_base.py`. The `get_activities` method has zero mocked coverage.

**ISSUE-003: OFSAPIException String Representation Is Empty**
As identified in failure analysis, `OFSAPIException(**kwargs).__str__()` returns `''`. Any test code or production code that uses `str(exception)` or relies on the exception message string will receive empty output. The `detail`, `title`, and `type` are stored as attributes but never appear in `repr()` or `str()`. This is a usability defect for debugging and error reporting.

**ISSUE-004: Sync Client Coverage is Very Low (34%)**
The synchronous `OFSC` client (`ofsc/core.py`) has 376 statements with only 34% coverage from mocked tests. Most tests for the sync client are `uses_real_data` tests in `tests/core/` (55 out of 59). There are only 4 mocked tests for the sync core client. As the project migrates to async, this coverage gap will remain unless additional mocked tests are added for the sync client before its eventual deprecation.

**ISSUE-005: Routing Profile Write Tests Skip Due to Missing Saved Responses**
4 tests in `tests/metadata/test_routing_profiles_write.py` always skip because they depend on a saved response file (`tests/saved_responses/routing_profiles/export_routing_plan_actual_data.json`) that does not exist (it is gitignored). These tests would otherwise be fully mocked.

**ISSUE-006: `get_activities` Has No Mocked Tests Despite Being Core Functionality**
The most fundamental API method in the library - `get_activities` - has no mocked tests. All tests for it are marked `uses_real_data`. Given the complexity of `GetActivitiesParams`, this is a significant quality gap.

### 5.3 Test Isolation

Tests correctly use `AsyncMock` for httpx responses. The `async_instance` fixture in `tests/async/conftest.py` properly sets up the async client for both mocked and live scenarios. The `pytest-env` plugin properly sets `RUN_ENV=1`.

The parallel execution via `pytest-xdist` (`-n auto --dist worksteal`) works correctly for mocked tests. The `serial` marker excludes certain tests from parallelization as expected.

---

## 6. ENDPOINT COVERAGE ANALYSIS

### 6.1 Implementation Summary (from ENDPOINTS.md)

| Client | GET | Write (POST/PUT/PATCH) | DELETE | Total | API Total |
|--------|-----|------------------------|--------|-------|-----------|
| Sync only | 57/115 (50%) | 25/102 (25%) | 7/26 (27%) | 89/243 (37%) | 243 |
| Async only | 104/115 (90%) | 68/102 (67%) | 23/26 (88%) | 195/243 (80%) | 243 |

### 6.2 Unimplemented Endpoints (44 total)

The following OFSC API domains have no implementation in either client:
- **Collaboration API** (7 endpoints): Address book, chats, messages, participants
- **Parts Catalog API** (3 endpoints): PUT/DELETE catalog items
- **Activity lifecycle actions** (9 endpoints): `startPrework`, `reopen`, `delay`, `cancel`, `start`, `enroute`, `stopTravel`, `suspend`, `complete`, `notDone`
- **Miscellaneous**: `whereIsMyTech`, `findNearbyActivities`, `bulkUpdateInventories`, `findMatchingResources`, `resourcesInArea`, service requests

### 6.3 Methods with NO Mocked Test Coverage

**Async Core Base (`_base.py`):**
- `get_activities` (2 tests skip unconditionally)
- `search_activities`
- `move_activity`
- `bulk_update`
- `get_activity_link`
- `set_activity_link`
- `delete_activity_link`
- `get_all_activities` (utility)
- `get_all_properties` (utility)

**Async Metadata (`metadata.py`):**
- `get_language` (only get_languages tested, not single language)
- Write operations for: `update_activity_type_group`, `update_activity_type`, `update_application`, `update_api_access`, `create_generate_client_secret`

**Async Resources (`resources.py`):**
- `get_resource_location` (single location by ID)

---

## 7. RECOMMENDATIONS FOR NEW TESTS

### Priority 1 - Critical (Fixes Failures or Near-Zero Coverage)

**REC-001: Add `@pytest.mark.uses_real_data` to integration tests**
Add the `uses_real_data` marker to all tests in `TestQuotaAPIIntegration` and `TestQuotaAPIPerformance`. This immediately fixes the 2 test failures when running `-m "not uses_real_data"`.

**REC-002: Implement mocked tests for `get_activities`**
Replace the unconditional `pytest.skip()` calls in `TestAsyncGetActivities` with proper mocked tests using `AsyncMock`. The `GetActivitiesParams` model has many fields; a comprehensive set of mocked tests would also improve `_base.py` coverage significantly.

Example structure needed:
```python
async def test_get_activities_returns_model(self, async_instance: AsyncOFSC):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "totalResults": 1,
        "items": [{"activityId": 123, "resourceId": "TECH01", "date": "2026-03-04", ...}]
    }
    mock_response.raise_for_status = Mock()
    async_instance.core._client.get = AsyncMock(return_value=mock_response)
    result = await async_instance.core.get_activities(params)
    assert isinstance(result, ActivityListResponse)
```

**REC-003: Add mocked tests for `search_activities`, `move_activity`, `bulk_update`**
These activity management methods in `_base.py` have no mocked coverage. Each should have at minimum: happy path, auth error, and not found error tests.

**REC-004: Fix `OFSAPIException` string representation**
The sync client raises `OFSAPIException(**response.json())` but `str(exception)` is empty. The `detail` field from the API response (which contains meaningful error text) should be accessible via `str(exception)`.

### Priority 2 - High (Improves Low-Coverage Modules)

**REC-005: Add mocked tests for sync `ofsc/core.py`**
The sync client has 34% coverage from mocked tests. At minimum, add mocked tests for the most commonly used methods: `get_activity`, `create_activity`, `update_activity`, `delete_activity`, `get_resources`, `get_resource`. Follow the mock pattern used in `tests/core/test_users.py`.

**REC-006: Add error path tests for `ofsc/async_client/core/users.py`**
The users module is at 51% coverage due to untested error paths. Add tests for:
- `get_user_file_property` - 404 not found
- `set_user_file_property` - 403 authorization error
- `create_collaboration_group` - happy path and errors
- `delete_collaboration_group` - happy path and errors

**REC-007: Add saved responses for routing profile write operations**
Create `tests/saved_responses/routing_profiles/export_routing_plan_actual_data.json` to unblock 4 skipped tests in `test_routing_profiles_write.py`. Use the capture script pattern documented in CLAUDE.md.

**REC-008: Add mocked tests for async metadata write operations**
Many write methods in `ofsc/async_client/metadata.py` (PUT, POST, DELETE) have only `uses_real_data` tests. Add mocked equivalents for:
- `update_activity_type_group`, `update_activity_type`
- `update_capacity_category`, `delete_capacity_category`
- `create_map_layer`, `update_map_layer`
- `install_plugin`

### Priority 3 - Moderate (Incremental Improvements)

**REC-009: Add test for `get_language` (single)**
The `get_language` single-item method exists in `metadata.py` but only `get_languages` (list) has mocked tests. Add a test for the single-language endpoint.

**REC-010: Add test for `get_resource_location` (single)**
Similar to above - only `get_resource_locations` (list) has test coverage; the single-location endpoint `get_resource_location(resource_id, location_id)` has none.

**REC-011: Add coverage for `ofsc/models/_base.py` utility methods**
At 84% coverage, several utility methods on `OFSResponseList` (`__iter__`, `__len__`, `__getitem__`, `append`, `extend`) lack test coverage. These are used throughout the codebase but not directly tested.

**REC-012: Add branch coverage tests for `ofsc/async_client/capacity.py`**
At 67% coverage with many missing error handler lines. Add tests for:
- `get_capacity` with auth error (401)
- `get_booking_closing_schedule` with 404
- `update_quota` - error path
- `show_booking_grid` - happy path (no mocked tests currently)

---

## 8. TOOL AND LIBRARY RECOMMENDATIONS

### 8.1 Current Testing Stack (Already in Use)
- `pytest` 8.3.4 - test runner
- `pytest-asyncio` 0.26.0 - async test support
- `pytest-cov` 6.3.0 - coverage reporting
- `pytest-xdist` 3.8.0 - parallel execution
- `pytest-env` 1.1.5 - environment variable management
- `Faker` 14.2.1 - test data generation

### 8.2 Recommended Additions

**`pytest-mock` (or `unittest.mock`)** - Already using `unittest.mock` effectively. No change needed, but ensure consistent use of `MagicMock` vs `Mock` vs `AsyncMock`.

**`respx`** - A library for mocking `httpx` requests at the transport level. Currently tests mock `_client.get/post/put/patch/delete` at the method level. `respx` would allow mocking at the HTTP transport level, making tests more realistic without requiring `AsyncMock` on every method.
```python
# Example with respx:
import respx, httpx

@respx.mock
async def test_get_workzones():
    respx.get("https://example.api.oracle.com/rest/ofscMetadata/v1/workZones").mock(
        return_value=httpx.Response(200, json={"items": [...], "totalResults": 1})
    )
    result = await async_instance.metadata.get_workzones()
    assert isinstance(result, WorkzoneListResponse)
```

**`hypothesis`** - Property-based testing for Pydantic model validation. Particularly useful for testing edge cases in `GetActivitiesParams`, `GetQuotaRequest`, and CSV-list models.

**`pytest-benchmark`** - Formalizes the performance assertions currently in `TestQuotaAPIPerformance`. Provides structured performance regression tracking.

### 8.3 Coverage Improvement Target

To reach the 80% minimum threshold, the following coverage improvements are needed:

| Module | Current | Target | Gap | Estimated Tests Needed |
|--------|---------|--------|-----|------------------------|
| `_base.py` | 15.4% | 80% | +65% | ~15 new test functions |
| `core.py` | 34.3% | 80% | +46% | ~10 new test functions |
| `resources.py` | 36.6% | 80% | +43% | ~12 new test functions |
| `metadata.py` (async) | 55.4% | 80% | +25% | ~8 new test functions |
| `users.py` (async) | 51.3% | 80% | +29% | ~6 new test functions |
| `capacity.py` (async) | 67% | 80% | +13% | ~4 new test functions |

Current total: 63.5%. Reaching 80% requires covering approximately 925 additional statements.

---

## 9. REQUIREMENTS TRACEABILITY

See `tests/REQUIREMENTS_TEST_MAPPING.md` for the detailed requirements-to-test mapping.

---

## 10. CONFIGURATION NOTES

### pyproject.toml `addopts` Analysis

```toml
addopts = "-n auto --dist worksteal -m 'not serial'"
```

**Issue:** The `addopts` only excludes `serial` from default runs. It does NOT exclude `integration` or `uses_real_data`. This means:
1. When `.env` exists with valid credentials, `integration` tests run by default
2. Users must explicitly run with `-m "not uses_real_data"` to get a credential-free run

**Recommendation:** Consider updating `addopts` to either:
- `-n auto --dist worksteal -m 'not serial and not uses_real_data'` (run only mocked by default)
- Or add documentation making it clear that the default run requires credentials

### asyncio_mode = "auto"

The `asyncio_mode = "auto"` setting causes `@pytest.mark.asyncio` decorators to be redundant but harmless. All async test functions are automatically treated as asyncio tests.

---

## 11. APPENDIX: TEST EXECUTION COMMANDS

```bash
# Run all mocked tests (recommended for CI without credentials)
uv run pytest tests/ -m "not uses_real_data and not integration" -v --tb=short

# Run mocked tests with coverage
uv run pytest tests/ -m "not uses_real_data and not integration" --cov=ofsc --cov-report=term-missing --cov-report=html

# Run async tests only (fastest, most comprehensive mocked coverage)
uv run pytest tests/async/ -m "not uses_real_data" -v --tb=short

# Run live tests (requires .env with valid OFSC credentials)
uv run pytest tests/ -m "uses_real_data" -v --tb=short

# Run integration tests (requires .env)
uv run pytest tests/ -m "integration" -v --tb=short

# Full suite
uv run pytest tests/ -v --tb=short

# Generate coverage HTML report
uv run pytest tests/ -m "not uses_real_data and not integration" --cov=ofsc --cov-report=html
# Open: htmlcov/index.html
```
