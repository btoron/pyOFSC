#!/bin/bash
# Initial project setup script

# Create directory structure
mkdir -p tests/{unit,integration,fixtures,utils}
mkdir -p tests/unit/test_endpoints
mkdir -p tests/integration/test_endpoints
mkdir -p tests/fixtures/{parameters,requests,responses}
mkdir -p tests/fixtures/test_data/{activities,resources,users}
mkdir -p error_reports
mkdir -p docs/testing

# Create __init__.py files
touch tests/__init__.py
touch tests/unit/__init__.py
touch tests/integration/__init__.py
touch tests/fixtures/__init__.py
touch tests/utils/__init__.py

# Create requirements-test.txt
cat > requirements-test.txt << 'EOF'
# Core testing dependencies
pytest==7.4.0
pytest-asyncio==0.21.0
pytest-httpx==0.22.0
pytest-xdist==3.3.1
pytest-timeout==2.1.0
pytest-rerunfailures==11.1.2
pytest-env==0.8.2
pytest-cov==4.1.0

# HTTP mocking and testing
respx==0.20.1
httpx==0.24.1

# Data generation and validation
faker==19.6.1
pydantic==2.0.0
jsonschema==4.19.0
openapi-spec-validator==0.5.7

# Utilities
python-dotenv==1.0.0
allpairspy==2.5.0
pyyaml==6.0.1
pandas==2.0.3  # For test data analysis

# Reporting
pytest-html==3.2.0
pytest-json-report==1.5.0
EOF

# Create pytest.ini
cat > pytest.ini << 'EOF'
[tool:pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Markers for selective testing
markers =
    unit: Unit tests with mocked responses
    integration: Integration tests with real API
    slow: Tests that take > 5 seconds
    critical: Critical path tests
    cleanup: Tests that require cleanup
    rate_limited: Tests subject to rate limiting

# Default options
addopts = 
    -v
    --tb=short
    --strict-markers
    --cov=oracle_field_service_proxy
    --cov-report=term-missing
    --cov-report=html
    -m "not slow"

# Timeout settings
timeout = 300
timeout_method = thread

# Environment file
env_files =
    .env.test
EOF

# Create .env.test template
cat > .env.test << 'EOF'
# Oracle Field Service API Test Configuration
OFS_BASE_URL=https://sandbox.fs.ocs.oraclecloud.com
OFS_API_VERSION=v2
OFS_USERNAME=your_sandbox_username
OFS_PASSWORD=your_sandbox_password

# Test Configuration
TEST_CLEANUP_ENABLED=true
TEST_RATE_LIMIT_MAX_CONCURRENT=10
TEST_TIMEOUT_SECONDS=30
TEST_RETRY_ATTEMPTS=3

# Test Data Configuration
TEST_EXISTING_ACTIVITY_ID=
TEST_EXISTING_RESOURCE_ID=
TEST_EXISTING_USER_ID=
EOF

# Create conftest.py
cat > tests/conftest.py << 'EOF'
"""Global pytest configuration and fixtures"""
import os
import pytest
import asyncio
from typing import Dict, Any, List
from dotenv import load_dotenv
import httpx
from asyncio import Semaphore

# Load test environment variables
load_dotenv('.env.test')

# Import your proxy client here
# from oracle_field_service_proxy import OFSClient

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def sandbox_config() -> Dict[str, Any]:
    """Load sandbox configuration from environment"""
    return {
        "base_url": os.getenv("OFS_BASE_URL"),
        "version": os.getenv("OFS_API_VERSION"),
        "auth": (
            os.getenv("OFS_USERNAME"),
            os.getenv("OFS_PASSWORD")
        ),
        "cleanup_enabled": os.getenv("TEST_CLEANUP_ENABLED", "true").lower() == "true",
        "rate_limit": int(os.getenv("TEST_RATE_LIMIT_MAX_CONCURRENT", "10")),
        "timeout": int(os.getenv("TEST_TIMEOUT_SECONDS", "30"))
    }

@pytest.fixture(scope="session")
def rate_limiter():
    """Global rate limiter for concurrent calls"""
    limiters = {}
    
    def get_limiter(endpoint: str, limit: int = None):
        if limit is None:
            limit = int(os.getenv("TEST_RATE_LIMIT_MAX_CONCURRENT", "10"))
        
        if endpoint not in limiters:
            limiters[endpoint] = Semaphore(limit)
        return limiters[endpoint]
    
    return get_limiter

@pytest.fixture
async def client(sandbox_config):
    """Create authenticated OFS client"""
    # Replace with your actual client initialization
    # client = OFSClient(
    #     base_url=sandbox_config["base_url"],
    #     version=sandbox_config["version"],
    #     auth=sandbox_config["auth"],
    #     timeout=sandbox_config["timeout"]
    # )
    # return client
    pass

@pytest.fixture
def created_resources():
    """Track resources created during tests for cleanup"""
    resources = []
    yield resources
    
    # Cleanup will be handled by individual test classes
    # This just provides the tracking mechanism

@pytest.fixture(scope="session")
def test_data_ids(sandbox_config) -> Dict[str, str]:
    """Pre-existing test data IDs from sandbox"""
    return {
        "activity_id": os.getenv("TEST_EXISTING_ACTIVITY_ID"),
        "resource_id": os.getenv("TEST_EXISTING_RESOURCE_ID"),
        "user_id": os.getenv("TEST_EXISTING_USER_ID")
    }
EOF

echo "Project structure created successfully!"
echo "Next steps:"
echo "1. Install dependencies: pip install -r requirements-test.txt"
echo "2. Configure .env.test with your sandbox credentials"
echo "3. Add your proxy client import in tests/conftest.py"