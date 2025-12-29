# Scripts Directory

This directory contains utility scripts for maintaining the pyOFSC project. These scripts help automate documentation, testing, and development workflows.

---

## Table of Contents

1. [update_endpoints_doc.py](#update_endpoints_docpy) - Automated endpoint documentation generator
2. [capture_api_responses.py](#capture_api_responsespy) - API response capture tool for testing

---

## update_endpoints_doc.py

**Purpose:** Automatically detects implemented OFSC API endpoints in the codebase and updates the `docs/ENDPOINTS.md` documentation with current implementation status.

### Features

- **AST-based Endpoint Detection**: Uses Python's Abstract Syntax Tree (AST) parser to accurately detect endpoints without relying on fragile regex patterns
- **Implementation Status Tracking**: Identifies which endpoints are implemented in sync client, async client, both, or neither
- **Version-aware Updates**: Only regenerates documentation when project version changes (unless forced)
- **Comprehensive Statistics**: Generates summary tables by module and HTTP method type
- **Endpoint ID Reference**: Maintains structured endpoint IDs (format: `XXYYYM`)

### Usage

```bash
# Update ENDPOINTS.md if version changed
uv run python scripts/update_endpoints_doc.py

# Force regeneration regardless of version
uv run python scripts/update_endpoints_doc.py --force
```

### How Endpoint Detection Works

The script uses **AST (Abstract Syntax Tree) analysis** to detect endpoints in Python source files. This approach is more reliable than regex-based parsing:

#### 1. URL Detection via `urljoin()` Calls

The script scans for all `urljoin()` function calls in the code:

```python
# Example from ofsc/async_client/metadata.py
url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/workZones")
```

When it finds a `urljoin()` call, it:
- Extracts the URL path from the second argument
- Handles both simple strings and f-strings with variables
- Normalizes path parameters: `/workZones/{label}` → `/workZones/{}`
- Filters for paths starting with `/rest/`

#### 2. HTTP Method Detection

Within the same function, the script looks for HTTP client method calls:

```python
# Examples detected
response = await self._client.get(url, ...)      # → GET
response = await self._client.post(url, ...)     # → POST
response = await self._client.put(url, ...)      # → PUT
response = await self._client.patch(url, ...)    # → PATCH
response = await self._client.delete(url, ...)   # → DELETE
```

#### 3. Stub Detection (Async Only)

For async client files, the script checks if a function raises `NotImplementedError`:

```python
async def some_endpoint(self):
    """Stub function - not yet implemented."""
    raise NotImplementedError("This endpoint is not yet implemented")
```

Endpoints with `NotImplementedError` are marked as **not implemented** even though the function exists.

#### 4. Matching URLs to Endpoints

The script:
1. Pairs each `urljoin()` call with the HTTP method call that follows it
2. Creates a tuple: `(normalized_path, http_method)`
3. Compares against the endpoint list in `docs/ENDPOINTS.md`
4. Updates status: `sync`, `async`, `both`, or `-` (not implemented)

### Endpoint ID Format

Endpoint IDs follow the pattern: `XXYYYM`

- **XX** = 2-character module code (`ME`, `CO`, `CA`, `AU`, etc.)
- **YYY** = 3-digit serial number (unique per path within module)
- **M** = HTTP method code (`G`, `P`, `U`, `A`, `D`)

**Examples:**
- `ME001G` = Metadata module, endpoint #1, GET
- `CO015P` = Core module, endpoint #15, POST
- `CA002A` = Capacity module, endpoint #2, PATCH

**Important:** When the same path has multiple HTTP methods, they share the same serial number but have different method letters:
- `ME002G` = GET `/rest/ofscMetadata/v1/activityTypeGroups/{label}`
- `ME002U` = PUT `/rest/ofscMetadata/v1/activityTypeGroups/{label}`

### Adding New Endpoints to Documentation

To add new endpoints to `docs/ENDPOINTS.md`:

1. **Manually add endpoint rows** to the endpoints table in `ENDPOINTS.md`:
   ```markdown
   | ID | Endpoint | Module | Method | Status |
   |------|---------------------------------------------------------|-------------|------|------|
   | ME999G | `/rest/ofscMetadata/v1/newResource` | metadata | GET | - |
   | ME999P | `/rest/ofscMetadata/v1/newResource` | metadata | POST | - |
   ```

2. **Run the update script** to detect implementation status:
   ```bash
   uv run python scripts/update_endpoints_doc.py --force
   ```

3. The script will:
   - Scan your implementation files
   - Update the status column automatically
   - Regenerate summary statistics

**Note:** The script does NOT add new endpoint rows automatically. You must add them manually to `ENDPOINTS.md` first. The script only updates the **Status** column and regenerates statistics.

### Finding Endpoints by Comments

While the script primarily uses AST analysis, you can help ensure endpoints are detected by following these patterns in your code:

```python
# GOOD - Easily detected by AST parser
async def get_workzones(self):
    """Get all workzones."""
    url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/workZones")
    response = await self._client.get(url, headers=self.headers)
    # ... rest of implementation

# GOOD - F-string paths are detected
async def get_workzone(self, label: str):
    """Get a single workzone."""
    url = urljoin(self.baseUrl, f"/rest/ofscMetadata/v1/workZones/{label}")
    response = await self._client.get(url, headers=self.headers)
    # ... rest of implementation

# BAD - URL constructed dynamically (may not be detected)
async def get_resource(self, path_parts: list[str]):
    """Get a resource."""
    path = "/".join(path_parts)
    url = urljoin(self.baseUrl, path)  # Dynamic path - won't be detected
    response = await self._client.get(url, headers=self.headers)
```

**Best Practices for Detectable Endpoints:**
- Use literal strings or f-strings in `urljoin()` calls
- Keep the `urljoin()` call and HTTP method call in the same function
- Avoid dynamically constructing URL paths from variables
- Use standard HTTP client methods: `get()`, `post()`, `put()`, `patch()`, `delete()`

### Module File Mapping

The script scans these implementation files:

| Module | Sync Client | Async Client |
|--------|-------------|--------------|
| core | `ofsc/core.py` | `ofsc/async_client/core.py` |
| metadata | `ofsc/metadata.py` | `ofsc/async_client/metadata.py` |
| capacity | `ofsc/capacity.py` | `ofsc/async_client/capacity.py` |
| auth | `ofsc/oauth.py` | `ofsc/async_client/oauth.py` |
| statistics | *(not implemented)* | *(not implemented)* |
| partscatalog | *(not implemented)* | *(not implemented)* |
| collaboration | *(not implemented)* | *(not implemented)* |

### Output

The script generates/updates `docs/ENDPOINTS.md` with:

1. **Metadata**
   - Current project version
   - Last updated date
   - Total endpoint count

2. **Endpoints Table**
   - All endpoints with ID, path, module, method, and status

3. **Implementation Summary**
   - Count of sync-only, async-only, both, and unimplemented endpoints

4. **Statistics Tables**
   - Breakdown by module and HTTP method type (GET, Write, DELETE)
   - Separate tables for sync and async clients
   - Totals with percentages

5. **Endpoint ID Reference**
   - Module codes, method codes, examples
   - Instructions for adding new endpoints

---

## capture_api_responses.py

**Purpose:** Captures real API responses from Oracle Field Service Cloud (OFSC) and saves them to JSON files for use in testing. This ensures tests validate against authentic API response structures.

### Features

- **Real API Testing**: Uses actual OFSC credentials to fetch live API responses
- **Comprehensive Coverage**: Captures both success (200) and error (404) responses
- **Organized Storage**: Saves responses to `tests/saved_responses/{category}/`
- **Metadata Tracking**: Includes request details, parameters, and context
- **Async Implementation**: Uses httpx for efficient parallel requests

### Prerequisites

Create a `.env` file in the project root with OFSC credentials:

```bash
OFSC_CLIENT_ID=your_client_id
OFSC_COMPANY=your_company_name
OFSC_CLIENT_SECRET=your_secret
OFSC_ROOT=optional_custom_root_url
```

### Usage

```bash
# Capture all configured endpoints
uv run python scripts/capture_api_responses.py
```

The script will:
1. Load credentials from `.env`
2. Make HTTP requests to all configured endpoints
3. Save responses to `tests/saved_responses/{category}/{name}.json`
4. Print progress and status for each request

### Configured Endpoint Categories

The script captures responses for these OFSC metadata categories:

- **workzones** - Workzone resources and hierarchies
- **properties** - Field properties and enumeration values
- **time_slots** - Time slot definitions
- **activity_type_groups** - Activity type group metadata
- **activity_types** - Activity type definitions
- **applications** - Application configurations and API access
- **capacity_areas** - Capacity area hierarchies
- **capacity_categories** - Capacity category definitions
- **forms** - Form templates
- **non_working_reasons** - Non-working reason codes
- **resource_types** - Resource type definitions
- **organizations** - Organization structures
- **link_templates** - Activity link templates
- **map_layers** - Map layer configurations
- **languages** - Language settings
- **inventory_types** - Inventory type definitions
- **routing_profiles** - Routing profile and plan data
- **shifts** - Shift definitions
- **work_skills** - Work skill metadata
- **work_skill_conditions** - Work skill condition rules
- **work_skill_groups** - Work skill group hierarchies

### Adding New Endpoints

To capture responses for new endpoints, add them to the `ENDPOINTS` dictionary in the script:

```python
ENDPOINTS = {
    "your_category": [
        {
            "name": "get_resource_200_success",
            "description": "Get all resources with pagination",
            "method": "GET",
            "path": "/rest/ofscMetadata/v1/resources",
            "params": {"offset": 0, "limit": 100},  # Optional query params
            "body": None,  # Optional request body for POST/PUT/PATCH
            "metadata": {},  # Optional context metadata
        },
        {
            "name": "get_resource_404_not_found",
            "description": "Get a non-existent resource",
            "method": "GET",
            "path": "/rest/ofscMetadata/v1/resources/NONEXISTENT_12345",
            "params": None,
            "body": None,
            "metadata": {"resource_label": "NONEXISTENT_12345"},
        },
    ],
}
```

**Endpoint Configuration Fields:**

- **name** (required): Filename for saved response (without `.json`)
- **description** (required): Human-readable description
- **method** (required): HTTP method (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`)
- **path** (required): API endpoint path (must start with `/rest/`)
- **params** (optional): Query parameters as dict
- **body** (optional): Request body as dict (for POST/PUT/PATCH)
- **metadata** (optional): Additional context (e.g., resource labels)

### Saved Response Format

Each saved response is a JSON file with this structure:

```json
{
  "description": "Get a single workzone by label",
  "status_code": 200,
  "headers": {
    "Content-Type": "application/json",
    "Cache-Control": "no-store, no-cache"
  },
  "request": {
    "url": "https://company.fs.ocs.oraclecloud.com/rest/ofscMetadata/v1/workZones/ALTAMONTE_SPRINGS",
    "method": "GET",
    "workzone_label": "ALTAMONTE_SPRINGS"
  },
  "response_data": {
    "label": "ALTAMONTE_SPRINGS",
    "name": "Altamonte Springs",
    "status": "active",
    "workZoneType": "moving",
    ...
  }
}
```

**For Error Responses (4xx, 5xx):**

```json
{
  "description": "Get a non-existent workzone",
  "status_code": 404,
  "headers": {
    "Content-Type": "application/json"
  },
  "request": {
    "url": "https://company.fs.ocs.oraclecloud.com/rest/ofscMetadata/v1/workZones/NONEXISTENT",
    "method": "GET",
    "workzone_label": "NONEXISTENT"
  },
  "body": "{\"type\": \"...\", \"title\": \"Not Found\", \"detail\": \"...\"}"
}
```

### Using Saved Responses in Tests

Load saved responses using `ResponseLoader` utility:

```python
import json
from pathlib import Path

def test_workzone_model_validation():
    """Test that Workzone model validates against saved response."""
    saved_response_path = (
        Path(__file__).parent.parent
        / "saved_responses"
        / "workzones"
        / "get_workzone_200_success.json"
    )

    with open(saved_response_path) as f:
        saved_data = json.load(f)

    # Validate against Pydantic model
    workzone = Workzone.model_validate(saved_data["response_data"])

    assert workzone.label == "ALTAMONTE_SPRINGS"
    assert workzone.status == "active"
```

This ensures your Pydantic models accurately represent real API responses.

### Best Practices

1. **Capture Both Success and Error Responses**
   - Always include 200 (success) and 404 (not found) responses
   - Add 400/422 for validation errors if applicable

2. **Use Real Resource Labels**
   - Use actual resource labels from your OFSC instance
   - Document which labels are environment-specific

3. **Update Regularly**
   - Re-capture responses when OFSC API versions change
   - Update when adding new fields or models

4. **Version Control**
   - Commit saved responses to git
   - Track changes to identify API breaking changes

5. **Protect Sensitive Data**
   - Never commit `.env` file with credentials
   - Review saved responses for PII before committing

---

## Development Workflow

### Adding a New Endpoint Implementation

1. **Capture API Responses** (if needed)
   ```bash
   # Add endpoint to ENDPOINTS dict in capture_api_responses.py
   uv run python scripts/capture_api_responses.py
   ```

2. **Implement the Method**
   - Add method to `ofsc/async_client/metadata.py` or other module
   - Follow existing patterns (use `urljoin()`, proper error handling)

3. **Update Documentation**
   ```bash
   # Force regenerate ENDPOINTS.md to detect new implementation
   uv run python scripts/update_endpoints_doc.py --force
   ```

4. **Create Tests**
   - Add tests to `tests/async/test_async_*.py`
   - Use saved responses for validation tests
   - Include both live (`@pytest.mark.uses_real_data`) and mock tests

5. **Verify**
   ```bash
   # Run tests
   uv run pytest tests/async/test_async_*.py -v

   # Check implementation status
   grep "your_endpoint" docs/ENDPOINTS.md
   ```

---

## Troubleshooting

### update_endpoints_doc.py

**Problem:** Endpoint not detected even though implemented

**Solutions:**
- Ensure `urljoin()` uses a string literal or f-string (not dynamic variable)
- Verify HTTP method call (`get`, `post`, etc.) is in the same function
- Check that URL path starts with `/rest/`
- Use `--force` to ignore version caching

**Problem:** Wrong implementation status

**Solutions:**
- Check for typos in endpoint path (case-sensitive)
- Verify parameter placeholders match: `{label}` in both ENDPOINTS.md and code
- Ensure async stubs raise `NotImplementedError` if not implemented

### capture_api_responses.py

**Problem:** Authentication fails

**Solutions:**
- Verify credentials in `.env` file
- Check `OFSC_CLIENT_ID` format: `{client_id}@{company_name}`
- Ensure `OFSC_CLIENT_SECRET` is correct
- Confirm network access to OFSC instance

**Problem:** 404 errors for valid endpoints

**Solutions:**
- Verify resource labels exist in your OFSC instance
- Check API version in path matches your instance
- Some resources may be tenant-specific

**Problem:** Timeout errors

**Solutions:**
- Increase timeout in script (default: 30 seconds)
- Check network connectivity
- Verify OFSC instance is responding

---

## Additional Resources

- [OFSC REST API Documentation](https://docs.oracle.com/en/cloud/saas/field-service/23c/cxfsc/c_rest_api.html)
- [pyOFSC README](../README.md)
- [Test Documentation](../tests/README.md) *(if exists)*
- [CLAUDE.md Development Guide](../CLAUDE.md)

---

## Contributing

When modifying these scripts:

1. **Test thoroughly** with various endpoint types
2. **Update this README** if behavior changes
3. **Follow code style**: Run `uv run ruff format scripts/`
4. **Add comments** for complex logic
5. **Preserve backward compatibility** when possible

---

**Last Updated:** 2025-12-29
**Maintained By:** pyOFSC Development Team
