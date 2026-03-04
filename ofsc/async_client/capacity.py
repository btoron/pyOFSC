"""Async version of OFSCapacity API module."""

from typing import Optional, Union
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
    ActivityBookingOptionsResponse,
    BookingClosingScheduleResponse,
    BookingClosingScheduleUpdateRequest,
    BookingFieldsDependenciesResponse,
    BookingStatusesResponse,
    BookingStatusesUpdateRequest,
    CapacityRequest,
    CsvList,
    GetCapacityResponse,
    GetQuotaRequest,
    GetQuotaResponse,
    OFSConfig,
    QuotaUpdateRequest,
    QuotaUpdateResponse,
    ShowBookingGridRequest,
    ShowBookingGridResponse,
)
from ..capacity import _convert_model_to_api_params


class AsyncOFSCapacity:
    """Async version of OFSCapacity API module."""

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

    # region Available Capacity

    async def get_available_capacity(
        self,
        dates: Union[list[str], CsvList, str],
        areas: Optional[Union[list[str], CsvList, str]] = None,
        categories: Optional[Union[list[str], CsvList, str]] = None,
        aggregateResults: Optional[bool] = None,
        availableTimeIntervals: str = "all",
        calendarTimeIntervals: str = "all",
        fields: Optional[Union[list[str], CsvList, str]] = None,
    ) -> GetCapacityResponse:
        """Get available capacity for a given resource or group of resources.

        Args:
            dates: Required. List of dates in YYYY-MM-DD format, CsvList, or CSV string
            areas: Optional. List of capacity area labels, CsvList, or CSV string
            categories: Optional. List of capacity categories, CsvList, or CSV string
            aggregateResults: Optional. Boolean to aggregate results
            availableTimeIntervals: Time interval specification (default: "all")
            calendarTimeIntervals: Calendar interval specification (default: "all")
            fields: Optional. List of fields to include in response

        Returns:
            GetCapacityResponse: Capacity data by date and area

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        capacity_request = CapacityRequest(
            dates=dates,
            areas=areas,
            categories=categories,
            aggregateResults=aggregateResults,
            availableTimeIntervals=availableTimeIntervals,
            calendarTimeIntervals=calendarTimeIntervals,
            fields=fields,
        )
        params = _convert_model_to_api_params(capacity_request)
        url = urljoin(self.baseUrl, "/rest/ofscCapacity/v1/capacity")
        try:
            response = await self._client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return GetCapacityResponse.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to get available capacity")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    # Deprecated camelCase alias
    getAvailableCapacity = get_available_capacity

    # endregion

    # region Quota

    async def get_quota(
        self,
        dates: Union[list[str], CsvList, str],
        areas: Optional[Union[list[str], CsvList, str]] = None,
        categories: Optional[Union[list[str], CsvList, str]] = None,
        aggregateResults: Optional[bool] = None,
        categoryLevel: Optional[bool] = None,
        intervalLevel: Optional[bool] = None,
        returnStatuses: Optional[bool] = None,
        timeSlotLevel: Optional[bool] = None,
    ) -> GetQuotaResponse:
        """Get quota information for specified areas and dates.

        Args:
            dates: Required. List of dates in YYYY-MM-DD format, CsvList, or CSV string
            areas: Optional. List of capacity area labels, CsvList, or CSV string
            categories: Optional. List of capacity categories, CsvList, or CSV string
            aggregateResults: Optional. Boolean to aggregate results
            categoryLevel: Optional. Boolean for category level reporting
            intervalLevel: Optional. Boolean for interval level reporting
            returnStatuses: Optional. Boolean for status return flag
            timeSlotLevel: Optional. Boolean for time slot level reporting

        Returns:
            GetQuotaResponse: Quota data by date and area

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        quota_request = GetQuotaRequest(
            dates=dates,
            areas=areas,
            categories=categories,
            aggregateResults=aggregateResults,
            categoryLevel=categoryLevel,
            intervalLevel=intervalLevel,
            returnStatuses=returnStatuses,
            timeSlotLevel=timeSlotLevel,
        )
        params = _convert_model_to_api_params(quota_request)
        url = urljoin(self.baseUrl, "/rest/ofscCapacity/v2/quota")
        try:
            response = await self._client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return GetQuotaResponse.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to get quota")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def update_quota(
        self,
        data: Union[QuotaUpdateRequest, dict],
    ) -> QuotaUpdateResponse:
        """Update quota values via PATCH.

        Args:
            data: QuotaUpdateRequest model or dict with items list

        Returns:
            QuotaUpdateResponse: Updated quota data

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCValidationError: If request data is invalid (400, 422)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        if isinstance(data, dict):
            data = QuotaUpdateRequest.model_validate(data)
        url = urljoin(self.baseUrl, "/rest/ofscCapacity/v2/quota")
        try:
            response = await self._client.patch(
                url, headers=self.headers, json=data.model_dump(exclude_none=True)
            )
            response.raise_for_status()
            return QuotaUpdateResponse.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to update quota")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    # Deprecated camelCase alias
    getQuota = get_quota

    # endregion

    # region Activity Booking Options

    async def get_activity_booking_options(
        self,
        dates: Union[list[str], str],
        areas: Optional[Union[list[str], str]] = None,
        activityType: Optional[str] = None,
        duration: Optional[int] = None,
        workSkills: Optional[Union[list[str], str]] = None,
        timeSlots: Optional[Union[list[str], str]] = None,
        categories: Optional[Union[list[str], str]] = None,
        languageCode: Optional[str] = None,
        timeZone: Optional[str] = None,
        resourceId: Optional[str] = None,
        activityId: Optional[str] = None,
        workZone: Optional[str] = None,
        determineAreaByWorkZone: Optional[bool] = None,
        aggregateResults: Optional[bool] = None,
        returnAvailableSlots: Optional[bool] = None,
        returnStatuses: Optional[bool] = None,
    ) -> ActivityBookingOptionsResponse:
        """Get activity booking options for given dates and areas.

        Args:
            dates: Required. Date or list of dates in YYYY-MM-DD format
            areas: Optional. Capacity area label(s)
            activityType: Optional. Activity type label
            duration: Optional. Activity duration in minutes
            workSkills: Optional. Work skill label(s)
            timeSlots: Optional. Time slot label(s)
            categories: Optional. Category label(s)
            languageCode: Optional. Language code for translations
            timeZone: Optional. Time zone for date/time values
            resourceId: Optional. Resource identifier
            activityId: Optional. Activity identifier
            workZone: Optional. Work zone label
            determineAreaByWorkZone: Optional. Auto-determine area by work zone (default: true in API)
            aggregateResults: Optional. Aggregate results flag
            returnAvailableSlots: Optional. Return available slots flag
            returnStatuses: Optional. Return statuses flag

        Returns:
            ActivityBookingOptionsResponse: Booking options by date and area

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        params: dict = {}
        if isinstance(dates, list):
            params["dates"] = ",".join(dates)
        else:
            params["dates"] = dates
        if areas is not None:
            params["areas"] = ",".join(areas) if isinstance(areas, list) else areas
        if activityType is not None:
            params["activityType"] = activityType
        if duration is not None:
            params["duration"] = duration
        if workSkills is not None:
            params["workSkills"] = (
                ",".join(workSkills) if isinstance(workSkills, list) else workSkills
            )
        if timeSlots is not None:
            params["timeSlots"] = (
                ",".join(timeSlots) if isinstance(timeSlots, list) else timeSlots
            )
        if categories is not None:
            params["categories"] = (
                ",".join(categories) if isinstance(categories, list) else categories
            )
        if languageCode is not None:
            params["languageCode"] = languageCode
        if timeZone is not None:
            params["timeZone"] = timeZone
        if resourceId is not None:
            params["resourceId"] = resourceId
        if activityId is not None:
            params["activityId"] = activityId
        if workZone is not None:
            params["workZone"] = workZone
        if determineAreaByWorkZone is not None:
            params["determineAreaByWorkZone"] = str(determineAreaByWorkZone).lower()
        if aggregateResults is not None:
            params["aggregateResults"] = str(aggregateResults).lower()
        if returnAvailableSlots is not None:
            params["returnAvailableSlots"] = str(returnAvailableSlots).lower()
        if returnStatuses is not None:
            params["returnStatuses"] = str(returnStatuses).lower()

        url = urljoin(self.baseUrl, "/rest/ofscCapacity/v1/activityBookingOptions")
        try:
            response = await self._client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return ActivityBookingOptionsResponse.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to get activity booking options")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    # endregion

    # region Booking Closing Schedule

    async def get_booking_closing_schedule(
        self,
        areas: Union[list[str], str],
    ) -> BookingClosingScheduleResponse:
        """Get booking closing schedule for specified capacity areas.

        Args:
            areas: Required. Capacity area label(s)

        Returns:
            BookingClosingScheduleResponse: Closing schedule items

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        params: dict = {}
        params["areas"] = ",".join(areas) if isinstance(areas, list) else areas

        url = urljoin(self.baseUrl, "/rest/ofscCapacity/v1/bookingClosingSchedule")
        try:
            response = await self._client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return BookingClosingScheduleResponse.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to get booking closing schedule")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def update_booking_closing_schedule(
        self,
        data: Union[BookingClosingScheduleUpdateRequest, dict],
    ) -> BookingClosingScheduleResponse:
        """Update booking closing schedule via PATCH.

        Args:
            data: BookingClosingScheduleUpdateRequest model or dict with items list

        Returns:
            BookingClosingScheduleResponse: Updated closing schedule

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCValidationError: If request data is invalid (400, 422)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        if isinstance(data, dict):
            data = BookingClosingScheduleUpdateRequest.model_validate(data)
        url = urljoin(self.baseUrl, "/rest/ofscCapacity/v1/bookingClosingSchedule")
        try:
            response = await self._client.patch(
                url, headers=self.headers, json=data.model_dump(exclude_none=True)
            )
            response.raise_for_status()
            return BookingClosingScheduleResponse.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to update booking closing schedule")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    # endregion

    # region Booking Statuses

    async def get_booking_statuses(
        self,
        dates: Union[list[str], str],
        areas: Optional[Union[list[str], str]] = None,
    ) -> BookingStatusesResponse:
        """Get booking statuses for specified dates and areas.

        Args:
            dates: Required. Date or list of dates in YYYY-MM-DD format
            areas: Optional. Capacity area label(s)

        Returns:
            BookingStatusesResponse: Booking status items

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        params: dict = {}
        params["dates"] = ",".join(dates) if isinstance(dates, list) else dates
        if areas is not None:
            params["areas"] = ",".join(areas) if isinstance(areas, list) else areas

        url = urljoin(self.baseUrl, "/rest/ofscCapacity/v1/bookingStatuses")
        try:
            response = await self._client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return BookingStatusesResponse.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to get booking statuses")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def update_booking_statuses(
        self,
        data: Union[BookingStatusesUpdateRequest, dict],
    ) -> BookingStatusesResponse:
        """Update booking statuses via PATCH.

        Args:
            data: BookingStatusesUpdateRequest model or dict with items list

        Returns:
            BookingStatusesResponse: Updated booking statuses

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCValidationError: If request data is invalid (400, 422)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        if isinstance(data, dict):
            data = BookingStatusesUpdateRequest.model_validate(data)
        url = urljoin(self.baseUrl, "/rest/ofscCapacity/v1/bookingStatuses")
        try:
            response = await self._client.patch(
                url, headers=self.headers, json=data.model_dump(exclude_none=True)
            )
            response.raise_for_status()
            return BookingStatusesResponse.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to update booking statuses")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    # endregion

    # region Show Booking Grid

    async def show_booking_grid(
        self,
        data: Union[ShowBookingGridRequest, dict],
    ) -> ShowBookingGridResponse:
        """Show booking grid for given dates, areas, and activity.

        Args:
            data: ShowBookingGridRequest model or dict with dates, areas, and activity

        Returns:
            ShowBookingGridResponse: Booking grid items by area and date

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCValidationError: If request data is invalid (400, 422)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        if isinstance(data, dict):
            data = ShowBookingGridRequest.model_validate(data)
        url = urljoin(self.baseUrl, "/rest/ofscCapacity/v1/showBookingGrid")
        try:
            response = await self._client.post(
                url, headers=self.headers, json=data.model_dump(exclude_none=True)
            )
            response.raise_for_status()
            return ShowBookingGridResponse.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to show booking grid")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    # endregion

    # region Booking Fields Dependencies

    async def get_booking_fields_dependencies(
        self,
        areas: Optional[Union[list[str], str]] = None,
    ) -> BookingFieldsDependenciesResponse:
        """Get booking fields dependencies.

        Args:
            areas: Optional. Capacity area label(s)

        Returns:
            BookingFieldsDependenciesResponse: Field dependency definitions

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        params: dict = {}
        if areas is not None:
            params["areas"] = ",".join(areas) if isinstance(areas, list) else areas

        url = urljoin(self.baseUrl, "/rest/ofscCapacity/v1/bookingFieldsDependencies")
        try:
            response = await self._client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return BookingFieldsDependenciesResponse.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to get booking fields dependencies")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    # endregion
