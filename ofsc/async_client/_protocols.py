"""Shared Protocol type stubs for async client mixins."""

from typing import Protocol

import httpx


class _CoreBaseProtocol(Protocol):
    """Type stub declaring what async core mixins expect from their base class."""

    _client: httpx.AsyncClient

    @property
    def baseUrl(self) -> str: ...

    @property
    def headers(self) -> dict: ...

    def _handle_http_error(self, e: httpx.HTTPStatusError, context: str = "") -> None: ...
