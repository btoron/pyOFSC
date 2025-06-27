# OFSC Python Wrapper v3.0 Design Decisions

## Overview

This document captures key design decisions made during the development of OFSC Python Wrapper v3.0. These decisions provide the rationale and constraints for implementation choices.

## Authentication Design

### Decision: Dual Authentication Support
**Context**: The library needs to support different authentication methods for various use cases.

**Decision**: Support both Basic Authentication and OAuth2 as separate authentication methods.

**Implementation**:
- **Basic Authentication**: Uses `client_id` and `client_secret`
- **OAuth2**: Separate authentication class with automatic token refresh

**Rationale**: 
- Provides flexibility for different deployment scenarios
- Maintains compatibility with existing authentication patterns
- Allows for future authentication method additions

**Example**:
```python
# Basic Auth with client credentials
client = OFSC(instance="demo", client_id="id", client_secret="secret")

# Basic Auth with user credentials  
client = OFSC(instance="demo", username="user", password="pass")

# OAuth2 (separate class)
oauth_client = OAuth2Client(instance="demo", client_id="id", client_secret="secret")
client = OFSC(instance="demo", auth=oauth_client)
```

## Response Model Access Pattern

### Decision: Public Read-Only Property for Raw Response Access
**Context**: Users need access to underlying HTTP response details while maintaining clean model interface.

**Decision**: Provide raw response access via public read-only property on response models.

**Implementation**:
```python
class BaseOFSResponse(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    _raw_response: Optional[httpx.Response] = None
    
    @property
    def raw_response(self) -> Optional[httpx.Response]:
        """Access the underlying httpx Response object if available."""
        return self._raw_response

# Usage
activity = await client.core.get_activity("123")
print(activity.activity_id)  # Typed model access
print(activity.raw_response.status_code)  # Raw response access
print(activity.raw_response.headers)  # Headers via raw response
```

**Rationale**:
- Maintains clean separation between model data and HTTP details
- Provides escape hatch for advanced users
- Read-only prevents accidental modification
- Consistent access pattern across all response models

**Constraints**:
- Status code and headers accessed via `raw_response` (no convenience properties)
- Raw response may be None in testing scenarios
- Implementation detail (_raw_response) is private

## Exception Hierarchy Design

### Decision: Flat Generic Exception Hierarchy (Maximum 10 Types)
**Context**: Need balance between specificity and maintainability in error handling.

**Decision**: Implement a flat hierarchy with maximum 10 generic exception types.

**Implementation**:
```python
# Base exception
class OFSCException(Exception):
    """Base exception for all OFSC errors."""
    
# Core exception types (max 10)
class OFSCAPIException(OFSCException):
    """API-related errors (4xx, 5xx responses)."""
    
class OFSCValidationException(OFSCException):
    """Input validation errors."""
    
class OFSCAuthenticationException(OFSCException):
    """Authentication/authorization errors."""
    
class OFSCConnectionException(OFSCException):
    """Network/connection errors."""
    
class OFSCTimeoutException(OFSCException):
    """Request timeout errors."""
    
class OFSCRetryExhaustedException(OFSCException):
    """Retry mechanism exhausted."""
    
class OFSCCircuitBreakerException(OFSCException):
    """Circuit breaker triggered."""
    
class OFSCConfigurationException(OFSCException):
    """Configuration/setup errors."""
    
class OFSCSerializationException(OFSCException):
    """Model serialization/deserialization errors."""
```

**Rationale**:
- Avoids complex inheritance hierarchies
- Easier to understand and maintain
- Sufficient granularity for most use cases
- Prevents exception proliferation

**Constraints**:
- No HTTP status code specific exceptions (404NotFound, etc.)
- Generic categories only
- Flat hierarchy (no sub-exceptions)
- Maximum 10 exception types total

## Test Environment Configuration

### Decision: Separate Test Configuration File
**Context**: Test configuration needs to be isolated from main application configuration.

**Decision**: Use separate `config.test.toml` file for all test-related configuration.

**Implementation**:
```toml
# config.test.toml (test-specific)
[test]
coverage_target = 80
report_format = "html"
debug_on_failure = true

[test.environments.dev]
url = "https://dev.ofsc.example.com"
client_id = "dev_client_id"
client_secret = "dev_client_secret"
instance = "dev_instance"

# config.toml (main application)
[credentials]
instance = "your_instance"
client_id = "your_client_id"
client_secret = "your_client_secret"
```

**Environment Variable Pattern**:
```bash
# Test environment variables
OFSC_TEST_ENVIRONMENTS_DEV_INSTANCE=dev_instance
OFSC_TEST_ENVIRONMENTS_DEV_CLIENT_ID=dev_client_id

# Main application environment variables
OFSC_INSTANCE=your_instance
OFSC_CLIENT_ID=your_client_id
```

**Rationale**:
- Clear separation of concerns
- Prevents test configuration from affecting production
- Allows different configuration structures for different purposes
- Supports multiple test environments

## Security Audit Logging Format

### Decision: Structured JSON Logging with Configurable Fields
**Context**: Need consistent, parseable audit logs for security compliance.

**Decision**: Use structured JSON format with configurable field inclusion.

**Implementation**:
```python
# Audit log entry format
{
    "timestamp": "2024-12-27T10:30:00Z",
    "event_type": "api_request",
    "user_id": "masked_user_id",
    "instance": "demo",
    "endpoint": "/rest/ofscCore/v1/activities",
    "method": "GET",
    "status_code": 200,
    "request_id": "uuid-request-id",
    "ip_address": "masked_ip",
    "user_agent": "ofsc-python-wrapper/3.0.0",
    "response_time_ms": 145,
    "error_code": null,
    "error_message": null
}

# Configuration
[logging.audit]
enabled = true
level = "INFO"
format = "json"
include_ip = false  # PII masking
include_user_agent = true
mask_credentials = true
```

**Rationale**:
- Machine-readable format for SIEM systems
- Configurable to meet different compliance requirements
- Built-in PII masking capabilities
- Standard fields for consistency

**Constraints**:
- No credentials or sensitive data in logs
- IP addresses masked by default
- User IDs hashed or masked
- Configurable field inclusion for privacy compliance

## Connection Pool Configuration

### Decision: httpx-based Connection Pool with Sensible Defaults
**Context**: Need efficient connection reuse while allowing customization.

**Decision**: Use httpx's built-in connection pooling with configurable parameters.

**Implementation**:
```python
# Configuration structure
[connection_pool]
max_connections = 20
max_keepalive_connections = 10
keepalive_expiry = 30.0  # seconds
timeout = 30.0  # seconds
retries = 3
retry_delay = 1.0  # seconds
max_retry_delay = 10.0

# Usage in client
limits = httpx.Limits(
    max_connections=config.max_connections,
    max_keepalive_connections=config.max_keepalive_connections,
    keepalive_expiry=config.keepalive_expiry
)

timeout = httpx.Timeout(config.timeout)

client = httpx.AsyncClient(limits=limits, timeout=timeout)
```

**Default Values**:
- **max_connections**: 20 (total pool size)
- **max_keepalive_connections**: 10 (reusable connections)
- **keepalive_expiry**: 30 seconds
- **timeout**: 30 seconds
- **retries**: 3 attempts
- **retry_delay**: 1 second initial delay

**Rationale**:
- Leverages httpx's mature connection pooling
- Sensible defaults for most use cases
- Configurable for high-load scenarios
- Automatic connection cleanup

**Constraints**:
- Uses httpx limits and timeout objects
- Pool configuration applies to entire client instance
- Cannot configure per-endpoint timeouts
- Connection limits shared between sync and async clients

## Parameter Naming Convention

### Decision: Instance-Based Naming with Backwards Compatibility
**Context**: Need clear, consistent parameter naming that reflects OFSC terminology.

**Decision**: Use `instance` parameter for OFSC instance identification, maintain backwards compatibility.

**Implementation**:
```python
# v3.0 (new)
client = OFSC(instance="demo", client_id="id", client_secret="secret")

# v2.x compatibility (OFSCV2 class)
client_v2 = OFSCV2(company="demo", clientID="id", secret="secret")
client_v2 = OFSCV2(companyName="demo", clientID="id", secret="secret")
```

**Rationale**:
- `instance` clearly indicates OFSC instance identification
- Removes confusion between authentication and instance parameters
- Maintains backwards compatibility via separate class
- Aligns with OFSC terminology

**Migration Path**:
1. v2 users continue using OFSCV2 class
2. New code uses v3 OFSC class with `instance` parameter
3. Deprecation warnings guide migration
4. OFSCV2 maintained until v4.0

## Backwards Compatibility Strategy

### Decision: Separate OFSCV2 Implementation
**Context**: Need to maintain compatibility while allowing v3 innovation.

**Decision**: Implement OFSCV2 as separate class with identical v2 signatures.

**Implementation**:
```python
# OFSCV2 class maintains exact v2.x signatures
class OFSCV2:
    def __init__(self, company=None, companyName=None, clientID=None, secret=None, ...):
        # Exact same signature as v2.14.1
        
    def get_activities(self, response_type='OBJ', ...):
        # Exact same signature as v2.14.1
        
# Usage - identical to v2
client = OFSCV2(company="demo", clientID="id", secret="secret")
activities = client.get_activities(response_type='FULL')
```

**Rationale**:
- Zero breaking changes for existing v2 users
- Allows v3 to implement new patterns without constraints
- Clear migration path and timeline
- Separate maintenance and testing

**Lifecycle**:
- OFSCV2 maintained until v4.0 release
- Deprecation warnings in OFSCV2 starting v3.1
- Migration utilities provided
- Full removal in v4.0

## Configuration Precedence

### Decision: Environment Variables Override File Configuration
**Context**: Need predictable configuration loading for different deployment scenarios.

**Decision**: Implement strict precedence hierarchy.

**Precedence Order**:
1. **Environment Variables** (highest priority)
2. **config.toml file** (application directory)
3. **Default values** (lowest priority)

**Implementation**:
```python
# Environment variables
OFSC_INSTANCE=prod_override
OFSC_CLIENT_ID=env_client_id

# config.toml
[credentials]
instance = "default_instance"  # Overridden by env var
client_id = "file_client_id"   # Overridden by env var
client_secret = "file_secret"  # Used (no env override)
```

**Rationale**:
- Environment variables allow deployment-specific overrides
- File configuration provides sensible defaults
- Predictable behavior across environments
- Supports containerized deployments

**Constraints**:
- No runtime configuration changes
- Environment variables must match specific patterns
- File configuration validated on startup
- Missing required configuration raises startup error

## Type Safety Strategy

### Decision: Full Type Hint Coverage with mypy Strict Mode
**Context**: Need maximum type safety for large-scale usage.

**Decision**: Implement comprehensive type hints compatible with mypy strict mode.

**Requirements**:
- All public methods have complete type hints
- All parameters and return types specified
- Generic types used where appropriate
- Optional/Union types explicit
- Type stubs for external dependencies

**Implementation Example**:
```python
from typing import Optional, List, Union, TypeVar, Generic
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

class OFSResponseList(BaseModel, Generic[T]):
    items: List[T]
    total_results: int
    limit: int
    offset: int

async def get_activities(
    self,
    date: Optional[str] = None,
    resource_id: Optional[str] = None
) -> OFSResponseList[Activity]:
    ...
```

**Rationale**:
- Prevents runtime type errors
- Enables excellent IDE support
- Supports gradual typing adoption
- Industry best practice for libraries

**Quality Gates**:
- mypy strict mode must pass
- IDE autocomplete fully functional
- Type hints tested in CI/CD
- Type stubs maintained for dependencies

---

## Document Metadata

**Version**: 1.0  
**Last Updated**: December 27, 2024  
**Status**: Draft  
**Reviewers**: TBD  

**Change History**:
- v1.0: Initial design decisions documentation