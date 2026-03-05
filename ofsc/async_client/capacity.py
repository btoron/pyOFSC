"""Async version of OFSCapacity API module."""

from typing import Any, Optional, Union
from urllib.parse import urljoin

import httpx

from ..exceptions import OFSCNetworkError
from ._base import AsyncClientBase
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
    QuotaUpdateRequest,
    QuotaUpdateResponse,
    ShowBookingGridRequest,
    ShowBookingGridResponse,
)


class AsyncOFSCapacity(AsyncClientBase):
    """Async version of OFSCapacity API module."""

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
        params: dict = {
            "dates": self._to_csv_param(capacity_request.dates),
            "availableTimeIntervals": capacity_request.availableTimeIntervals,
            "calendarTimeIntervals": capacity_request.calendarTimeIntervals,
        }
        if capacity_request.areas is not None:
            params["areas"] = self._to_csv_param(capacity_request.areas)
        if capacity_request.categories is not None:
            params["categories"] = self._to_csv_param(capacity_request.categories)
        if capacity_request.aggregateResults is not None:
            params["aggregateResults"] = str(capacity_request.aggregateResults).lower()
        if capacity_request.fields is not None:
            params["fields"] = self._to_csv_param(capacity_request.fields)

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
        params: dict = {"dates": self._to_csv_param(quota_request.dates)}
        if quota_request.areas is not None:
            params["areas"] = self._to_csv_param(quota_request.areas)
        if quota_request.categories is not None:
            params["categories"] = self._to_csv_param(quota_request.categories)
        if quota_request.aggregateResults is not None:
            params["aggregateResults"] = str(quota_request.aggregateResults).lower()
        if quota_request.categoryLevel is not None:
            params["categoryLevel"] = str(quota_request.categoryLevel).lower()
        if quota_request.intervalLevel is not None:
            params["intervalLevel"] = str(quota_request.intervalLevel).lower()
        if quota_request.returnStatuses is not None:
            params["returnStatuses"] = str(quota_request.returnStatuses).lower()
        if quota_request.timeSlotLevel is not None:
            params["timeSlotLevel"] = str(quota_request.timeSlotLevel).lower()

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
        return await self._patch_item(
            "/rest/ofscCapacity/v2/quota",
            data,
            QuotaUpdateResponse,
            "Failed to update quota",
        )

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
        **kwargs: Any,
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
        params: dict = {"dates": self._to_csv_param(dates)}
        if areas is not None:
            params["areas"] = self._to_csv_param(areas)
        if activityType is not None:
            params["activityType"] = activityType
        if duration is not None:
            params["duration"] = duration
        if workSkills is not None:
            params["workSkills"] = self._to_csv_param(workSkills)
        if timeSlots is not None:
            params["timeSlots"] = self._to_csv_param(timeSlots)
        if categories is not None:
            params["categories"] = self._to_csv_param(categories)
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
        params.update(kwargs)

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
        params: dict = {"areas": self._to_csv_param(areas)}

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
        return await self._patch_item(
            "/rest/ofscCapacity/v1/bookingClosingSchedule",
            data,
            BookingClosingScheduleResponse,
            "Failed to update booking closing schedule",
        )

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
        params: dict = {"dates": self._to_csv_param(dates)}
        if areas is not None:
            params["areas"] = self._to_csv_param(areas)

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
        return await self._patch_item(
            "/rest/ofscCapacity/v1/bookingStatuses",
            data,
            BookingStatusesResponse,
            "Failed to update booking statuses",
        )

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
        return await self._post_item(
            "/rest/ofscCapacity/v1/showBookingGrid",
            data,
            ShowBookingGridResponse,
            "Failed to show booking grid",
        )

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
            params["areas"] = self._to_csv_param(areas)

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
