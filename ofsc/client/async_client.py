"""Async OFSC client implementation using httpx.AsyncClient."""

import logging
from typing import Optional

import httpx
from pydantic import HttpUrl

from .base import BaseOFSClient, ConnectionConfig
from ofsc.auth import BaseAuth


class AsyncOFSC(BaseOFSClient):
    """Asynchronous OFSC client using httpx.AsyncClient."""
    
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
        auth: Optional[BaseAuth] = None
    ):
        """Initialize the async OFSC client.
        
        Args:
            instance: OFSC instance name (can be loaded from OFSC_INSTANCE env var)
            client_id: Client ID for authentication (can be loaded from OFSC_CLIENT_ID env var)
            client_secret: Client secret for authentication (can be loaded from OFSC_CLIENT_SECRET env var)
            base_url: Custom base URL as HttpUrl (auto-generated if not provided)
            use_token: Whether to use OAuth2 token authentication
            auto_raise: Whether to automatically raise exceptions on API errors
            auto_model: Whether to automatically convert responses to models
            connection_config: Configuration for HTTP connection pooling
            auth: Custom authentication instance (overrides other auth parameters)
        """
        super().__init__(
            instance=instance,
            client_id=client_id,
            client_secret=client_secret,
            base_url=base_url,
            use_token=use_token,
            auto_raise=auto_raise,
            auto_model=auto_model,
            connection_config=connection_config,
            auth=auth
        )
        
        # Initialize API modules (will be implemented in later phases)
        # self._core = AsyncOFSCore(self)
        # self._metadata = AsyncOFSMetadata(self)
        # self._capacity = AsyncOFSCapacity(self)
        # self._oauth = AsyncOFSOauth(self)
    
    def _create_client(self) -> httpx.AsyncClient:
        """Create an async httpx client with proper configuration."""
        return httpx.AsyncClient(
            limits=self._get_limits(),
            timeout=self._get_timeout(),
            headers=self._get_auth_headers(),
            follow_redirects=True
        )
    
    async def __aenter__(self):
        """Async context manager entry."""
        self._client = self._create_client()
        logging.info(f"Async OFSC client connected to {self.base_url}")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def close(self):
        """Close the async HTTP client and clean up resources."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            logging.info("Async OFSC client closed")
    
    @property
    def client(self) -> httpx.AsyncClient:
        """Get the underlying httpx.AsyncClient instance."""
        if self._client is None:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")
        return self._client
    
    async def request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> httpx.Response:
        """Make an async HTTP request.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            **kwargs: Additional arguments for httpx request
            
        Returns:
            httpx.Response object
        """
        url = self._build_url(endpoint)
        response = await self.client.request(method, url, **kwargs)
        
        if self._config.auto_raise and response.status_code >= 400:
            response.raise_for_status()
        
        return response
    
    # Properties for API modules (will be implemented in later phases)
    @property
    def core(self):
        """Get the Core API interface."""
        if self._core is None:
            raise NotImplementedError("Core API not yet implemented in Phase 1.2")
        return self._core
    
    @property
    def metadata(self):
        """Get the Metadata API interface."""
        if self._metadata is None:
            raise NotImplementedError("Metadata API not yet implemented in Phase 1.2")
        return self._metadata
    
    @property
    def capacity(self):
        """Get the Capacity API interface."""
        if self._capacity is None:
            raise NotImplementedError("Capacity API not yet implemented in Phase 1.2")
        return self._capacity
    
    @property
    def oauth(self):
        """Get the OAuth API interface."""
        if self._oauth is None:
            raise NotImplementedError("OAuth API not yet implemented in Phase 1.2")
        return self._oauth
    
    def __str__(self) -> str:
        return f"AsyncOFSC(instance={self._config.instance}, base_url={self.base_url})"