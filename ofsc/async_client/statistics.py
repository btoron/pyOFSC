"""Async version of OFSC Statistics API module."""

from typing import Optional, Union
from urllib.parse import urljoin

import httpx

from ..exceptions import OFSCNetworkError
from ._base import AsyncClientBase
from ..models import (
    ActivityDurationStatRequestList,
    ActivityDurationStatsList,
    ActivityTravelStatRequestList,
    ActivityTravelStatsList,
    AirlineDistanceBasedTravelList,
    AirlineDistanceBasedTravelRequestList,
    StatisticsPatchResponse,
)


class AsyncOFSStatistics(AsyncClientBase):
    """Async version of OFSC Statistics API module."""

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
        url = urljoin(self.baseUrl, "/rest/ofscStatistics/v1/airlineDistanceBasedTravel")
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

    # region Write Operations

    async def update_activity_duration_stats(
        self,
        data: Union[ActivityDurationStatRequestList, dict],
    ) -> StatisticsPatchResponse:
        """Update activity duration statistics overrides.

        Args:
            data: List of activity duration stat overrides to apply.

        Returns:
            StatisticsPatchResponse: Result with status and updatedRecords count.

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCValidationError: If request data is invalid (400/422)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        if isinstance(data, dict):
            data = ActivityDurationStatRequestList.model_validate(data)
        url = urljoin(self.baseUrl, "/rest/ofscStatistics/v1/activityDurationStats")
        try:
            response = await self._client.patch(
                url,
                headers=self.headers,
                json=data.model_dump(mode="python", exclude_none=True),
            )
            response.raise_for_status()
            return StatisticsPatchResponse.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to update activity duration stats")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def update_activity_travel_stats(
        self,
        data: Union[ActivityTravelStatRequestList, dict],
    ) -> StatisticsPatchResponse:
        """Update activity travel statistics overrides.

        Args:
            data: List of activity travel stat overrides to apply.

        Returns:
            StatisticsPatchResponse: Result with status and updatedRecords count.

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCConflictError: If "Detect activity travel keys automatically" is enabled (409)
            OFSCValidationError: If request data is invalid (400/422)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        if isinstance(data, dict):
            data = ActivityTravelStatRequestList.model_validate(data)
        url = urljoin(self.baseUrl, "/rest/ofscStatistics/v1/activityTravelStats")
        try:
            response = await self._client.patch(
                url,
                headers=self.headers,
                json=data.model_dump(mode="python", exclude_none=True),
            )
            response.raise_for_status()
            return StatisticsPatchResponse.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to update activity travel stats")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def update_airline_distance_based_travel(
        self,
        data: Union[AirlineDistanceBasedTravelRequestList, dict],
    ) -> StatisticsPatchResponse:
        """Update airline distance based travel overrides.

        Args:
            data: List of airline distance travel overrides to apply.

        Returns:
            StatisticsPatchResponse: Result with status and updatedRecords count.

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCConflictError: If "Detect activity travel keys automatically" is enabled (409)
            OFSCValidationError: If request data is invalid (400/422)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        if isinstance(data, dict):
            data = AirlineDistanceBasedTravelRequestList.model_validate(data)
        url = urljoin(self.baseUrl, "/rest/ofscStatistics/v1/airlineDistanceBasedTravel")
        try:
            response = await self._client.patch(
                url,
                headers=self.headers,
                json=data.model_dump(mode="python", exclude_none=True),
            )
            response.raise_for_status()
            return StatisticsPatchResponse.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to update airline distance based travel")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    # endregion
