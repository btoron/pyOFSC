"""Pytest configuration and fixtures for OFSC v3.0 tests following documented strategy."""

import os
import pytest
import asyncio
from unittest.mock import Mock
from pathlib import Path
import httpx
from dotenv import load_dotenv

# Import test configuration
from .config import load_test_config, TestEnvironmentConfig

# Import v3.0 modules using standard imports
from ofsc.client import OFSC
from ofsc.auth import BasicAuth, OAuth2Auth

# Load environment variables from .env file
load_dotenv()


# Configuration fixtures
@pytest.fixture(scope="session")
def test_config():
    """Load test configuration with precedence handling."""
    return load_test_config()


@pytest.fixture
def test_credentials():
    """Test credentials for mocked tests."""
    return {
        "instance": "test_instance",
        "client_id": "test_client_id",
        "client_secret": "test_client_secret"
    }


@pytest.fixture
def live_credentials(test_config):
    """Live credentials from configuration for integration tests."""
    # Try to get from test config first, then fall back to env vars
    env_config = test_config.environments.get("env")
    if env_config:
        return {
            "instance": env_config.instance,
            "client_id": env_config.client_id,
            "client_secret": env_config.client_secret
        }
    
    # Fallback to direct env var check
    instance = os.getenv('OFSC_INSTANCE')
    client_id = os.getenv('OFSC_CLIENT_ID')
    client_secret = os.getenv('OFSC_CLIENT_SECRET')
    
    if not all([instance, client_id, client_secret]):
        pytest.skip("Live credentials not available. Set OFSC_INSTANCE, OFSC_CLIENT_ID, OFSC_CLIENT_SECRET")
    
    return {
        "instance": instance,
        "client_id": client_id,
        "client_secret": client_secret
    }


# Authentication fixtures
@pytest.fixture
def basic_auth(test_credentials):
    """Basic authentication instance for testing."""
    return BasicAuth(
        instance=test_credentials["instance"],
        client_id=test_credentials["client_id"],
        client_secret=test_credentials["client_secret"]
    )


# Mock fixtures
@pytest.fixture
def mock_httpx_client():
    """Mock httpx.Client for unit testing."""
    mock_client = Mock(spec=httpx.Client)
    mock_response = Mock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success"}
    mock_response.text = '{"status": "success"}'
    mock_client.request.return_value = mock_response
    mock_client.is_closed = False
    return mock_client


# Client fixtures
@pytest.fixture
def async_client(test_credentials):
    """Async OFSC client for unit testing."""
    return OFSC(
        instance=test_credentials["instance"],
        client_id=test_credentials["client_id"],
        client_secret=test_credentials["client_secret"]
    )


@pytest.fixture
def live_async_client(live_credentials):
    """Live async OFSC client for integration tests."""
    return OFSC(
        instance=live_credentials["instance"],
        client_id=live_credentials["client_id"],
        client_secret=live_credentials["client_secret"]
    )


# Environment-specific client fixtures
@pytest.fixture
def dev_async_client(test_config):
    """Async client for dev environment."""
    env_config = test_config.environments.get("dev")
    if not env_config:
        pytest.skip("Dev environment not configured")
    
    return OFSC(
        instance=env_config.instance,
        client_id=env_config.client_id,
        client_secret=env_config.client_secret
    )


# Data fixtures
@pytest.fixture
def response_examples_path():
    """Path to response examples directory."""
    return Path(__file__).parent.parent / "response_examples"


@pytest.fixture
def test_data_path():
    """Path to test data directory."""
    return Path(__file__).parent / "data"


# Async test configuration using the modern approach
# Note: Removed event_loop fixture to use pytest-asyncio's default


# Test isolation fixtures
@pytest.fixture
def test_prefix():
    """Generate unique prefix for test isolation in live tests."""
    import uuid
    return f"PYTEST_{uuid.uuid4().hex[:8]}_"


# Mock server fixtures (placeholder for future implementation)
@pytest.fixture(scope="session")
def mock_server(test_config):
    """Mock server fixture for integration tests."""
    # Placeholder - will be implemented in Phase 2
    pytest.skip("Mock server not yet implemented")


# Test markers configuration
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests (no external dependencies)"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (may require live credentials)"
    )
    config.addinivalue_line(
        "markers", "live: marks tests as live environment tests (requires real OFSC instance)"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running tests"
    )


# Debug fixtures
@pytest.fixture
def debug_mode(test_config):
    """Enable debug mode based on configuration."""
    return test_config.debug_on_failure


# Environment selection
def pytest_addoption(parser):
    """Add command line options for test execution."""
    parser.addoption(
        "--env",
        action="store",
        default="dev",
        help="Test environment to use: dev, staging, prod"
    )
    parser.addoption(
        "--live",
        action="store_true",
        default=False,
        help="Run live tests against real OFSC instance"
    )


@pytest.fixture
def test_env(request):
    """Get the test environment from command line."""
    return request.config.getoption("--env")


@pytest.fixture
def run_live_tests(request):
    """Determine if live tests should be run."""
    return request.config.getoption("--live")


# Parametrized client fixtures for async-only testing
@pytest.fixture
def client(async_client):
    """Client fixture for async-only testing."""
    return async_client


# Error handling and debugging
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Generate detailed debug logs on test failure."""
    outcome = yield
    rep = outcome.get_result()
    
    if rep.when == "call" and rep.failed:
        # Create debug directory
        debug_dir = Path("test_debug") / item.nodeid.replace("/", "_").replace("::", "_")
        debug_dir.mkdir(parents=True, exist_ok=True)
        
        # Save test context if debug mode is enabled
        try:
            config = load_test_config()
            if config.debug_on_failure:
                import json
                from datetime import datetime
                
                with open(debug_dir / "context.json", "w") as f:
                    json.dump({
                        "test": item.nodeid,
                        "timestamp": datetime.now().isoformat(),
                        "environment": getattr(item, "test_env", "unknown"),
                        "error": str(rep.longrepr)
                    }, f, indent=2)
        except Exception:
            # Don't fail if debug saving fails
            pass