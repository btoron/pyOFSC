"""Test-aware HTTP client wrapper that integrates rate limiting with OFSC clients.

This module provides wrappers for OFSC clients that automatically apply rate limiting
when running in parallel test environments.
"""

import os
from typing import Optional, Any, Dict
from contextlib import asynccontextmanager

import httpx
from ..client import OFSC
from .rate_limiter import RateLimitedHTTPClient


class TestAwareOFSC(OFSC):
    """OFSC client wrapper that automatically applies rate limiting in test environments."""

    def __init__(self, *args, **kwargs):
        """Initialize test-aware OFSC client.

        Automatically detects test environment and applies appropriate rate limiting.
        """
        # Extract rate limiting configuration
        self._rate_limit_config = {
            "max_concurrent_requests": kwargs.pop("max_concurrent_requests", 10),
            "rate_limit_delay": kwargs.pop("rate_limit_delay", 0.1),
            "max_retries": kwargs.pop("max_retries", 3),
            "base_backoff": kwargs.pop("base_backoff", 1.0),
            "max_backoff": kwargs.pop("max_backoff", 60.0),
        }

        # Initialize parent
        super().__init__(*args, **kwargs)

        # Check if we're in a test environment
        self._is_test_env = self._detect_test_environment()
        self._rate_limited_client = None

    def _detect_test_environment(self) -> bool:
        """Detect if we're running in a test environment."""
        test_indicators = [
            os.environ.get("PYTEST_CURRENT_XDIST_WORKER"),  # pytest-xdist
            os.environ.get("PYTEST_RATE_LIMITED", "").lower() == "true",
            "pytest" in os.environ.get("_", ""),  # Running via pytest
            "test" in os.environ.get("PYTEST_CURRENT_CATEGORY", ""),
        ]

        return any(test_indicators)

    async def __aenter__(self):
        """Async context manager entry with rate limiting support."""
        # Call parent's __aenter__
        result = await super().__aenter__()

        # Wrap client with rate limiting if in test environment
        if self._is_test_env and hasattr(self, "client") and self.client:
            self._rate_limited_client = RateLimitedHTTPClient(
                self.client, **self._rate_limit_config
            )

            # Replace the client's request methods with rate-limited versions
            self._original_request = self.client.request
            self.client.request = self._rate_limited_client.request

        return result

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with cleanup."""
        # Restore original request method if we wrapped it
        if self._rate_limited_client and hasattr(self, "_original_request"):
            self.client.request = self._original_request
            await self._rate_limited_client.close()
            self._rate_limited_client = None

        # Call parent's __aexit__
        return await super().__aexit__(exc_type, exc_val, exc_tb)

    def get_rate_limit_stats(self) -> Optional[Dict[str, Any]]:
        """Get rate limiting statistics if available."""
        if self._rate_limited_client:
            return self._rate_limited_client.get_stats()
        return None

    def reset_rate_limit_stats(self):
        """Reset rate limiting statistics."""
        if self._rate_limited_client:
            self._rate_limited_client.reset_stats()


@asynccontextmanager
async def test_aware_ofsc_client(*args, **kwargs):
    """Create a test-aware OFSC client context manager.

    This automatically applies rate limiting in test environments while
    behaving normally in production environments.

    Args:
        *args, **kwargs: Arguments passed to TestAwareOFSC constructor

    Yields:
        TestAwareOFSC instance
    """
    async with TestAwareOFSC(*args, **kwargs) as client:
        yield client


class RateLimitedClientFactory:
    """Factory for creating rate-limited HTTP clients with consistent configuration."""

    def __init__(self):
        """Initialize the factory with default configuration."""
        self._default_config = {
            "max_concurrent_requests": 10,
            "rate_limit_delay": 0.1,
            "max_retries": 3,
            "base_backoff": 1.0,
            "max_backoff": 60.0,
            "backoff_multiplier": 2.0,
            "jitter": True,
        }

        # Update from environment variables
        self._update_config_from_env()

    def _update_config_from_env(self):
        """Update configuration from environment variables."""
        env_mapping = {
            "PYTEST_MAX_CONCURRENT_REQUESTS": "max_concurrent_requests",
            "PYTEST_RATE_LIMIT_DELAY": "rate_limit_delay",
            "PYTEST_MAX_RETRIES": "max_retries",
            "PYTEST_BASE_BACKOFF": "base_backoff",
            "PYTEST_MAX_BACKOFF": "max_backoff",
        }

        for env_var, config_key in env_mapping.items():
            if env_var in os.environ:
                try:
                    if (
                        config_key == "max_concurrent_requests"
                        or config_key == "max_retries"
                    ):
                        self._default_config[config_key] = int(os.environ[env_var])
                    else:
                        self._default_config[config_key] = float(os.environ[env_var])
                except ValueError:
                    pass

    def create_rate_limited_client(
        self, base_client: httpx.AsyncClient, **overrides
    ) -> RateLimitedHTTPClient:
        """Create a rate-limited HTTP client with factory defaults.

        Args:
            base_client: The underlying httpx.AsyncClient
            **overrides: Override default configuration values

        Returns:
            RateLimitedHTTPClient instance
        """
        config = self._default_config.copy()
        config.update(overrides)

        return RateLimitedHTTPClient(base_client, **config)

    def get_config(self) -> Dict[str, Any]:
        """Get current factory configuration."""
        return self._default_config.copy()

    def update_config(self, **kwargs):
        """Update factory configuration."""
        self._default_config.update(kwargs)


# Global factory instance
_client_factory = RateLimitedClientFactory()


def get_client_factory() -> RateLimitedClientFactory:
    """Get the global client factory instance."""
    return _client_factory


def create_test_client(*args, **kwargs) -> TestAwareOFSC:
    """Create a test-aware OFSC client.

    This is a convenience function that creates a TestAwareOFSC instance
    with optimal configuration for testing.

    Args:
        *args, **kwargs: Arguments passed to TestAwareOFSC

    Returns:
        TestAwareOFSC instance
    """
    # Apply test-optimized defaults
    defaults = {
        "max_concurrent_requests": 10,
        "rate_limit_delay": 0.1,
        "max_retries": 3,
        "base_backoff": 1.0,
    }

    # Update with any provided overrides
    for key, value in defaults.items():
        kwargs.setdefault(key, value)

    return TestAwareOFSC(*args, **kwargs)
