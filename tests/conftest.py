"""Pytest configuration and fixtures for OFSC v3.0 tests following documented strategy."""

import os
from pathlib import Path
from unittest.mock import Mock

import httpx
import pytest
from dotenv import load_dotenv

from ofsc.auth import BasicAuth

# Import v3.0 modules using standard imports
from ofsc.client import OFSC

# Import test configuration
from .config import load_test_config

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
        "client_secret": "test_client_secret",
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
            "client_secret": env_config.client_secret,
        }

    # Fallback to direct env var check
    instance = os.getenv("OFSC_INSTANCE")
    client_id = os.getenv("OFSC_CLIENT_ID")
    client_secret = os.getenv("OFSC_CLIENT_SECRET")

    if not all([instance, client_id, client_secret]):
        pytest.skip(
            "Live credentials not available. Set OFSC_INSTANCE, OFSC_CLIENT_ID, OFSC_CLIENT_SECRET"
        )

    return {
        "instance": instance,
        "client_id": client_id,
        "client_secret": client_secret,
    }


# Authentication fixtures
@pytest.fixture
def basic_auth(test_credentials):
    """Basic authentication instance for testing."""
    return BasicAuth(
        instance=test_credentials["instance"],
        client_id=test_credentials["client_id"],
        client_secret=test_credentials["client_secret"],
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
            client_secret=test_credentials["client_secret"],
        )
    else:
        return OFSC(
            instance=test_credentials["instance"],
            client_id=test_credentials["client_id"],
            client_secret=test_credentials["client_secret"],
        )


@pytest.fixture
def live_async_client(live_credentials, rate_limiting_enabled):
    """Live async OFSC client for integration tests."""
    if rate_limiting_enabled:
        from ofsc.testing import create_test_client

        return create_test_client(
            instance=live_credentials["instance"],
            client_id=live_credentials["client_id"],
            client_secret=live_credentials["client_secret"],
        )
    else:
        return OFSC(
            instance=live_credentials["instance"],
            client_id=live_credentials["client_id"],
            client_secret=live_credentials["client_secret"],
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
        client_secret=env_config.client_secret,
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
    """Configure pytest markers and auto-parallel execution."""
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests (no external dependencies)"
    )
    config.addinivalue_line(
        "markers",
        "integration: marks tests as integration tests (may require live credentials)",
    )
    config.addinivalue_line(
        "markers",
        "live: marks tests as live environment tests (requires real OFSC instance)",
    )
    config.addinivalue_line("markers", "slow: marks tests as slow running tests")

    # Implement auto-parallel configuration
    _configure_auto_parallel(config)

    # Implement fallback strategy for parallel execution
    _implement_parallel_fallback(config)
    
    # NEW: Configure optimal distribution based on test mix
    if hasattr(config.option, 'include_e2e') and config.option.include_e2e:
        # Set environment variable for loadfile mode
        os.environ["PYTEST_XDIST_MODE"] = "loadfile"
        
        # Override dist mode if not manually set
        if hasattr(config.option, "dist") and config.option.dist == "loadscope":
            config.option.dist = "loadfile"


def _configure_auto_parallel(config):
    """Configure automatic parallel execution based on test paths and environment."""
    # Store command line option for later use
    if hasattr(config.option, 'include_e2e'):
        _should_include_slow_tests._include_e2e = config.option.include_e2e

    # Check if user explicitly disabled parallel execution
    if os.environ.get("PYTEST_DISABLE_PARALLEL", "").lower() in ("true", "1", "yes"):
        # Remove parallel options if they exist
        if hasattr(config.option, "numprocesses"):
            config.option.numprocesses = None
        print("\n📋 Parallel execution disabled via environment variable")
        return

    # Check if user already specified -n flag manually
    if (
        hasattr(config.option, "numprocesses")
        and config.option.numprocesses is not None
    ):
        print(f"\n🔧 Manual worker count specified: {config.option.numprocesses}")
        return

    # Check if we're being called from the run_tests_parallel.py script
    if os.environ.get("PYTEST_CURRENT_CATEGORY"):
        print("\n🔄 Auto-parallel skipped: using run_tests_parallel.py script")
        return

    # Analyze test paths to determine optimal worker count
    test_paths = getattr(config.option, "file_or_dir", [])
    if not test_paths:
        test_paths = ["tests/"]

    optimal_workers = _calculate_optimal_workers(test_paths)

    if optimal_workers > 1:
        # Set the number of workers
        config.option.numprocesses = optimal_workers

        # Determine if rate limiting should be enabled
        enable_rate_limiting = _should_enable_rate_limiting(test_paths)
        if enable_rate_limiting:
            os.environ["PYTEST_RATE_LIMITED"] = "true"

        # Set timeout for end-to-end tests
        is_end_to_end = _is_end_to_end_tests(test_paths)
        if is_end_to_end and not hasattr(config.option, "timeout"):
            config.option.timeout = 300  # 5 minutes for E2E tests

        # Provide user feedback about what's being executed
        _print_execution_status(test_paths, optimal_workers, enable_rate_limiting)
    else:
        print("\n📋 Sequential execution (auto-parallel analysis)")


def _calculate_optimal_workers(test_paths):
    """Calculate optimal number of workers based on test paths."""
    # Convert to Path objects for easier analysis
    from pathlib import Path

    paths = [Path(p) for p in test_paths]

    # Check for explicit worker count override
    if "PYTEST_WORKERS" in os.environ:
        try:
            return int(os.environ["PYTEST_WORKERS"])
        except ValueError:
            pass
    
    # Check if we're using loadfile distribution
    # This is set when using the optimized config
    if os.environ.get("PYTEST_XDIST_MODE") == "loadfile":
        # Use maximum workers for loadfile distribution
        return min(os.cpu_count() or 1, 8)

    # Analyze path patterns to determine test category
    categories = set()

    for path in paths:
        path_str = str(path).lower()

        # Check if this is the top-level tests directory
        if path_str.endswith("tests") or path_str.endswith("tests/"):
            # This is a mixed scenario - we need to analyze subdirectories
            import glob
            test_files = glob.glob(str(Path(path) / "**/test_*.py"), recursive=True)
            for test_file in test_files:
                test_file_str = test_file.lower()
                if "unit" in test_file_str:
                    categories.add("unit")
                elif "model" in test_file_str:
                    categories.add("models")
                elif "end_to_end" in test_file_str or "e2e" in test_file_str:
                    categories.add("end_to_end")
                elif "integration" in test_file_str:
                    categories.add("integration")
                elif "live" in test_file_str:
                    categories.add("live")
        elif "unit" in path_str:
            categories.add("unit")
        elif "model" in path_str:
            categories.add("models")
        elif "end_to_end" in path_str or "e2e" in path_str:
            categories.add("end_to_end")
        elif "integration" in path_str:
            categories.add("integration")
        elif "live" in path_str:
            categories.add("live")
        else:
            categories.add("mixed")

    # Get available CPU count
    cpu_count = os.cpu_count() or 1

    # Determine optimal worker count based on categories
    if categories == {"unit"} or categories == {"models"}:
        # CPU-bound tests, high parallelism
        return min(cpu_count, 8)
    elif categories == {"end_to_end"} or categories == {"live"}:
        # Rate-limited tests, default to sequential for reliability
        return 1
    elif categories == {"integration"}:
        # Moderate parallelism
        return min(cpu_count // 2, 4)
    elif len(categories) == 1 and "mixed" in categories:
        # Unknown test type, conservative approach
        return min(cpu_count // 2, 2)
    else:
        # Mixed test types - intelligent handling
        return _handle_mixed_test_scenario(test_paths, categories, cpu_count)


def _handle_mixed_test_scenario(test_paths, categories, cpu_count):
    """Handle mixed test scenarios intelligently."""
    import glob
    from pathlib import Path

    # Count actual test files in each category
    fast_tests = 0  # unit + models
    slow_tests = 0  # end_to_end + live + integration

    for path in test_paths:
        base_path = Path(path)
        if base_path.is_file():
            # Single file - categorize directly
            path_str = str(path).lower()
            if any(keyword in path_str for keyword in ["unit", "model"]):
                fast_tests += 1
            else:
                slow_tests += 1
        else:
            # Directory - count test files
            test_files = glob.glob(str(base_path / "**/test_*.py"), recursive=True)
            for test_file in test_files:
                test_file_str = test_file.lower()
                if any(keyword in test_file_str for keyword in ["unit", "model"]):
                    fast_tests += 1
                else:
                    slow_tests += 1

    # Check if user wants to include slow tests
    include_slow = _should_include_slow_tests()

    if not include_slow and slow_tests > 0:
        # Exclude slow tests, run only fast tests in parallel
        _mark_slow_tests_for_exclusion(test_paths)
        return min(cpu_count, 8) if fast_tests > 0 else 1

    # If including slow tests, use optimal parallelism (since e2e tests work with -n 8)
    if include_slow and fast_tests > 0 and slow_tests > 0:
        # Mixed scenario with --include-e2e: try the exact same as manual override
        # If -n 8 works, let's use 8 workers exactly like the manual case
        return min(cpu_count, 8)  # Use same as manual -n 8

    # If including slow tests or no slow tests detected
    if fast_tests > slow_tests * 3:  # 75%+ are fast tests
        # Majority fast tests - use high parallelism
        return min(cpu_count, 8)
    else:
        # Mixed or majority slow - use optimal settings for slow tests
        return min(cpu_count // 2, 4)


def _should_include_slow_tests():
    """Check if slow tests should be included in mixed scenarios."""
    # Check for command line flag (will be set by pytest_configure)
    return getattr(_should_include_slow_tests, '_include_e2e', False)


def _mark_slow_tests_for_exclusion(test_paths):
    """Mark slow tests for exclusion in mixed scenarios."""
    # This will be used to provide user feedback about excluded tests
    excluded_patterns = []
    for path in test_paths:
        path_str = str(path).lower()
        if any(keyword in path_str for keyword in ["end_to_end", "live", "integration"]):
            excluded_patterns.append(path)

    # Always mark for exclusion when this function is called
    _mark_slow_tests_for_exclusion._excluded_patterns = test_paths


def _print_execution_status(test_paths, optimal_workers, enable_rate_limiting):
    """Print detailed status about what's being executed."""
    # Check if any tests were excluded
    excluded_patterns = getattr(_mark_slow_tests_for_exclusion, '_excluded_patterns', [])
    
    # Check if this is a mixed scenario with --include-e2e
    include_slow = _should_include_slow_tests()
    
    if excluded_patterns:
        print(f"\n🚀 Auto-parallel enabled: {optimal_workers} workers (fast tests only)")
        print("📋 Excluded end-to-end/live tests for better performance")
        print("💡 Use --include-e2e to run all tests")
    elif include_slow and any(path.endswith("tests") or path.endswith("tests/") for path in test_paths):
        print(f"\n🚀 Auto-parallel enabled: {optimal_workers} workers (mixed tests)")
        print("📋 Running fast and slow tests together")
        if enable_rate_limiting:
            print("⚡ Rate limiting enabled for API tests")
    else:
        print(f"\n🚀 Auto-parallel enabled: {optimal_workers} workers, rate limiting: {enable_rate_limiting}")


def _should_enable_rate_limiting(test_paths):
    """Determine if rate limiting should be enabled based on test paths."""
    from pathlib import Path

    paths = [Path(p) for p in test_paths]

    # Check if slow tests were excluded
    excluded_patterns = getattr(_mark_slow_tests_for_exclusion, '_excluded_patterns', [])
    if excluded_patterns:
        # Slow tests excluded, no rate limiting needed
        return False

    # Check if user explicitly wants to include slow tests
    include_slow = _should_include_slow_tests()
    
    if not include_slow:
        return False

    # For mixed scenarios with --include-e2e, be smarter about rate limiting
    # The issue might be that we're being too aggressive with rate limiting
    # Since manual -n 8 works for e2e tests, maybe rate limiting isn't the core issue
    
    # Enable rate limiting only for specific e2e-heavy scenarios
    for path in paths:
        path_str = str(path).lower()
        if any(
            keyword in path_str
            for keyword in ["end_to_end", "e2e", "live"]
        ):
            # Direct e2e test execution - enable rate limiting
            return True

        # For mixed scenarios (tests/), try without rate limiting first
        # Since manual -n 8 works for e2e tests, the issue might be rate limiting config
        if path_str.endswith("tests") or path_str.endswith("tests/"):
            # Disable rate limiting for mixed scenarios - let's see if this fixes the timeout
            return False

    return False


def _is_end_to_end_tests(test_paths):
    """Determine if tests are primarily end-to-end tests."""
    from pathlib import Path

    paths = [Path(p) for p in test_paths]

    # Check if any path contains end-to-end keywords
    for path in paths:
        path_str = str(path).lower()
        if any(keyword in path_str for keyword in ["end_to_end", "e2e", "live"]):
            return True

    return False


def _implement_parallel_fallback(config):
    """Implement fallback strategy when parallel execution fails."""
    # Check if pytest-xdist is available and working
    try:
        import xdist

        # Check if we're running with -n flag but xdist failed to start
        if hasattr(config.option, "numprocesses") and config.option.numprocesses:
            # Store original value in case we need to fall back
            config._original_numprocesses = config.option.numprocesses

    except ImportError:
        # pytest-xdist not available, force sequential mode
        if hasattr(config.option, "numprocesses"):
            config.option.numprocesses = None

        # Set environment variable to disable parallel mode
        os.environ["PYTEST_DISABLE_PARALLEL"] = "true"

        print("\n⚠️  pytest-xdist not available, falling back to sequential execution")


def pytest_sessionstart(session):
    """Handle session start with parallel execution validation."""
    config = session.config

    # Check for worker startup failures
    if hasattr(config, "workerinput"):
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
    if hasattr(config.option, "numprocesses") and config.option.numprocesses:
        num_workers = config.option.numprocesses
        if num_workers == "auto":
            num_workers = os.cpu_count()

        print(f"\n🚀 Starting parallel execution with {num_workers} workers")

        # Set environment variables for worker coordination
        os.environ["PYTEST_PARALLEL_WORKERS"] = str(num_workers)
        # Don't override PYTEST_RATE_LIMITED - let the auto-parallel logic decide

        # Validate dependencies
        try:
            import xdist

            from ofsc.testing import get_global_rate_limiter

            print("✅ Parallel execution dependencies validated")
        except ImportError as e:
            print(f"❌ Missing parallel execution dependency: {e}")
            print("Falling back to sequential execution")
            config.option.numprocesses = None
            os.environ["PYTEST_DISABLE_PARALLEL"] = "true"
    else:
        print("\n📋 Running in sequential mode")


# Worker failure handling
def pytest_runtest_logreport(report):
    """Handle test reports and detect worker failures."""
    if report.when == "call" and report.failed:
        # Check if this is a rate limiting related failure
        if hasattr(report, "longrepr") and report.longrepr:
            error_text = str(report.longrepr).lower()

            if "429" in error_text or "rate limit" in error_text:
                print(f"\n⚠️  Rate limiting detected in test: {report.nodeid}")

                # Could implement automatic retry or worker throttling here
                # For now, just log the occurrence

    elif report.when == "setup" and report.failed:
        # Setup failures might indicate worker startup issues
        if hasattr(report, "longrepr") and report.longrepr:
            error_text = str(report.longrepr).lower()

            if "worker" in error_text or "xdist" in error_text:
                print(f"\n❌ Possible worker setup failure: {report.nodeid}")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to exclude slow tests in mixed scenarios."""
    excluded_patterns = getattr(_mark_slow_tests_for_exclusion, '_excluded_patterns', [])
    
    # NEW: Always sort tests by speed (fast first)
    def get_test_priority(item):
        path_str = str(item.fspath).lower()
        # Lower number = higher priority (runs first)
        if "unit" in path_str or "model" in path_str:
            return 0  # Fastest
        elif "integration" in path_str:
            return 2  # Medium
        elif "end_to_end" in path_str or "e2e" in path_str or "live" in path_str:
            return 3  # Slowest
        return 1  # Default
    
    # Sort all items regardless of exclusion
    items.sort(key=get_test_priority)
    
    # Continue with existing exclusion logic
    if not excluded_patterns:
        return  # No exclusions needed
    
    # Filter out slow tests
    original_count = len(items)
    items_to_keep = []
    excluded_count = 0
    
    for item in items:
        item_path = str(item.fspath).lower()
        should_exclude = any(keyword in item_path for keyword in ["end_to_end", "live", "integration"])
        
        if should_exclude:
            excluded_count += 1
        else:
            items_to_keep.append(item)
    
    # Update the items list in place
    items[:] = items_to_keep
    
    if excluded_count > 0:
        print(f"📋 Excluded {excluded_count} slow tests, running {len(items_to_keep)} fast tests")


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
        help="Test environment to use: dev, staging, prod",
    )
    parser.addoption(
        "--live",
        action="store_true",
        default=False,
        help="Run live tests against real OFSC instance",
    )
    parser.addoption(
        "--parallel",
        action="store_true",
        default=True,
        help="Run tests in parallel (default)",
    )
    parser.addoption(
        "--sequential",
        action="store_true",
        default=False,
        help="Run tests sequentially",
    )
    parser.addoption(
        "--include-e2e",
        action="store_true",
        default=False,
        help="Include end-to-end and live tests when running mixed test scenarios",
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
    disable_parallel = os.environ.get("PYTEST_DISABLE_PARALLEL", "").lower()
    if disable_parallel in ("true", "1", "yes"):
        return False

    # Default to parallel
    return True


@pytest.fixture
def rate_limiting_enabled():
    """Check if rate limiting should be enabled for this test run."""
    return os.environ.get("PYTEST_RATE_LIMITED", "").lower() in ("true", "1", "yes")


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

        worker_id = getattr(item.config, "workerinput", {}).get("workerid", "main")
        process_id = os.getpid()
        thread_id = threading.get_ident()

        # Include worker ID, process ID, and timestamp for uniqueness
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

        debug_dir = (
            Path("test_debug")
            / f"worker_{worker_id}"
            / f"pid_{process_id}"
            / f"thread_{thread_id}"
            / f"{timestamp}_{item.nodeid.replace('/', '_').replace('::', '_')}"
        )
        debug_dir.mkdir(parents=True, exist_ok=True)

        # Save test context if debug mode is enabled
        try:
            config = load_test_config()
            if config.debug_on_failure:
                import json
                from datetime import datetime

                with open(debug_dir / "context.json", "w") as f:
                    json.dump(
                        {
                            "test": item.nodeid,
                            "timestamp": datetime.now().isoformat(),
                            "environment": getattr(item, "test_env", "unknown"),
                            "error": str(rep.longrepr),
                        },
                        f,
                        indent=2,
                    )
        except Exception:
            # Don't fail if debug saving fails
            pass
