"""Shared base class for all async OFSC API modules."""

from typing import Type, TypeVar, Union
from urllib.parse import quote_plus, urljoin

import httpx
from pydantic import BaseModel

from ..exceptions import (
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
from ..models import CsvList, OFSConfig

T = TypeVar("T")


class AsyncClientBase:
    """Base class for all async API modules.

    Provides shared infrastructure: config access, URL construction,
    auth headers, HTTP error handling, and generic HTTP operation helpers.
    """

    def __init__(self, config: OFSConfig, client: httpx.AsyncClient):
        self._config = config
        self._client = client

    @property
    def config(self) -> OFSConfig:
        return self._config

    @property
    def baseUrl(self) -> str:
        if self._config.baseURL is None:
            raise ValueError("Base URL is not configured")
        return self._config.baseURL

    @property
    def headers(self) -> dict:
        """Build authorization headers."""
        headers = {"Content-Type": "application/json;charset=UTF-8"}
        if not self._config.useToken:
            headers["Authorization"] = "Basic " + self._config.basicAuthString.decode("utf-8")
        else:
            if self._config.access_token is None:
                raise ValueError("access_token required when useToken=True")
            headers["Authorization"] = f"Bearer {self._config.access_token}"
        return headers

    def _parse_error_response(self, response: httpx.Response) -> dict:
        """Parse OFSC error response format.

        OFSC API returns errors in the format:
        {
            "type": "string",
            "title": "string",
            "detail": "string"
        }

        :param response: The httpx Response object
        :type response: httpx.Response
        :return: Error information with type, title, and detail keys
        :rtype: dict
        """
        try:
            error_data = response.json()
            return {
                "type": error_data.get("type", "about:blank"),
                "title": error_data.get("title", ""),
                "detail": error_data.get("detail", response.text),
            }
        except Exception:
            return {
                "type": "about:blank",
                "title": f"HTTP {response.status_code}",
                "detail": response.text,
            }

    def _handle_http_error(self, e: httpx.HTTPStatusError, context: str = "") -> None:
        """Convert httpx exceptions to OFSC exceptions with error details.

        :param e: The httpx HTTPStatusError exception
        :type e: httpx.HTTPStatusError
        :param context: Additional context for the error message
        :type context: str
        :raises OFSCAuthenticationError: For 401 errors
        :raises OFSCAuthorizationError: For 403 errors
        :raises OFSCNotFoundError: For 404 errors
        :raises OFSCConflictError: For 409 errors
        :raises OFSCRateLimitError: For 429 errors
        :raises OFSCValidationError: For 400, 422 errors
        :raises OFSCServerError: For 5xx errors
        :raises OFSCApiError: For other HTTP errors
        """
        status = e.response.status_code
        error_info = self._parse_error_response(e.response)

        message = f"{context}: {error_info['detail']}" if context else error_info["detail"]

        error_map = {
            401: OFSCAuthenticationError,
            403: OFSCAuthorizationError,
            404: OFSCNotFoundError,
            409: OFSCConflictError,
            429: OFSCRateLimitError,
        }

        if status in error_map:
            raise error_map[status](
                message,
                status_code=status,
                response=e.response,
                error_type=error_info["type"],
                title=error_info["title"],
                detail=error_info["detail"],
            ) from e
        elif 400 <= status < 500:
            raise OFSCValidationError(
                message,
                status_code=status,
                response=e.response,
                error_type=error_info["type"],
                title=error_info["title"],
                detail=error_info["detail"],
            ) from e
        elif 500 <= status < 600:
            raise OFSCServerError(
                message,
                status_code=status,
                response=e.response,
                error_type=error_info["type"],
                title=error_info["title"],
                detail=error_info["detail"],
            ) from e
        else:
            raise OFSCApiError(
                message,
                status_code=status,
                response=e.response,
                error_type=error_info["type"],
                title=error_info["title"],
                detail=error_info["detail"],
            ) from e

    # region Generic HTTP helpers

    @staticmethod
    def _to_csv_param(value: Union[CsvList, list[str], str]) -> str:
        """Convert a list, CsvList, or plain string to a CSV string for API query params.

        :param value: A CsvList model, a list of strings, or a plain string
        :type value: Union[CsvList, list[str], str]
        :return: Comma-separated string suitable for an API query parameter
        :rtype: str
        """
        if isinstance(value, CsvList):
            return value.value
        if isinstance(value, list):
            return ",".join(value)
        return value

    def _clean_response(self, data: dict) -> dict:
        """Remove the 'links' key from an API response dict.

        The OFSC API adds a 'links' key to responses that is not represented
        in Pydantic models. This helper removes it unconditionally, replacing
        the previous inconsistent dual-pattern approach.

        :param data: Parsed JSON response dict
        :type data: dict
        :return: The same dict with 'links' removed if present
        :rtype: dict
        """
        data.pop("links", None)
        return data

    async def _get_paginated_list(
        self,
        endpoint: str,
        response_model: Type[T],
        error_context: str,
        offset: int = 0,
        limit: int = 100,
        extra_params: dict | None = None,
    ) -> T:
        """GET a paginated list resource and return a validated model.

        :param endpoint: API path (e.g. '/rest/ofscMetadata/v1/workZones')
        :type endpoint: str
        :param response_model: Pydantic model class to validate the response
        :type response_model: Type[T]
        :param error_context: Human-readable context for error messages
        :type error_context: str
        :param offset: Pagination offset (default 0)
        :type offset: int
        :param limit: Pagination limit (default 100)
        :type limit: int
        :param extra_params: Additional query parameters to merge
        :type extra_params: dict | None
        :return: Validated response model instance
        :rtype: T
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, endpoint)
        params: dict = {"offset": offset, "limit": limit}
        if extra_params:
            params.update(extra_params)

        try:
            response = await self._client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = self._clean_response(response.json())
            return response_model.model_validate(data)  # type: ignore[union-attr]
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, error_context)
            raise  # satisfies type checker
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def _get_single_item(
        self,
        endpoint_template: str,
        label: str,
        response_model: Type[T],
        error_context: str,
    ) -> T:
        """GET a single resource by label and return a validated model.

        The label is always URL-encoded with quote_plus before substitution.

        :param endpoint_template: API path template with '{label}' placeholder
            (e.g. '/rest/ofscMetadata/v1/workZones/{label}')
        :type endpoint_template: str
        :param label: Resource label (will be URL-encoded)
        :type label: str
        :param response_model: Pydantic model class to validate the response
        :type response_model: Type[T]
        :param error_context: Human-readable context for error messages
        :type error_context: str
        :return: Validated response model instance
        :rtype: T
        :raises OFSCNotFoundError: If the resource is not found (404)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        encoded_label = quote_plus(label)
        url = urljoin(self.baseUrl, endpoint_template.format(label=encoded_label))

        try:
            response = await self._client.get(url, headers=self.headers)
            response.raise_for_status()
            data = self._clean_response(response.json())
            return response_model.model_validate(data)  # type: ignore[union-attr]
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, error_context)
            raise  # satisfies type checker
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def _get_all_items(
        self,
        endpoint: str,
        response_model: Type[T],
        error_context: str,
    ) -> T:
        """GET all items from a non-paginated resource.

        :param endpoint: API path (e.g. '/rest/ofscMetadata/v1/applications')
        :type endpoint: str
        :param response_model: Pydantic model class to validate the response
        :type response_model: Type[T]
        :param error_context: Human-readable context for error messages
        :type error_context: str
        :return: Validated response model instance
        :rtype: T
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, endpoint)

        try:
            response = await self._client.get(url, headers=self.headers)
            response.raise_for_status()
            data = self._clean_response(response.json())
            return response_model.model_validate(data)  # type: ignore[union-attr]
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, error_context)
            raise  # satisfies type checker
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def _put_item(
        self,
        endpoint: str,
        data: BaseModel,
        response_model: Type[T],
        error_context: str,
    ) -> T:
        """PUT (create or replace) a resource and return the validated response.

        :param endpoint: Full API path including the resource identifier
        :type endpoint: str
        :param data: Pydantic model to serialize as the request body
        :type data: BaseModel
        :param response_model: Pydantic model class to validate the response
        :type response_model: Type[T]
        :param error_context: Human-readable context for error messages
        :type error_context: str
        :return: Validated response model instance
        :rtype: T
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCValidationError: If validation fails (400, 422)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, endpoint)

        try:
            response = await self._client.put(
                url,
                headers=self.headers,
                json=data.model_dump(exclude_none=True, mode="json"),
            )
            response.raise_for_status()
            result = self._clean_response(response.json())
            return response_model.model_validate(result)  # type: ignore[union-attr]
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, error_context)
            raise  # satisfies type checker
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def _post_item(
        self,
        endpoint: str,
        data: BaseModel,
        response_model: Type[T],
        error_context: str,
    ) -> T:
        """POST (create) a resource and return the validated response.

        :param endpoint: API path (e.g. '/rest/ofscMetadata/v1/workZones')
        :type endpoint: str
        :param data: Pydantic model to serialize as the request body
        :type data: BaseModel
        :param response_model: Pydantic model class to validate the response
        :type response_model: Type[T]
        :param error_context: Human-readable context for error messages
        :type error_context: str
        :return: Validated response model instance
        :rtype: T
        :raises OFSCConflictError: If the resource already exists (409)
        :raises OFSCValidationError: If validation fails (400)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, endpoint)

        try:
            response = await self._client.post(
                url,
                headers=self.headers,
                content=data.model_dump_json(exclude_none=True),
            )
            response.raise_for_status()
            result = self._clean_response(response.json())
            return response_model.model_validate(result)  # type: ignore[union-attr]
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, error_context)
            raise  # satisfies type checker
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def _patch_item(
        self,
        endpoint: str,
        data: BaseModel,
        response_model: Type[T],
        error_context: str,
    ) -> T:
        """PATCH (partial update) a resource and return the validated response.

        :param endpoint: Full API path including the resource identifier
        :type endpoint: str
        :param data: Pydantic model to serialize as the request body
        :type data: BaseModel
        :param response_model: Pydantic model class to validate the response
        :type response_model: Type[T]
        :param error_context: Human-readable context for error messages
        :type error_context: str
        :return: Validated response model instance
        :rtype: T
        :raises OFSCNotFoundError: If the resource is not found (404)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCValidationError: If validation fails (400, 422)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, endpoint)

        try:
            response = await self._client.patch(
                url,
                headers=self.headers,
                content=data.model_dump_json(exclude_none=True).encode("utf-8"),
            )
            response.raise_for_status()
            result = self._clean_response(response.json())
            return response_model.model_validate(result)  # type: ignore[union-attr]
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, error_context)
            raise  # satisfies type checker
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def _delete_item(
        self,
        endpoint_template: str,
        label: str,
        error_context: str,
    ) -> None:
        """DELETE a resource by label.

        The label is always URL-encoded with quote_plus before substitution.

        :param endpoint_template: API path template with '{label}' placeholder
            (e.g. '/rest/ofscMetadata/v1/workZones/{label}')
        :type endpoint_template: str
        :param label: Resource label (will be URL-encoded)
        :type label: str
        :param error_context: Human-readable context for error messages
        :type error_context: str
        :raises OFSCNotFoundError: If the resource is not found (404)
        :raises OFSCAuthenticationError: If authentication fails (401)
        :raises OFSCAuthorizationError: If authorization fails (403)
        :raises OFSCApiError: For other API errors
        :raises OFSCNetworkError: For network/transport errors
        """
        encoded_label = quote_plus(label)
        url = urljoin(self.baseUrl, endpoint_template.format(label=encoded_label))

        try:
            response = await self._client.delete(url, headers=self.headers)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, error_context)
            raise  # satisfies type checker
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    # endregion
