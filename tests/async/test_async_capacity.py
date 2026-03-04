"""Async tests for capacity operations."""

from datetime import date, timedelta
from unittest.mock import AsyncMock, Mock

import httpx
import pytest

from ofsc.exceptions import OFSCAuthenticationError
from ofsc.models import (
    ActivityBookingOptionsResponse,
    BookingClosingScheduleResponse,
    BookingClosingScheduleUpdateRequest,
    BookingFieldsDependenciesResponse,
    BookingStatusesResponse,
    BookingStatusesUpdateRequest,
    GetCapacityResponse,
    GetQuotaResponse,
    QuotaUpdateRequest,
    QuotaUpdateResponse,
    ShowBookingGridRequest,
    ShowBookingGridResponse,
)


# region get_available_capacity


class TestAsyncGetAvailableCapacityLive:
    """Live tests for get_available_capacity."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_available_capacity(self, async_instance):
        """Test get_available_capacity with actual API."""
        result = await async_instance.capacity.get_available_capacity(dates="2026-03-03")
        assert isinstance(result, GetCapacityResponse)
        assert hasattr(result, "items")
        assert isinstance(result.items, list)

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_available_capacity_with_intervals(self, async_instance):
        """Test get_available_capacity with interval options."""
        result = await async_instance.capacity.get_available_capacity(
            dates=["2026-03-03", "2026-03-04"],
            availableTimeIntervals="all",
            calendarTimeIntervals="all",
        )
        assert isinstance(result, GetCapacityResponse)


class TestAsyncGetAvailableCapacity:
    """Mocked tests for get_available_capacity."""

    @pytest.mark.asyncio
    async def test_get_available_capacity_returns_model(self, mock_instance):
        """Test that get_available_capacity returns GetCapacityResponse model."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "date": "2026-03-03",
                    "areas": [
                        {
                            "label": "FLUSA",
                            "name": "Florida USA",
                            "calendar": {"count": [8], "minutes": [480]},
                            "available": {"count": [5], "minutes": [300]},
                            "categories": [],
                        }
                    ],
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_instance.capacity._client.get = AsyncMock(return_value=mock_response)

        result = await mock_instance.capacity.get_available_capacity(dates="2026-03-03")

        assert isinstance(result, GetCapacityResponse)
        assert len(result.items) == 1
        assert result.items[0].date == "2026-03-03"
        assert result.items[0].areas[0].label == "FLUSA"

    @pytest.mark.asyncio
    async def test_get_available_capacity_with_list_dates(self, mock_instance):
        """Test get_available_capacity with list of dates."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": []}
        mock_response.raise_for_status = Mock()
        mock_instance.capacity._client.get = AsyncMock(return_value=mock_response)

        result = await mock_instance.capacity.get_available_capacity(dates=["2026-03-03", "2026-03-04"])

        assert isinstance(result, GetCapacityResponse)
        call_kwargs = mock_instance.capacity._client.get.call_args
        params = call_kwargs.kwargs.get("params", call_kwargs.args[1] if len(call_kwargs.args) > 1 else {})
        assert "dates" in params

    @pytest.mark.asyncio
    async def test_get_available_capacity_auth_error(self, mock_instance):
        """Test that 401 raises OFSCAuthenticationError."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "type": "about:blank",
            "title": "Unauthorized",
            "detail": "Authentication required",
        }
        mock_response.text = "Unauthorized"
        http_error = httpx.HTTPStatusError("401", request=Mock(), response=mock_response)
        mock_response.raise_for_status = Mock(side_effect=http_error)
        mock_instance.capacity._client.get = AsyncMock(return_value=mock_response)

        with pytest.raises(OFSCAuthenticationError):
            await mock_instance.capacity.get_available_capacity(dates="2026-03-03")

    @pytest.mark.asyncio
    async def test_getAvailableCapacity_alias(self, mock_instance):
        """Test deprecated camelCase alias works."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": []}
        mock_response.raise_for_status = Mock()
        mock_instance.capacity._client.get = AsyncMock(return_value=mock_response)

        result = await mock_instance.capacity.getAvailableCapacity(dates="2026-03-03")
        assert isinstance(result, GetCapacityResponse)


# endregion

# region get_quota


class TestAsyncGetQuotaLive:
    """Live tests for get_quota."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_quota(self, async_instance):
        """Test get_quota with actual API."""
        result = await async_instance.capacity.get_quota(dates="2026-03-03")
        assert isinstance(result, GetQuotaResponse)
        assert hasattr(result, "items")
        assert isinstance(result.items, list)

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_quota_with_options(self, async_instance):
        """Test get_quota with boolean options."""
        result = await async_instance.capacity.get_quota(
            dates="2026-03-03",
            categoryLevel=True,
            intervalLevel=True,
        )
        assert isinstance(result, GetQuotaResponse)


class TestAsyncGetQuota:
    """Mocked tests for get_quota."""

    @pytest.mark.asyncio
    async def test_get_quota_returns_model(self, mock_instance):
        """Test that get_quota returns GetQuotaResponse model."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "date": "2026-03-03",
                    "areas": [
                        {
                            "label": "FLUSA",
                            "name": "Florida USA",
                            "quota": 10,
                            "used": 3,
                            "categories": [],
                            "intervals": [],
                        }
                    ],
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_instance.capacity._client.get = AsyncMock(return_value=mock_response)

        result = await mock_instance.capacity.get_quota(dates="2026-03-03")

        assert isinstance(result, GetQuotaResponse)
        assert len(result.items) == 1
        assert result.items[0].date == "2026-03-03"

    @pytest.mark.asyncio
    async def test_getQuota_alias(self, mock_instance):
        """Test deprecated camelCase alias works."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": []}
        mock_response.raise_for_status = Mock()
        mock_instance.capacity._client.get = AsyncMock(return_value=mock_response)

        result = await mock_instance.capacity.getQuota(dates="2026-03-03")
        assert isinstance(result, GetQuotaResponse)


# endregion

# region update_quota


class TestAsyncUpdateQuota:
    """Mocked tests for update_quota (PATCH - no live tests)."""

    @pytest.mark.asyncio
    async def test_update_quota_with_model(self, mock_instance):
        """Test update_quota with QuotaUpdateRequest model."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": []}
        mock_response.raise_for_status = Mock()
        mock_instance.capacity._client.patch = AsyncMock(return_value=mock_response)

        request = QuotaUpdateRequest.model_validate(
            {
                "items": [
                    {
                        "date": "2026-03-03",
                        "areas": [{"label": "FLUSA", "quota": 10}],
                    }
                ]
            }
        )
        result = await mock_instance.capacity.update_quota(request)
        assert isinstance(result, QuotaUpdateResponse)

    @pytest.mark.asyncio
    async def test_update_quota_with_dict(self, mock_instance):
        """Test update_quota with dict input."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": []}
        mock_response.raise_for_status = Mock()
        mock_instance.capacity._client.patch = AsyncMock(return_value=mock_response)

        result = await mock_instance.capacity.update_quota(
            {
                "items": [
                    {
                        "date": "2026-03-03",
                        "areas": [{"label": "FLUSA", "quota": 10}],
                    }
                ]
            }
        )
        assert isinstance(result, QuotaUpdateResponse)

    @pytest.mark.asyncio
    async def test_update_quota_calls_patch(self, mock_instance):
        """Test that update_quota uses PATCH method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": []}
        mock_response.raise_for_status = Mock()
        mock_instance.capacity._client.patch = AsyncMock(return_value=mock_response)

        await mock_instance.capacity.update_quota({"items": [{"date": "2026-03-03", "areas": []}]})
        assert mock_instance.capacity._client.patch.called


# endregion

# region get_activity_booking_options


class TestAsyncGetActivityBookingOptionsLive:
    """Live tests for get_activity_booking_options."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_activity_booking_options(self, async_instance, workzone_activity_type, workzone_postal_code):
        """Test get_activity_booking_options with actual API."""
        result = await async_instance.capacity.get_activity_booking_options(
            dates="2026-03-03",
            activityType=workzone_activity_type,
            postalCode=workzone_postal_code,
        )
        assert isinstance(result, ActivityBookingOptionsResponse)
        assert hasattr(result, "items")


class TestAsyncGetActivityBookingOptions:
    """Mocked tests for get_activity_booking_options."""

    @pytest.mark.asyncio
    async def test_get_activity_booking_options_returns_model(self, mock_instance):
        """Test that get_activity_booking_options returns correct model."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "date": "2026-03-03",
                    "areas": [
                        {
                            "label": "FLUSA",
                            "name": "Florida USA",
                            "timeSlots": [],
                        }
                    ],
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_instance.capacity._client.get = AsyncMock(return_value=mock_response)

        result = await mock_instance.capacity.get_activity_booking_options(dates="2026-03-03")

        assert isinstance(result, ActivityBookingOptionsResponse)
        assert len(result.items) == 1

    @pytest.mark.asyncio
    async def test_get_activity_booking_options_with_all_params(self, mock_instance):
        """Test get_activity_booking_options with all optional parameters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": []}
        mock_response.raise_for_status = Mock()
        mock_instance.capacity._client.get = AsyncMock(return_value=mock_response)

        result = await mock_instance.capacity.get_activity_booking_options(
            dates=["2026-03-03", "2026-03-04"],
            areas=["FLUSA"],
            activityType="LU",
            duration=60,
            aggregateResults=True,
        )

        assert isinstance(result, ActivityBookingOptionsResponse)
        call_kwargs = mock_instance.capacity._client.get.call_args
        params = call_kwargs.kwargs.get("params", {})
        assert params.get("activityType") == "LU"
        assert params.get("duration") == 60
        assert params.get("aggregateResults") == "true"


# endregion

# region get_booking_closing_schedule


class TestAsyncGetBookingClosingScheduleLive:
    """Live tests for get_booking_closing_schedule."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_booking_closing_schedule(self, async_instance):
        """Test get_booking_closing_schedule with actual API."""
        result = await async_instance.capacity.get_booking_closing_schedule(areas=["CAUSA"])
        assert isinstance(result, BookingClosingScheduleResponse)
        assert hasattr(result, "items")


class TestAsyncGetBookingClosingSchedule:
    """Mocked tests for get_booking_closing_schedule."""

    @pytest.mark.asyncio
    async def test_get_booking_closing_schedule_returns_model(self, mock_instance):
        """Test that get_booking_closing_schedule returns correct model."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "areaLabel": "FLUSA",
                    "date": "2026-03-03",
                    "closingTime": "17:00",
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_instance.capacity._client.get = AsyncMock(return_value=mock_response)

        result = await mock_instance.capacity.get_booking_closing_schedule(areas="FLUSA")

        assert isinstance(result, BookingClosingScheduleResponse)
        assert len(result.items) == 1
        assert result.items[0].areaLabel == "FLUSA"

    @pytest.mark.asyncio
    async def test_get_booking_closing_schedule_with_areas(self, mock_instance):
        """Test get_booking_closing_schedule with areas parameter."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": []}
        mock_response.raise_for_status = Mock()
        mock_instance.capacity._client.get = AsyncMock(return_value=mock_response)

        await mock_instance.capacity.get_booking_closing_schedule(areas=["FLUSA", "CAUSA"])

        call_kwargs = mock_instance.capacity._client.get.call_args
        params = call_kwargs.kwargs.get("params", {})
        assert "FLUSA" in params.get("areas", "")
        assert "CAUSA" in params.get("areas", "")


# endregion

# region update_booking_closing_schedule


class TestAsyncUpdateBookingClosingSchedule:
    """Mocked tests for update_booking_closing_schedule (PATCH - no live tests)."""

    @pytest.mark.asyncio
    async def test_update_booking_closing_schedule_with_model(self, mock_instance):
        """Test update_booking_closing_schedule with model input."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": []}
        mock_response.raise_for_status = Mock()
        mock_instance.capacity._client.patch = AsyncMock(return_value=mock_response)

        request = BookingClosingScheduleUpdateRequest.model_validate(
            {
                "items": [
                    {
                        "areaLabel": "FLUSA",
                        "date": "2026-03-03",
                        "closingTime": "17:00",
                    }
                ]
            }
        )
        result = await mock_instance.capacity.update_booking_closing_schedule(request)
        assert isinstance(result, BookingClosingScheduleResponse)

    @pytest.mark.asyncio
    async def test_update_booking_closing_schedule_with_dict(self, mock_instance):
        """Test update_booking_closing_schedule with dict input."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": []}
        mock_response.raise_for_status = Mock()
        mock_instance.capacity._client.patch = AsyncMock(return_value=mock_response)

        result = await mock_instance.capacity.update_booking_closing_schedule({"items": [{"areaLabel": "FLUSA", "date": "2026-03-03"}]})
        assert isinstance(result, BookingClosingScheduleResponse)
        assert mock_instance.capacity._client.patch.called


# endregion

# region get_booking_statuses


class TestAsyncGetBookingStatusesLive:
    """Live tests for get_booking_statuses."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_booking_statuses(self, async_instance):
        """Test get_booking_statuses with actual API."""
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        result = await async_instance.capacity.get_booking_statuses(dates=tomorrow)
        assert isinstance(result, BookingStatusesResponse)
        assert hasattr(result, "items")


class TestAsyncGetBookingStatuses:
    """Mocked tests for get_booking_statuses."""

    @pytest.mark.asyncio
    async def test_get_booking_statuses_returns_model(self, mock_instance):
        """Test that get_booking_statuses returns correct model."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "areaLabel": "FLUSA",
                    "date": "2026-03-03",
                    "status": "open",
                    "statuses": [],
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_instance.capacity._client.get = AsyncMock(return_value=mock_response)

        result = await mock_instance.capacity.get_booking_statuses(dates="2026-03-03")

        assert isinstance(result, BookingStatusesResponse)
        assert len(result.items) == 1
        assert result.items[0].areaLabel == "FLUSA"


# endregion

# region update_booking_statuses


class TestAsyncUpdateBookingStatuses:
    """Mocked tests for update_booking_statuses (PATCH - no live tests)."""

    @pytest.mark.asyncio
    async def test_update_booking_statuses_with_model(self, mock_instance):
        """Test update_booking_statuses with model input."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": []}
        mock_response.raise_for_status = Mock()
        mock_instance.capacity._client.patch = AsyncMock(return_value=mock_response)

        request = BookingStatusesUpdateRequest.model_validate(
            {
                "items": [
                    {
                        "areaLabel": "FLUSA",
                        "date": "2026-03-03",
                        "status": "closed",
                    }
                ]
            }
        )
        result = await mock_instance.capacity.update_booking_statuses(request)
        assert isinstance(result, BookingStatusesResponse)

    @pytest.mark.asyncio
    async def test_update_booking_statuses_with_dict(self, mock_instance):
        """Test update_booking_statuses with dict input."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": []}
        mock_response.raise_for_status = Mock()
        mock_instance.capacity._client.patch = AsyncMock(return_value=mock_response)

        result = await mock_instance.capacity.update_booking_statuses({"items": [{"areaLabel": "FLUSA", "date": "2026-03-03"}]})
        assert isinstance(result, BookingStatusesResponse)
        assert mock_instance.capacity._client.patch.called


# endregion

# region show_booking_grid


class TestAsyncShowBookingGrid:
    """Mocked tests for show_booking_grid (POST - no live tests by default)."""

    @pytest.mark.asyncio
    async def test_show_booking_grid_with_model(self, mock_instance):
        """Test show_booking_grid with ShowBookingGridRequest model."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "label": "FLUSA",
                    "name": "Florida USA",
                    "dates": [
                        {
                            "date": "2026-03-03",
                            "timeSlots": [
                                {
                                    "timeSlotLabel": "08-10",
                                    "timeFrom": "08:00",
                                    "timeTo": "10:00",
                                    "available": True,
                                }
                            ],
                        }
                    ],
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_instance.capacity._client.post = AsyncMock(return_value=mock_response)

        request = ShowBookingGridRequest.model_validate({"dates": ["2026-03-03"], "areas": ["FLUSA"]})
        result = await mock_instance.capacity.show_booking_grid(request)

        assert isinstance(result, ShowBookingGridResponse)
        assert len(result.items) == 1
        assert result.items[0].label == "FLUSA"

    @pytest.mark.asyncio
    async def test_show_booking_grid_with_dict(self, mock_instance):
        """Test show_booking_grid with dict input."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": []}
        mock_response.raise_for_status = Mock()
        mock_instance.capacity._client.post = AsyncMock(return_value=mock_response)

        result = await mock_instance.capacity.show_booking_grid({"dates": ["2026-03-03"]})
        assert isinstance(result, ShowBookingGridResponse)
        assert mock_instance.capacity._client.post.called

    @pytest.mark.asyncio
    async def test_show_booking_grid_calls_post(self, mock_instance):
        """Test that show_booking_grid uses POST method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": []}
        mock_response.raise_for_status = Mock()
        mock_instance.capacity._client.post = AsyncMock(return_value=mock_response)

        await mock_instance.capacity.show_booking_grid({"dates": "2026-03-03"})
        assert mock_instance.capacity._client.post.called


# endregion

# region get_booking_fields_dependencies


class TestAsyncGetBookingFieldsDependenciesLive:
    """Live tests for get_booking_fields_dependencies."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_booking_fields_dependencies(self, async_instance):
        """Test get_booking_fields_dependencies with actual API."""
        result = await async_instance.capacity.get_booking_fields_dependencies()
        assert isinstance(result, BookingFieldsDependenciesResponse)
        assert hasattr(result, "items")


class TestAsyncGetBookingFieldsDependencies:
    """Mocked tests for get_booking_fields_dependencies."""

    @pytest.mark.asyncio
    async def test_get_booking_fields_dependencies_returns_model(self, mock_instance):
        """Test that get_booking_fields_dependencies returns correct model."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "fieldName": "areaLabel",
                    "dependsOn": ["date"],
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_instance.capacity._client.get = AsyncMock(return_value=mock_response)

        result = await mock_instance.capacity.get_booking_fields_dependencies()

        assert isinstance(result, BookingFieldsDependenciesResponse)
        assert len(result.items) == 1
        assert result.items[0].fieldName == "areaLabel"

    @pytest.mark.asyncio
    async def test_get_booking_fields_dependencies_with_areas(self, mock_instance):
        """Test get_booking_fields_dependencies with areas filter."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": []}
        mock_response.raise_for_status = Mock()
        mock_instance.capacity._client.get = AsyncMock(return_value=mock_response)

        result = await mock_instance.capacity.get_booking_fields_dependencies(areas=["FLUSA"])
        assert isinstance(result, BookingFieldsDependenciesResponse)
        call_kwargs = mock_instance.capacity._client.get.call_args
        params = call_kwargs.kwargs.get("params", {})
        assert "FLUSA" in params.get("areas", "")

    @pytest.mark.asyncio
    async def test_get_booking_fields_dependencies_empty_response(self, mock_instance):
        """Test get_booking_fields_dependencies with empty items response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": []}
        mock_response.raise_for_status = Mock()
        mock_instance.capacity._client.get = AsyncMock(return_value=mock_response)

        result = await mock_instance.capacity.get_booking_fields_dependencies()
        assert isinstance(result, BookingFieldsDependenciesResponse)
        assert result.items == []


# endregion

# region Model Validation Tests


class TestAsyncCapacityModelValidation:
    """Tests validating model structures."""

    def test_get_capacity_response_empty(self):
        """Test GetCapacityResponse with empty items."""
        response = GetCapacityResponse.model_validate({"items": []})
        assert isinstance(response, GetCapacityResponse)
        assert response.items == []

    def test_get_quota_response_empty(self):
        """Test GetQuotaResponse with empty items."""
        response = GetQuotaResponse.model_validate({"items": []})
        assert isinstance(response, GetQuotaResponse)
        assert response.items == []

    def test_quota_update_request_validation(self):
        """Test QuotaUpdateRequest model validation."""
        request = QuotaUpdateRequest.model_validate(
            {
                "items": [
                    {
                        "date": "2026-03-03",
                        "areas": [
                            {
                                "label": "FLUSA",
                                "quota": 10,
                                "quotaIsClosed": False,
                            }
                        ],
                    }
                ]
            }
        )
        assert len(request.items) == 1
        assert request.items[0].date == "2026-03-03"
        assert request.items[0].areas[0].label == "FLUSA"
        assert request.items[0].areas[0].quota == 10

    def test_show_booking_grid_request_validation(self):
        """Test ShowBookingGridRequest model validation."""
        request = ShowBookingGridRequest.model_validate(
            {
                "dates": ["2026-03-03", "2026-03-04"],
                "areas": ["FLUSA"],
                "activity": {"activityType": "LU", "duration": 60},
            }
        )
        assert request.dates == ["2026-03-03", "2026-03-04"]
        assert request.areas == ["FLUSA"]
        assert request.activity is not None
        assert request.activity.activityType == "LU"

    def test_booking_closing_schedule_update_request_validation(self):
        """Test BookingClosingScheduleUpdateRequest model validation."""
        request = BookingClosingScheduleUpdateRequest.model_validate(
            {
                "items": [
                    {
                        "areaLabel": "FLUSA",
                        "date": "2026-03-03",
                        "closingTime": "17:00",
                    }
                ]
            }
        )
        assert len(request.items) == 1
        assert request.items[0].areaLabel == "FLUSA"
        assert request.items[0].closingTime == "17:00"

    def test_booking_statuses_update_request_validation(self):
        """Test BookingStatusesUpdateRequest model validation."""
        request = BookingStatusesUpdateRequest.model_validate({"items": [{"areaLabel": "FLUSA", "date": "2026-03-03", "status": "open"}]})
        assert len(request.items) == 1
        assert request.items[0].status == "open"

    def test_activity_booking_options_response_validation(self):
        """Test ActivityBookingOptionsResponse model validation."""
        response = ActivityBookingOptionsResponse.model_validate(
            {
                "items": [
                    {
                        "date": "2026-03-03",
                        "areas": [
                            {
                                "label": "FLUSA",
                                "timeSlots": [
                                    {
                                        "timeSlotLabel": "08-10",
                                        "available": True,
                                    }
                                ],
                            }
                        ],
                    }
                ]
            }
        )
        assert isinstance(response, ActivityBookingOptionsResponse)
        assert len(response.items) == 1
        assert response.items[0].areas[0].timeSlots[0].timeSlotLabel == "08-10"

    def test_booking_fields_dependencies_response_validation(self):
        """Test BookingFieldsDependenciesResponse model validation."""
        response = BookingFieldsDependenciesResponse.model_validate(
            {
                "items": [
                    {"fieldName": "areaLabel", "dependsOn": ["date"]},
                    {"fieldName": "timeSlot", "dependsOn": ["areaLabel", "date"]},
                ]
            }
        )
        assert isinstance(response, BookingFieldsDependenciesResponse)
        assert len(response.items) == 2
        assert response.items[0].fieldName == "areaLabel"
        assert response.items[1].dependsOn == ["areaLabel", "date"]


# endregion
