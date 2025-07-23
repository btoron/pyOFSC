# OFSC Python Wrapper v3.0 Implementation Plan

## Overview

This document provides a detailed implementation plan for the OFSC Python Wrapper v3.0, breaking down the work into manageable phases with specific tasks, deliverables, and acceptance criteria.

**IMPORTANT UPDATE (July 2025):** This plan has been significantly revised to reflect the actual implementation approach taken. The major change is the shift from dual sync/async clients to an **async-only** architecture.

## Implementation Phases

### Phase 1: Foundation and Breaking Changes (Weeks 1-4)

#### 1.1 Project Setup and Dependencies

**Tasks:**
- [ ] Update `pyproject.toml` to require Python 3.12+ (R1.1)
- [ ] Replace `requests` dependency with `httpx`
- [ ] Add `pytest-asyncio` for async testing
- [ ] Add `respx` for httpx mocking
- [ ] Update all development dependencies

**Deliverables:**
- Updated `pyproject.toml` with new dependencies
- Working test environment with async support

**Acceptance Criteria:**
- All existing tests pass with new dependencies
- Python 3.12+ enforcement works
- Async test fixtures are available

#### 1.2 Core HTTP Client Infrastructure

**Tasks:**
- [x] Create `client/base.py` with shared client logic
- [x] Implement `client/ofsc_client.py` using `httpx.AsyncClient()` (async-only)
- [x] ~~Implement `client/sync_client.py` using `httpx.Client()`~~ **REMOVED: Async-only architecture**
- [x] Create connection pooling configuration
- [x] Implement context manager support for async client

**Deliverables:**
- `OFSC` class with async-only methods
- ~~`OFSC` class with sync methods~~ **REMOVED**
- Proper resource cleanup via async context manager
- Backward compatibility via `ofsc.compat` wrapper

**Acceptance Criteria:**
- Async client can make HTTP requests
- Connection pooling is configured
- Async context manager properly closes connections
- Backward compatibility maintained through wrapper

#### 1.3 Authentication System

**Tasks:**
- [ ] Update authentication to use `client_id` and `client_secret` parameters (R5)
- [ ] Implement Basic Authentication for httpx (R5)
- [ ] Update OAuth2 implementation for httpx (R5)
- [ ] Add automatic token refresh for OAuth2 (R5)
- [ ] Update environment variable naming (`OFSC_INSTANCE`, etc.) (R5)

**Deliverables:**
- Basic auth working with httpx
- OAuth2 with automatic refresh
- Environment variable support

**Acceptance Criteria:**
- Basic auth works with both sync and async clients
- OAuth2 tokens refresh automatically
- Environment variables load correctly
- Credentials are never logged

#### 1.4 Pydantic Response Models (Split into 5 Subphases)

**Phase 1.4.0: Model Submodule Organization**
**Tasks:**
- [ ] Create `ofsc/models/` directory structure
- [ ] Split large models.py into focused submodules (base, metadata, core, capacity, auth)
- [ ] Create `ofsc/models/__init__.py` with backward-compatible re-exports
- [ ] Update all existing imports throughout codebase
- [ ] Verify no breaking changes to existing model imports

**Phase 1.4.1: BaseOFSResponse Foundation + Metadata Model Adaptation**
**Tasks:**
- [ ] Design `BaseOFSResponse` with raw httpx response access
- [ ] Adapt existing Metadata models for v3.0 integration
- [ ] Update response examples validation for Metadata models
- [ ] Integrate models with new client classes

**Phase 1.4.2: Core API Model Adaptation**
**Tasks:**
- [ ] Adapt existing Core models for v3.0 (Resource, Activity, Location, etc.)
- [ ] Add any missing Core models based on response examples
- [ ] Update Core API client integration with adapted models
- [ ] Extend model validation tests for Core API

**Phase 1.4.3: Capacity API Model Adaptation**
**Tasks:**
- [ ] Adapt existing Capacity models for v3.0 (CapacityArea, CapacityCategory, Quota, etc.)
- [ ] Validate complex capacity response structures
- [ ] Update Capacity API client integration
- [ ] Extend model validation tests for Capacity API

**Phase 1.4.4: Model Integration Finalization**
**Tasks:**
- [ ] Final integration of all adapted models with client classes
- [ ] Comprehensive model validation against all response examples
- [ ] Type hint enhancement for IDE support
- [ ] Model documentation and cross-API relationship validation

**Deliverables:**
- Organized model submodule structure with backward compatibility
- Adapted (not rewritten) Pydantic models for all API responses
- BaseOFSResponse class with httpx integration
- Complete model validation test suite

**Acceptance Criteria:**
- All existing `from ofsc.models import X` statements continue to work unchanged
- All 33+ response examples validate against adapted models
- Raw httpx response accessible via `model.raw_response`
- Type hints work correctly in IDEs
- Zero breaking changes to existing model field names

#### 1.5 Error Handling

**Tasks:**
- [ ] Create typed exception hierarchy
- [ ] Implement error context (status code, request details)
- [ ] Add retry logic with exponential backoff
- [ ] Implement circuit breaker pattern
- [ ] Remove configurable error handling (always raise)

**Deliverables:**
- Comprehensive exception types
- Retry mechanism with backoff
- Circuit breaker implementation

**Acceptance Criteria:**
- Specific exceptions for different error types
- Retry works for transient failures
- Circuit breaker prevents cascade failures
- All errors include request context

#### 1.6 API Endpoint Implementation (Split into 5 Subphases)

**1.6.1 Metadata API GET Endpoints**
**Tasks:**
- [ ] Migrate Metadata API GET endpoints to new architecture (get_properties, get_workskills, etc.)
- [ ] Implement internal request parameter validation for Metadata GET methods
- [ ] Update Metadata GET methods to return Pydantic models
- [ ] Add comprehensive validation tests for Metadata GET endpoints
- [ ] Verify backwards compatibility for Metadata GET methods

**1.6.2 Capacity API GET Endpoints**
**Tasks:**
- [ ] Migrate Capacity API GET endpoints to new architecture (get_capacity, get_capacity_areas, etc.)
- [ ] Implement internal request parameter validation for Capacity GET methods
- [ ] Update Capacity GET methods to return Pydantic models
- [ ] Add comprehensive validation tests for Capacity GET endpoints
- [ ] Verify backwards compatibility for Capacity GET methods

**1.6.3 Core API GET Endpoints**
**Tasks:**
- [ ] Migrate Core API GET endpoints to new architecture (get_activities, get_resources, get_users, etc.)
- [ ] Implement internal request parameter validation for Core GET methods
- [ ] Update Core GET methods to return Pydantic models
- [ ] Add comprehensive validation tests for Core GET endpoints
- [ ] Verify backwards compatibility for Core GET methods

**1.6.4 All APIs Non-GET Endpoints (POST/PUT/PATCH/DELETE)**
**Tasks:**
- [ ] Migrate all POST/PUT/PATCH/DELETE endpoints across Core, Metadata, and Capacity APIs
- [ ] Implement comprehensive request body validation using Pydantic models
- [ ] Update all modification methods to return appropriate Pydantic response models
- [ ] Add validation tests for all non-GET endpoint request/response cycles
- [ ] Verify backwards compatibility for all modification methods

**1.6.5 Integration Finalization and Testing**
**Tasks:**
- [ ] Complete end-to-end integration testing of all migrated endpoints
- [ ] Validate that all API methods work with both sync and async clients
- [ ] Ensure all methods properly use fault tolerance (retry + circuit breaker)
- [ ] Complete comprehensive API coverage testing against real OFSC environments
- [ ] Finalize backwards compatibility validation for entire API surface

**Deliverables:**
- All API endpoints working with new architecture
- Internal request validation for all endpoint types
- Model-based responses for all API calls
- Comprehensive test coverage for all endpoints

**Acceptance Criteria:**
- All existing functionality preserved across all API endpoints
- New methods return typed Pydantic models for all responses
- Internal request validation catches errors early before API calls
- Both sync and async variants work identically for all endpoints

### Phase 2: Enhanced Features (Weeks 5-7)

#### 2.1 Configuration System

**Tasks:**
- [ ] Implement Pydantic settings for configuration
- [ ] Add support for `config.toml` credentials file
- [ ] Create multiple configuration sources (env, file, code)
- [ ] Add configuration validation
- [ ] Implement URL auto-generation from instance name

**Deliverables:**
- Flexible configuration system
- config.toml support for credentials
- Auto URL generation

**Acceptance Criteria:**
- Configuration loads from multiple sources
- Precedence: env vars > .env > config.toml > defaults
- config.toml validates correctly
- URLs generate from instance names

#### 2.2 Logging and Monitoring

**Tasks:**
- [ ] Implement structured logging
- [ ] Add configurable log levels
- [ ] Integrate OpenTelemetry for distributed tracing
- [ ] Create debug mode with detailed logs
- [ ] Mask sensitive data in logs

**Deliverables:**
- Structured logging system
- OpenTelemetry integration
- Debug mode

**Acceptance Criteria:**
- Logs are structured (JSON format)
- Log levels configurable
- Tracing works with OpenTelemetry
- No credentials in logs
- Debug mode shows request/response details

#### 2.3 Security Enhancements

**Tasks:**
- [ ] Implement automatic OAuth2 token rotation
- [ ] Add audit logging for API calls
- [ ] Enforce HTTPS by default
- [ ] Add SSL certificate validation
- [ ] Ensure sensitive data masking

**Deliverables:**
- Enhanced security features
- Audit logging capability

**Acceptance Criteria:**
- OAuth2 tokens rotate automatically
- All API calls logged for audit
- HTTPS enforced
- SSL certificates validated
- Sensitive data masked in all logs

#### 2.4 Extensibility Framework

**Tasks:**
- [ ] Implement middleware/interceptor system
- [ ] Create plugin architecture for custom behaviors
- [ ] Add support for custom model validators
- [ ] Make response processing customizable

**Deliverables:**
- Middleware system
- Plugin architecture
- Custom validation support

**Acceptance Criteria:**
- Middleware can intercept requests/responses
- Custom behaviors can be plugged in
- Custom validators work with models
- Response processing is customizable

#### 2.5 Request Handling Enhancement

**Tasks:**
- [ ] Ensure simple parameter passing in public API
- [ ] Implement internal Pydantic validation
- [ ] Create clear validation error messages
- [ ] Hide validation implementation from public API

**Deliverables:**
- Clean public API
- Internal validation system

**Acceptance Criteria:**
- Public API uses simple parameters
- Internal validation catches errors
- Validation errors are clear
- Implementation is hidden from users

### Phase 3: Testing and Quality Assurance (Weeks 8-10)

#### 3.1 Comprehensive Test Suite

**Tasks:**
- [ ] Implement model validation tests against response examples
- [ ] Create mock tests using respx
- [ ] Build custom mock server for integration tests
- [ ] Add live environment tests
- [ ] Achieve 80% test coverage

**Deliverables:**
- Four-layer testing strategy implementation
- 80%+ test coverage
- Mock server for integration tests

**Acceptance Criteria:**
- All model validation tests pass
- Mock tests cover all scenarios
- Integration tests work with mock server
- Live tests work with real environments
- Coverage meets 80% target

#### 3.2 Type Safety and IDE Support

**Tasks:**
- [ ] Add comprehensive type hints throughout codebase
- [ ] Ensure mypy strict mode compatibility
- [ ] Implement generic types where appropriate
- [ ] Create type stubs for external dependencies
- [ ] Test IDE autocomplete and type checking

**Deliverables:**
- Full type safety
- mypy compatibility
- IDE support

**Acceptance Criteria:**
- mypy passes in strict mode
- IDEs provide good autocomplete
- Generic types work correctly
- Type stubs complete

#### 3.3 Configuration and Credential Management

**Tasks:**
- [ ] Test configuration precedence
- [ ] Validate config.toml structure
- [ ] Test environment variable loading
- [ ] Verify credential masking
- [ ] Test URL auto-generation

**Deliverables:**
- Robust configuration system
- Credential security

**Acceptance Criteria:**
- Configuration precedence works correctly
- config.toml validates properly
- Environment variables load
- Credentials never appear in logs
- URL generation works from instance

#### 3.4 Security and Monitoring Testing

**Tasks:**
- [ ] Test credential masking in logs
- [ ] Verify HTTPS enforcement
- [ ] Test SSL certificate validation
- [ ] Validate OpenTelemetry tracing
- [ ] Test structured logging

**Deliverables:**
- Security validation
- Monitoring verification

**Acceptance Criteria:**
- No credentials in any logs
- HTTPS enforced for all calls
- SSL certificates validated
- Tracing data collected
- Logs are properly structured

#### 3.5 Extensibility Testing

**Tasks:**
- [ ] Test middleware/interceptor functionality
- [ ] Validate custom behavior plugins
- [ ] Test custom model validators
- [ ] Verify response processing customization

**Deliverables:**
- Extensibility validation

**Acceptance Criteria:**
- Middleware works correctly
- Custom behaviors can be added
- Custom validators function
- Response processing is customizable

### Phase 4: Documentation and Migration (Weeks 11-12)

#### 4.1 Documentation

**Tasks:**
- [ ] Write comprehensive docstrings for all public APIs
- [ ] Create usage examples for all major features
- [ ] Develop migration guide from v2 to v3
- [ ] Write troubleshooting guide
- [ ] Update README with v3 information

**Deliverables:**
- Complete documentation set
- Migration guide
- Usage examples

**Acceptance Criteria:**
- All public APIs documented
- Examples work correctly
- Migration guide is clear
- Troubleshooting covers common issues

#### 4.2 Backwards Compatibility

**Tasks:**
- [x] ~~Implement OFSCV2 compatibility class~~ **CHANGED:** Implement ofsc.compat wrapper module
- [x] Add import compatibility for sync usage patterns
- [x] Create automatic sync wrapper for async methods
- [x] Document all breaking changes
- [x] Test compatibility layer

**Deliverables:**
- ofsc.compat compatibility wrapper module
- Breaking changes documentation
- Seamless migration path for v2 users

**Acceptance Criteria:**
- ofsc.compat module allows unchanged v2 code to work
- Simple import change enables compatibility
- Breaking changes are documented
- Migration path is clear

#### 4.3 Examples and Integration

**Tasks:**
- [ ] Update all code examples
- [ ] Create new examples showcasing v3 features
- [ ] Test examples against real API
- [ ] Update response examples
- [ ] Create integration examples

**Deliverables:**
- Updated examples
- Integration samples

**Acceptance Criteria:**
- All examples work with v3
- New features demonstrated
- Examples tested against API
- Integration patterns shown

#### 4.4 Performance and Optimization

**Tasks:**
- [ ] Profile async vs sync performance
- [ ] Optimize connection pooling settings
- [ ] Test concurrent request limits
- [ ] Validate memory usage
- [ ] Benchmark against v2

**Deliverables:**
- Performance validation
- Optimized settings

**Acceptance Criteria:**
- Performance meets expectations
- Connection pooling optimized
- Concurrent requests work
- Memory usage acceptable
- No regression from v2

#### 4.5 Release Preparation

**Tasks:**
- [ ] Final code review
- [ ] Complete test suite execution
- [ ] Version number update
- [ ] Release notes preparation
- [ ] Package building and testing

**Deliverables:**
- Release-ready package
- Release notes

**Acceptance Criteria:**
- All tests pass
- Package builds correctly
- Release notes are complete
- Version numbers updated

## Success Metrics

### Functional Requirements
- [ ] All 16 requirements (R1-R16) implemented and tested
- [ ] 80% test coverage achieved
- [ ] All breaking changes documented
- [ ] Backwards compatibility layer working

### Technical Requirements
- [ ] Python 3.12+ compatibility
- [ ] mypy strict mode passes
- [ ] Both sync and async clients working
- [ ] httpx integration complete

### Quality Requirements
- [ ] No credentials in logs
- [ ] SSL/HTTPS enforced
- [ ] OpenTelemetry tracing working
- [ ] Structured logging implemented

### User Experience
- [ ] Clear migration path from v2
- [ ] Comprehensive documentation
- [ ] Working examples
- [ ] IDE support with type hints

## Risk Mitigation

### Technical Risks
- **httpx Compatibility**: Extensive testing with current API patterns
- **Async Implementation**: Parallel development of sync and async
- **Breaking Changes**: Comprehensive compatibility layer

### Timeline Risks
- **Scope Creep**: Strict adherence to defined requirements
- **Testing Complexity**: Early test implementation in each phase
- **Documentation Lag**: Documentation written alongside code

### Quality Risks
- **Test Coverage**: Automated coverage reporting
- **Type Safety**: mypy integration in CI/CD
- **Security**: Security review in each phase

## Dependencies and Prerequisites

### External Dependencies
- Python 3.12+ environment
- httpx library compatibility
- pytest-asyncio for testing
- OpenTelemetry libraries

### Internal Dependencies
- Current v2 codebase understanding
- Response examples for model validation
- Test environment access
- Documentation infrastructure

## Deliverable Timeline

| Week | Phase | Key Deliverables |
|------|-------|------------------|
| 1 | 1.1-1.2 | Project setup, HTTP clients |
| 2 | 1.3 | Auth system |
| 3 | 1.4.0-1.4.2 | Model reorganization, Metadata & Core model adaptation |
| 4 | 1.4.3-1.4.4, 1.5 | Capacity models, integration, Error handling |
| 5 | 1.6.1-1.6.2 | Metadata & Capacity GET endpoints migration |
| 6 | 1.6.3-1.6.4 | Core GET endpoints, Non-GET methods migration |
| 7 | 1.6.5, Phase 1 Complete | API integration finalization, testing |
| 8 | 2.1-2.2 | Configuration, logging/monitoring |
| 9 | 2.3-2.4 | Security, extensibility |
| 10 | 2.5 | Request handling, Phase 2 complete |
| 11 | 3.1-3.2 | Testing suite, type safety |
| 12 | 3.3-3.4 | Config testing, security testing |
| 13 | 3.5 | Extensibility testing, Phase 3 complete |
| 14 | 4.1-4.2 | Documentation, backwards compatibility |
| 15 | 4.3-4.5 | Examples, release preparation |

## Acceptance Criteria Summary

### Phase 1 Complete When:
- [ ] All API endpoints work with httpx (58/242 completed)
- [x] ~~Both sync and async clients functional~~ **CHANGED:** Async-only client functional
- [x] Pydantic models replace all dict responses  
- [x] Authentication system migrated
- [x] Error handling implemented

### Phase 2 Complete When:
- [ ] Configuration system fully functional
- [ ] Logging and monitoring integrated
- [ ] Security features implemented
- [ ] Extensibility framework working
- [ ] Request validation internal

### Phase 3 Complete When:
- [ ] 80% test coverage achieved
- [ ] All test types implemented
- [ ] Type safety validated
- [ ] Security testing complete
- [ ] Extensibility tested

### Phase 4 Complete When:
- [ ] Documentation complete
- [ ] Migration guide available
- [ ] Backwards compatibility working
- [ ] Examples updated
- [ ] Package ready for release

## Final Release Criteria

The v3.0 release is ready when:
1. All 222 tasks completed (covering all 16 requirements R1-R16)
2. All acceptance criteria met
3. 80% test coverage achieved
4. mypy strict mode passes
5. All security requirements met
6. Documentation complete
7. Migration guide validated
8. Backwards compatibility tested
9. Performance validated
10. Package builds successfully