"""Async version of OFSC Statistics API module."""

from typing import Optional
from urllib.parse import urljoin

import httpx

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
from ..models import (
    ActivityDurationStatsList,
    ActivityTravelStatsList,
    AirlineDistanceBasedTravelList,
    OFSConfig,
)


class AsyncOFSStatistics:
    """Async version of OFSC Statistics API module."""

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
            headers["Authorization"] = "Basic " + self._config.basicAuthString.decode(
                "utf-8"
            )
        else:
            raise NotImplementedError("Token-based auth not yet implemented for async")
        return headers

    def _parse_error_response(self, response: httpx.Response) -> dict:
        """Parse OFSC error response format."""
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
        """Convert httpx exceptions to OFSC exceptions with error details."""
        status = e.response.status_code
        error_info = self._parse_error_response(e.response)

        message = (
            f"{context}: {error_info['detail']}" if context else error_info["detail"]
        )

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

    # region Activity Duration Stats

    async def get_activity_duration_stats(
        self,
        resource_id: Optional[str] = None,
        include_children: Optional[bool] = None,
        akey: Optional[str] = None,
        offset: int = 0,
        limit: int = 100,
    ) -> ActivityDurationStatsList:
        """Get activity duration statistics.

        Args:
            resource_id: Optional. Filter by resource ID
            include_children: Optional. Include child resources
            akey: Optional. Activity key filter
            offset: Starting record number (default 0)
            limit: Maximum number of records to return (default 100)

        Returns:
            ActivityDurationStatsList: Paginated list of activity duration stats

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, "/rest/ofscStatistics/v1/activityDurationStats")
        params: dict = {"offset": offset, "limit": limit}
        if resource_id is not None:
            params["resourceId"] = resource_id
        if include_children is not None:
            params["includeChildren"] = str(include_children).lower()
        if akey is not None:
            params["akey"] = akey

        try:
            response = await self._client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return ActivityDurationStatsList.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to get activity duration stats")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    # endregion

    # region Activity Travel Stats

    async def get_activity_travel_stats(
        self,
        region: Optional[str] = None,
        tkey: Optional[str] = None,
        fkey: Optional[str] = None,
        key_id: Optional[int] = None,
        offset: int = 0,
        limit: int = 100,
    ) -> ActivityTravelStatsList:
        """Get activity travel statistics.

        Args:
            region: Optional. Filter by region
            tkey: Optional. To-key filter
            fkey: Optional. From-key filter
            key_id: Optional. Key ID filter
            offset: Starting record number (default 0)
            limit: Maximum number of records to return (default 100)

        Returns:
            ActivityTravelStatsList: Paginated list of activity travel stats

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, "/rest/ofscStatistics/v1/activityTravelStats")
        params: dict = {"offset": offset, "limit": limit}
        if region is not None:
            params["region"] = region
        if tkey is not None:
            params["tkey"] = tkey
        if fkey is not None:
            params["fkey"] = fkey
        if key_id is not None:
            params["keyId"] = key_id

        try:
            response = await self._client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return ActivityTravelStatsList.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to get activity travel stats")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    # endregion

    # region Airline Distance Based Travel

    async def get_airline_distance_based_travel(
        self,
        level: Optional[str] = None,
        key: Optional[str] = None,
        distance: Optional[int] = None,
        key_id: Optional[int] = None,
        offset: int = 0,
        limit: int = 100,
    ) -> AirlineDistanceBasedTravelList:
        """Get airline distance based travel data.

        Args:
            level: Optional. Filter by level
            key: Optional. Filter by key
            distance: Optional. Filter by distance
            key_id: Optional. Key ID filter
            offset: Starting record number (default 0)
            limit: Maximum number of records to return (default 100)

        Returns:
            AirlineDistanceBasedTravelList: Paginated list of airline distance travel data

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(
            self.baseUrl, "/rest/ofscStatistics/v1/airlineDistanceBasedTravel"
        )
        params: dict = {"offset": offset, "limit": limit}
        if level is not None:
            params["level"] = level
        if key is not None:
            params["key"] = key
        if distance is not None:
            params["distance"] = distance
        if key_id is not None:
            params["keyId"] = key_id

        try:
            response = await self._client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return AirlineDistanceBasedTravelList.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to get airline distance based travel")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    # endregion
