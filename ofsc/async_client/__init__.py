"""Async version of the OFSC client using httpx.AsyncClient."""

import logging
from typing import Optional

import httpx

from ..exceptions import (
    OFSAPIException,
    OFSCApiError,
    OFSCAuthenticationError,
    OFSCAuthorizationError,
    OFSCConflictError,
    OFSCNetworkError,
    OFSCNotFoundError,
    OFSCRateLimitError,
    OFSCServerError,
    OFSCValidationError,
)
from ..models import OFSConfig
from .capacity import AsyncOFSCapacity
from .core import AsyncOFSCore
from .metadata import AsyncOFSMetadata
from .oauth import AsyncOFSOauth2
from .statistics import AsyncOFSStatistics

logger = logging.getLogger(__name__)

__all__ = [
    "AsyncOFSC",
    "OFSAPIException",
    "OFSCApiError",
    "OFSCAuthenticationError",
    "OFSCAuthorizationError",
    "OFSCConflictError",
    "OFSCNetworkError",
    "OFSCNotFoundError",
    "OFSCRateLimitError",
    "OFSCServerError",
    "OFSCValidationError",
]


class AsyncOFSC:
    """Async version of OFSC client using httpx.AsyncClient with HTTP/2 support.

    This class provides the same interface as OFSC but uses async/await patterns.
    It must be used as an async context manager to properly manage the HTTP client lifecycle.

    HTTP/2 is enabled by default for efficient stream multiplexing and improved performance
    when making parallel API calls using asyncio.gather().

    Warning:
        This client is task-safe but NOT thread-safe. Do not share a single AsyncOFSC
        instance across multiple threads or event loops. For parallel requests, use
        asyncio.gather() within the same async context.

    Example:
        async with AsyncOFSC(
            clientID="my_client",
            companyName="my_company",
            secret="my_secret",
        ) as client:
            # Single request
            result = await client.core.get_resource("resource_id")

            # Parallel requests (recommended for bulk operations)
            workzones, properties = await asyncio.gather(
                client.metadata.get_workzones(),
                client.metadata.get_properties(),
            )
    """

    def __init__(
        self,
        clientID: str,
        companyName: str,
        secret: str,
        root: Optional[str] = None,
        baseUrl: Optional[str] = None,
        useToken: bool = False,
        access_token: Optional[str] = None,
        enable_auto_raise: bool = True,
        enable_auto_model: bool = True,
        enable_logging: bool = False,
    ):
        self._enable_logging = enable_logging
        self._config = OFSConfig(
            baseURL=baseUrl,
            clientID=clientID,
            secret=secret,
            companyName=companyName,
            root=root,
            useToken=useToken,
            access_token=access_token,
            auto_raise=enable_auto_raise,
            auto_model=enable_auto_model,
        )
        self._client: Optional[httpx.AsyncClient] = None
        self._core: Optional[AsyncOFSCore] = None
        self._metadata: Optional[AsyncOFSMetadata] = None
        self._capacity: Optional[AsyncOFSCapacity] = None
        self._oauth: Optional[AsyncOFSOauth2] = None
        self._statistics: Optional[AsyncOFSStatistics] = None

    async def __aenter__(self) -> "AsyncOFSC":
        """Enter async context manager - create shared httpx.AsyncClient."""

        async def log_request(request: httpx.Request) -> None:
            logger.debug("Request: %s %s", request.method, request.url)

        async def log_response(response: httpx.Response) -> None:
            request = response.request
            logger.debug("Response: %s %s %s", request.method, request.url, response.status_code)
            if response.status_code >= 400:
                logger.warning(
                    "HTTP error: %s %s %s",
                    request.method,
                    request.url,
                    response.status_code,
                )

        event_hooks: dict[str, list] = {}
        if self._enable_logging:
            event_hooks = {
                "request": [log_request],
                "response": [log_response],
            }

        self._client = httpx.AsyncClient(http2=True, event_hooks=event_hooks)
        self._core = AsyncOFSCore(config=self._config, client=self._client)
        self._metadata = AsyncOFSMetadata(config=self._config, client=self._client)
        self._capacity = AsyncOFSCapacity(config=self._config, client=self._client)
        self._oauth = AsyncOFSOauth2(config=self._config, client=self._client)
        self._statistics = AsyncOFSStatistics(config=self._config, client=self._client)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit async context manager - close the shared client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    @property
    def core(self) -> AsyncOFSCore:
        if self._core is None:
            raise RuntimeError("AsyncOFSC must be used as async context manager")
        return self._core

    @property
    def metadata(self) -> AsyncOFSMetadata:
        if self._metadata is None:
            raise RuntimeError("AsyncOFSC must be used as async context manager")
        return self._metadata

    @property
    def capacity(self) -> AsyncOFSCapacity:
        if self._capacity is None:
            raise RuntimeError("AsyncOFSC must be used as async context manager")
        return self._capacity

    @property
    def oauth2(self) -> AsyncOFSOauth2:
        if self._oauth is None:
            raise RuntimeError("AsyncOFSC must be used as async context manager")
        return self._oauth

    @property
    def statistics(self) -> AsyncOFSStatistics:
        if self._statistics is None:
            raise RuntimeError("AsyncOFSC must be used as async context manager")
        return self._statistics

    @property
    def auto_model(self) -> bool:
        return self._config.auto_model

    @auto_model.setter
    def auto_model(self, value: bool) -> None:
        self._config.auto_model = value
        if self._core:
            self._core.config.auto_model = value
        if self._metadata:
            self._metadata.config.auto_model = value
        if self._capacity:
            self._capacity.config.auto_model = value
        if self._oauth:
            self._oauth.config.auto_model = value
        if self._statistics:
            self._statistics.config.auto_model = value

    def __str__(self) -> str:
        return f"AsyncOFSC(baseURL={self._config.baseURL})"
