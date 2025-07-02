"""Pytest configuration and fixtures for OFSC v3.0 tests following documented strategy."""

import os
import pytest
from unittest.mock import Mock
from pathlib import Path
import httpx
from dotenv import load_dotenv

# Import test configuration
from .config import load_test_config

# Import v3.0 modules using standard imports
from ofsc.client import OFSC
from ofsc.auth import BasicAuth

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
def async_client(test_credentials, rate_limiting_enabled):
    """Async OFSC client for unit testing."""
    if rate_limiting_enabled:
        from ofsc.testing import create_test_client
        return create_test_client(
            instance=test_credentials["instance"],
            client_id=test_credentials["client_id"],
            client_secret=test_credentials["client_secret"]
        )
    else:
        return OFSC(
            instance=test_credentials["instance"],
            client_id=test_credentials["client_id"],
            client_secret=test_credentials["client_secret"]
        )


@pytest.fixture
def live_async_client(live_credentials, rate_limiting_enabled):
    """Live async OFSC client for integration tests."""
    if rate_limiting_enabled:
        from ofsc.testing import create_test_client
        return create_test_client(
            instance=live_credentials["instance"],
            client_id=live_credentials["client_id"],
            client_secret=live_credentials["client_secret"]
        )
    else:
        return OFSC(
            instance=live_credentials["instance"],
            client_id=live_credentials["client_id"],
            client_secret=live_credentials["client_secret"]
        )


@pytest.fixture
def async_client_basic_auth(live_credentials, rate_limiting_enabled):
    """Async OFSC client with Basic Auth for live testing."""
    if rate_limiting_enabled:
        from ofsc.testing import create_test_client
        return create_test_client(
            instance=live_credentials["instance"],
            client_id=live_credentials["client_id"],
            client_secret=live_credentials["client_secret"],
            use_token=False,  # Use Basic Auth
        )
    else:
        return OFSC(
            instance=live_credentials["instance"],
            client_id=live_credentials["client_id"],
            client_secret=live_credentials["client_secret"],
            use_token=False,  # Use Basic Auth
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
    """Configure pytest markers and parallel execution fallback."""
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
    
    # Implement fallback strategy for parallel execution
    _implement_parallel_fallback(config)


def _implement_parallel_fallback(config):
    """Implement fallback strategy when parallel execution fails."""
    # Check if pytest-xdist is available and working
    try:
        import xdist
        
        # Check if we're running with -n flag but xdist failed to start
        if hasattr(config.option, 'numprocesses') and config.option.numprocesses:
            # Store original value in case we need to fall back
            config._original_numprocesses = config.option.numprocesses
            
    except ImportError:
        # pytest-xdist not available, force sequential mode
        if hasattr(config.option, 'numprocesses'):
            config.option.numprocesses = None
        
        # Set environment variable to disable parallel mode
        os.environ['PYTEST_DISABLE_PARALLEL'] = 'true'
        
        print("\n⚠️  pytest-xdist not available, falling back to sequential execution")


def pytest_sessionstart(session):
    """Handle session start with parallel execution validation."""
    config = session.config
    
    # Check for worker startup failures
    if hasattr(config, 'workerinput'):
        # We're running as a worker, validate setup
        _validate_worker_setup(config)
    else:
        # We're the main process, validate parallel setup
        _validate_parallel_setup(config)


def _validate_worker_setup(config):
    """Validate that worker setup is correct."""
    try:
        # Import our testing utilities to ensure they work
        from ofsc.testing import get_global_rate_limiter
        
        # Test rate limiter initialization
        rate_limiter = get_global_rate_limiter()
        
    except Exception as e:
        print(f"\n❌ Worker setup validation failed: {e}")
        print("This may indicate an issue with parallel test configuration.")


def _validate_parallel_setup(config):
    """Validate that parallel execution setup is correct."""
    # Check if running with multiple workers
    if hasattr(config.option, 'numprocesses') and config.option.numprocesses:
        num_workers = config.option.numprocesses
        if num_workers == 'auto':
            num_workers = os.cpu_count()
        
        print(f"\n🚀 Starting parallel execution with {num_workers} workers")
        
        # Set environment variables for worker coordination
        os.environ['PYTEST_PARALLEL_WORKERS'] = str(num_workers)
        os.environ['PYTEST_RATE_LIMITED'] = 'true'
        
        # Validate dependencies
        try:
            import xdist
            from ofsc.testing import get_global_rate_limiter
            print("✅ Parallel execution dependencies validated")
        except ImportError as e:
            print(f"❌ Missing parallel execution dependency: {e}")
            print("Falling back to sequential execution")
            config.option.numprocesses = None
            os.environ['PYTEST_DISABLE_PARALLEL'] = 'true'
    else:
        print("\n📋 Running in sequential mode")


# Worker failure handling
def pytest_runtest_logreport(report):
    """Handle test reports and detect worker failures."""
    if report.when == "call" and report.failed:
        # Check if this is a rate limiting related failure
        if hasattr(report, 'longrepr') and report.longrepr:
            error_text = str(report.longrepr).lower()
            
            if '429' in error_text or 'rate limit' in error_text:
                print(f"\n⚠️  Rate limiting detected in test: {report.nodeid}")
                
                # Could implement automatic retry or worker throttling here
                # For now, just log the occurrence
                
    elif report.when == "setup" and report.failed:
        # Setup failures might indicate worker startup issues
        if hasattr(report, 'longrepr') and report.longrepr:
            error_text = str(report.longrepr).lower()
            
            if 'worker' in error_text or 'xdist' in error_text:
                print(f"\n❌ Possible worker setup failure: {report.nodeid}")


def pytest_keyboard_interrupt(excinfo):
    """Handle keyboard interrupts gracefully."""
    print("\n🛑 Test execution interrupted by user")
    
    # Clean up any rate limiting resources
    try:
        from ofsc.testing import get_global_rate_limiter
        rate_limiter = get_global_rate_limiter()
        # Reset any pending requests
    except:
        pass


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
    parser.addoption(
        "--parallel",
        action="store_true",
        default=True,
        help="Run tests in parallel (default)"
    )
    parser.addoption(
        "--sequential",
        action="store_true",
        default=False,
        help="Run tests sequentially"
    )


@pytest.fixture
def test_env(request):
    """Get the test environment from command line."""
    return request.config.getoption("--env")


@pytest.fixture
def run_live_tests(request):
    """Determine if live tests should be run."""
    return request.config.getoption("--live")


@pytest.fixture
def parallel_execution(request):
    """Determine if tests should run in parallel."""
    # Check command line options
    if request.config.getoption("--sequential"):
        return False
    if request.config.getoption("--parallel"):
        return True
    
    # Check environment variable
    disable_parallel = os.environ.get('PYTEST_DISABLE_PARALLEL', '').lower()
    if disable_parallel in ('true', '1', 'yes'):
        return False
    
    # Default to parallel
    return True


@pytest.fixture
def rate_limiting_enabled():
    """Check if rate limiting should be enabled for this test run."""
    return os.environ.get('PYTEST_RATE_LIMITED', '').lower() in ('true', '1', 'yes')


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
        # Create worker-safe debug directory
        import threading
        worker_id = getattr(item.config, 'workerinput', {}).get('workerid', 'main')
        process_id = os.getpid()
        thread_id = threading.get_ident()
        
        # Include worker ID, process ID, and timestamp for uniqueness
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        
        debug_dir = (Path("test_debug") / 
                    f"worker_{worker_id}" / 
                    f"pid_{process_id}" / 
                    f"thread_{thread_id}" /
                    f"{timestamp}_{item.nodeid.replace('/', '_').replace('::', '_')}")
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