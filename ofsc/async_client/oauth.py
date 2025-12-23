"""Async version of OFSOauth2 API module."""

import httpx

from ..models import OFSConfig, OFSOAuthRequest


class AsyncOFSOauth2:
    """Async version of OFSOauth2 API module."""

    def __init__(self, config: OFSConfig, client: httpx.AsyncClient):
        self._config = config
        self._client = client

    @property
    def config(self) -> OFSConfig:
        return self._config

    @property
    def baseUrl(self) -> str:
        return self._config.baseURL

    @property
    def headers(self) -> dict:
        """Build authorization headers."""
        headers = {"Content-Type": "application/json;charset=UTF-8"}
        if not self._config.useToken:
            headers["Authorization"] = "Basic " + self._config.basicAuthString.decode(
                "utf-8"
            )
        else:
            raise NotImplementedError("Token-based auth not yet implemented for async")
        return headers

    async def get_token(self, params: OFSOAuthRequest = None) -> httpx.Response:
        raise NotImplementedError("Async method not yet implemented")
