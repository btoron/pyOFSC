"""Base client implementation with shared logic for both sync and async clients."""

import base64
import os
from abc import ABC, abstractmethod
from typing import Optional, Union
from urllib.parse import urljoin

import httpx
from pydantic import BaseModel, ConfigDict, field_validator, ValidationInfo, HttpUrl

from ofsc.auth import BaseAuth, create_auth
from ofsc.retry import RetryConfig, CircuitBreakerConfig, with_fault_tolerance
from ofsc.exceptions import OFSConfigurationException


class OFSConfig(BaseModel):
    """Configuration model for OFSC clients."""

    # Authentication parameters - new v3.0 naming
    instance: str
    client_id: str
    client_secret: str

    # Optional parameters
    use_token: bool = False
    root: Optional[str] = None
    base_url: Optional[HttpUrl] = None
    auto_raise: bool = True
    auto_model: bool = True

    model_config = ConfigDict(validate_assignment=True)

    @field_validator("base_url")
    def set_base_url(cls, url, info: ValidationInfo):
        """Auto-generate base URL from instance name if not provided."""
        if url:
            return url
        instance = info.data.get("instance")
        if instance:
            return HttpUrl(f"https://{instance}.fs.ocs.oraclecloud.com/")
        return None

    @property
    def basic_auth_string(self) -> str:
        """Generate Basic Auth string for HTTP headers."""
        auth_user = f"{self.client_id}@{self.instance}"
        auth_secret = self.client_secret

        credentials = f"{auth_user}:{auth_secret}"
        return base64.b64encode(credentials.encode("utf-8")).decode("utf-8")


class ConnectionConfig(BaseModel):
    """Configuration for httpx connection pooling."""

    max_connections: int = 20
    max_keepalive_connections: int = 10
    keepalive_expiry: float = 30.0
    timeout: float = 30.0

    # Retry configuration (R7.4)
    enable_retries: bool = True
    max_retry_attempts: int = 3
    initial_retry_delay: float = 1.0
    max_retry_delay: float = 60.0
    retry_exponential_base: float = 2.0
    retry_jitter: bool = True

    # Circuit breaker configuration (R7.5)
    enable_circuit_breaker: bool = True
    circuit_breaker_failure_threshold: int = 5
    circuit_breaker_timeout: float = 60.0


class BaseOFSClient(ABC):
    """Abstract base class for OFSC clients with shared logic."""

    def __init__(
        self,
        instance: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        base_url: Optional[HttpUrl] = None,
        use_token: bool = False,
        auto_raise: bool = True,
        auto_model: bool = True,
        connection_config: Optional[ConnectionConfig] = None,
        auth: Optional[BaseAuth] = None,
    ):
        """Initialize the OFSC client.

        Args:
            instance: OFSC instance name (can be loaded from OFSC_INSTANCE env var)
            client_id: Client ID for authentication (can be loaded from OFSC_CLIENT_ID env var)
            client_secret: Client secret for authentication (can be loaded from OFSC_CLIENT_SECRET env var)
            base_url: Custom base URL as HttpUrl (auto-generated if not provided)
            use_token: Whether to use OAuth2 token authentication
            auto_raise: DEPRECATED - errors are always raised (R7.3)
            auto_model: Whether to automatically convert responses to models
            connection_config: Configuration for HTTP connection pooling
            auth: Custom authentication instance (overrides other auth parameters)
        """
        # Load credentials from environment variables if not provided
        instance = instance or os.getenv("OFSC_INSTANCE")
        client_id = client_id or os.getenv("OFSC_CLIENT_ID")
        client_secret = client_secret or os.getenv("OFSC_CLIENT_SECRET")

        if not instance:
            raise OFSConfigurationException(
                "instance must be provided or set OFSC_INSTANCE environment variable"
            )
        if not client_id:
            raise OFSConfigurationException(
                "client_id must be provided or set OFSC_CLIENT_ID environment variable"
            )
        if not client_secret:
            raise OFSConfigurationException(
                "client_secret must be provided or set OFSC_CLIENT_SECRET environment variable"
            )

        self._config = OFSConfig(
            instance=instance,
            client_id=client_id,
            client_secret=client_secret,
            base_url=base_url,
            use_token=use_token,
            auto_raise=auto_raise,
            auto_model=auto_model,
        )

        self._connection_config = connection_config or ConnectionConfig()
        self._client: Optional[Union[httpx.Client, httpx.AsyncClient]] = None

        # Authentication setup
        if auth:
            self._auth = auth
        else:
            self._auth = create_auth(
                instance=instance,
                client_id=client_id,
                client_secret=client_secret,
                use_oauth2=use_token,
                base_url=str(self._config.base_url) if self._config.base_url else None,
            )

        # Will be set by subclasses
        self._core = None
        self._metadata = None
        self._capacity = None
        self._oauth = None

        # Initialize fault tolerance components
        self._setup_fault_tolerance()

    @property
    def config(self) -> OFSConfig:
        """Get the client configuration."""
        return self._config

    @property
    def auth(self) -> BaseAuth:
        """Get the authentication instance."""
        return self._auth

    @property
    def base_url(self) -> str:
        """Get the base URL for API requests."""
        if self._config.base_url:
            url_str = str(self._config.base_url)
            return url_str.rstrip("/")  # Remove trailing slash for consistency
        return ""

    def _get_auth_headers(self) -> dict:
        """Get authentication headers for HTTP requests."""
        return self._auth.get_headers()

    def _get_limits(self) -> httpx.Limits:
        """Get connection limits for httpx client."""
        return httpx.Limits(
            max_connections=self._connection_config.max_connections,
            max_keepalive_connections=self._connection_config.max_keepalive_connections,
            keepalive_expiry=self._connection_config.keepalive_expiry,
        )

    def _get_timeout(self) -> httpx.Timeout:
        """Get timeout configuration for httpx client."""
        return httpx.Timeout(self._connection_config.timeout)

    def _build_url(self, endpoint: str) -> str:
        """Build full URL from endpoint path."""
        return urljoin(self.base_url, endpoint)

    @abstractmethod
    def _create_client(self) -> Union[httpx.Client, httpx.AsyncClient]:
        """Create the appropriate httpx client (sync or async)."""
        pass

    @abstractmethod
    def close(self):
        """Close the HTTP client and clean up resources."""
        pass

    def _setup_fault_tolerance(self):
        """Setup retry and circuit breaker configurations."""
        if self._connection_config.enable_retries:
            self._retry_config = RetryConfig(
                max_attempts=self._connection_config.max_retry_attempts,
                initial_delay=self._connection_config.initial_retry_delay,
                max_delay=self._connection_config.max_retry_delay,
                exponential_base=self._connection_config.retry_exponential_base,
                jitter=self._connection_config.retry_jitter,
            )
        else:
            self._retry_config = None

        if self._connection_config.enable_circuit_breaker:
            self._circuit_breaker_config = CircuitBreakerConfig(
                failure_threshold=self._connection_config.circuit_breaker_failure_threshold,
                timeout_seconds=self._connection_config.circuit_breaker_timeout,
                name=f"ofsc_{self._config.instance}",
            )
        else:
            self._circuit_breaker_config = None

    def _apply_fault_tolerance(self, func):
        """Apply fault tolerance decorators to a function."""
        return with_fault_tolerance(
            retry_config=self._retry_config,
            circuit_breaker_config=self._circuit_breaker_config,
        )(func)

    def __str__(self) -> str:
        return (
            f"BaseOFSClient(instance={self._config.instance}, base_url={self.base_url})"
        )
