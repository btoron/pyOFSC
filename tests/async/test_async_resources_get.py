"""Tests for async resource GET operations."""

import inspect
import json
from datetime import date
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

from ofsc.async_client import AsyncOFSC
from ofsc.exceptions import OFSCNotFoundError
from ofsc.models import (
    AssignedLocationsResponse,
    CalendarView,
    CalendarsListResponse,
    InventoryListResponse,
    LocationListResponse,
    PositionHistoryResponse,
    Resource,
    ResourceAssistantsResponse,
    ResourceListResponse,
    ResourcePlansResponse,
    ResourceRouteResponse,
    ResourceUsersListResponse,
    ResourceWorkScheduleResponse,
    ResourceWorkskillListResponse,
    ResourceWorkzoneListResponse,
)


# ===================================================================
# GET RESOURCES (LIST)
# ===================================================================


class TestAsyncGetResourcesLive:
    """Live tests for get_resources."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_resources(self, async_instance: AsyncOFSC):
        """Test get_resources with actual API."""
        result = await async_instance.core.get_resources(limit=10)

        assert isinstance(result, ResourceListResponse)
        assert hasattr(result, "items")
        assert hasattr(result, "totalResults")
        assert len(result.items) <= 10
        if len(result.items) > 0:
            assert isinstance(result.items[0], Resource)

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_resources_with_expand(self, async_instance: AsyncOFSC):
        """Test get_resources with expand parameters."""
        result = await async_instance.core.get_resources(limit=2, expand_inventories=True, expand_workskills=True)

        assert isinstance(result, ResourceListResponse)
        assert len(result.items) <= 2


# ===================================================================
# GET RESOURCE (SINGLE)
# ===================================================================


class TestAsyncGetResourceLive:
    """Live tests for get_resource."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_resource_individual(self, async_instance: AsyncOFSC):
        """Test get_resource for individual resource."""
        result = await async_instance.core.get_resource("33001")

        assert isinstance(result, Resource)
        assert result.resourceId == "33001"

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_resource_bucket(self, async_instance: AsyncOFSC):
        """Test get_resource for bucket resource."""
        result = await async_instance.core.get_resource("FLUSA")

        assert isinstance(result, Resource)
        assert result.resourceId == "FLUSA"

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_resource_group(self, async_instance: AsyncOFSC):
        """Test get_resource for group resource."""
        result = await async_instance.core.get_resource("ACMECONTRACTOR")

        assert isinstance(result, Resource)
        assert result.resourceId == "ACMECONTRACTOR"

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_resource_not_found(self, async_instance: AsyncOFSC):
        """Test get_resource with non-existent resource."""
        with pytest.raises(OFSCNotFoundError):
            await async_instance.core.get_resource("NONEXISTENT_12345")


# ===================================================================
# RESOURCE HIERARCHY
# ===================================================================


class TestAsyncResourceHierarchyLive:
    """Live tests for resource hierarchy methods."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_resource_children(self, async_instance: AsyncOFSC):
        """Test get_resource_children."""
        result = await async_instance.core.get_resource_children("SUNRISE", limit=10)

        assert isinstance(result, ResourceListResponse)
        assert hasattr(result, "items")

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_resource_descendants(self, async_instance: AsyncOFSC):
        """Test get_resource_descendants."""
        result = await async_instance.core.get_resource_descendants("SUNRISE", limit=10)

        assert isinstance(result, ResourceListResponse)
        assert hasattr(result, "items")


# ===================================================================
# RESOURCE SUB-ENTITIES
# ===================================================================


class TestAsyncResourceSubEntitiesLive:
    """Live tests for resource sub-entity methods."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_resource_users(self, async_instance: AsyncOFSC):
        """Test get_resource_users."""
        result = await async_instance.core.get_resource_users("33001")

        assert isinstance(result, ResourceUsersListResponse)
        assert hasattr(result, "items")

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_resource_inventories(self, async_instance: AsyncOFSC):
        """Test get_resource_inventories."""
        result = await async_instance.core.get_resource_inventories("33001")

        assert isinstance(result, InventoryListResponse)
        assert hasattr(result, "items")

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_resource_workskills(self, async_instance: AsyncOFSC):
        """Test get_resource_workskills."""
        result = await async_instance.core.get_resource_workskills("33001")

        assert isinstance(result, ResourceWorkskillListResponse)
        assert hasattr(result, "items")

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_resource_workzones(self, async_instance: AsyncOFSC):
        """Test get_resource_workzones."""
        result = await async_instance.core.get_resource_workzones("33001")

        assert isinstance(result, ResourceWorkzoneListResponse)
        assert hasattr(result, "items")

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_resource_workschedules(self, async_instance: AsyncOFSC):
        """Test get_resource_workschedules."""
        result = await async_instance.core.get_resource_workschedules("33001", date.today())

        assert isinstance(result, ResourceWorkScheduleResponse)

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_resource_calendar(self, async_instance: AsyncOFSC):
        """Test get_resource_calendar."""
        from calendar import monthrange
        from datetime import date

        today = date.today()
        date_from = date(today.year, today.month, 1)
        last_day = monthrange(today.year, today.month)[1]
        date_to = date(today.year, today.month, last_day)

        result = await async_instance.core.get_resource_calendar("33001", date_from, date_to)

        assert isinstance(result, CalendarView)


# ===================================================================
# LOCATIONS
# ===================================================================


class TestAsyncResourceLocationsLive:
    """Live tests for resource location methods."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_resource_locations(self, async_instance: AsyncOFSC):
        """Test get_resource_locations."""
        result = await async_instance.core.get_resource_locations("33001")

        assert isinstance(result, LocationListResponse)
        assert hasattr(result, "items")

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_assigned_locations(self, async_instance: AsyncOFSC):
        """Test get_assigned_locations."""
        from calendar import monthrange
        from datetime import date

        today = date.today()
        date_from = date(today.year, today.month, 1)
        last_day = monthrange(today.year, today.month)[1]
        date_to = date(today.year, today.month, last_day)

        result = await async_instance.core.get_assigned_locations("33001", date_from, date_to)

        assert isinstance(result, AssignedLocationsResponse)

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_position_history(self, async_instance: AsyncOFSC):
        """Test get_position_history."""
        try:
            result = await async_instance.core.get_position_history("33001", date.today())
            assert isinstance(result, PositionHistoryResponse)
            assert hasattr(result, "items")
        except OFSCNotFoundError:
            pytest.skip("Position history not available for resource '33001' on today's date (route may not be activated)")


# ===================================================================
# ROUTES & PLANS
# ===================================================================


class TestAsyncResourceRoutesPlansLive:
    """Live tests for resource routes and plans."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_resource_route(self, async_instance: AsyncOFSC):
        """Test get_resource_route."""
        result = await async_instance.core.get_resource_route("33001", date.today())

        assert isinstance(result, ResourceRouteResponse)
        assert hasattr(result, "items")

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_resource_plans(self, async_instance: AsyncOFSC):
        """Test get_resource_plans with date range (uses bucket resource with plans feature)."""
        from calendar import monthrange

        today = date.today()
        # Use next month to avoid past-date errors
        if today.month == 12:
            next_month = date(today.year + 1, 1, 1)
        else:
            next_month = date(today.year, today.month + 1, 1)
        last_day = monthrange(next_month.year, next_month.month)[1]
        date_to = date(next_month.year, next_month.month, last_day)

        result = await async_instance.core.get_resource_plans("FLUSA", next_month, date_to)

        assert isinstance(result, ResourcePlansResponse)
        assert hasattr(result, "items")

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_resource_assistants(self, async_instance: AsyncOFSC):
        """Test get_resource_assistants with date range (max 14 days, future dates)."""
        today = date.today()
        # Use next month start + 6 days to avoid past-date errors and stay within 14-day limit
        if today.month == 12:
            date_from = date(today.year + 1, 1, 1)
        else:
            date_from = date(today.year, today.month + 1, 1)
        date_to = date(date_from.year, date_from.month, 7)

        result = await async_instance.core.get_resource_assistants("33001", date_from, date_to)

        assert isinstance(result, ResourceAssistantsResponse)
        assert hasattr(result, "items")

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_calendars(self, async_instance: AsyncOFSC):
        """Test get_calendars with resources list and date range (future dates)."""
        from calendar import monthrange

        today = date.today()
        # Use next month to avoid past-date errors
        if today.month == 12:
            date_from = date(today.year + 1, 1, 1)
        else:
            date_from = date(today.year, today.month + 1, 1)
        last_day = monthrange(date_from.year, date_from.month)[1]
        date_to = date(date_from.year, date_from.month, last_day)

        result = await async_instance.core.get_calendars(["33001"], date_from, date_to)

        assert isinstance(result, CalendarsListResponse)
        assert hasattr(result, "items")


# ===================================================================
# SAVED RESPONSE VALIDATION
# ===================================================================


@pytest.mark.uses_local_data
class TestAsyncResourceSavedResponses:
    """Test model validation against saved API responses."""

    def test_resources_list_response_validation(self):
        """Test ResourceListResponse validates against saved response."""
        saved_response_path = Path(__file__).parent.parent / "saved_responses" / "resources" / "get_resources_200_success.json"

        with open(saved_response_path) as f:
            saved_data = json.load(f)

        response = ResourceListResponse.model_validate(saved_data["response_data"])

        assert isinstance(response, ResourceListResponse)
        assert hasattr(response, "items")
        assert len(response.items) > 0
        assert all(isinstance(r, Resource) for r in response.items)

    def test_resource_individual_validation(self):
        """Test Resource model validates against individual resource."""
        saved_response_path = Path(__file__).parent.parent / "saved_responses" / "resources" / "get_resource_individual_200_success.json"

        with open(saved_response_path) as f:
            saved_data = json.load(f)

        resource = Resource.model_validate(saved_data["response_data"])

        assert isinstance(resource, Resource)
        assert resource.resourceId == "33001"

    def test_resource_bucket_validation(self):
        """Test Resource model validates against bucket resource."""
        saved_response_path = Path(__file__).parent.parent / "saved_responses" / "resources" / "get_resource_bucket_200_success.json"

        with open(saved_response_path) as f:
            saved_data = json.load(f)

        resource = Resource.model_validate(saved_data["response_data"])

        assert isinstance(resource, Resource)
        assert resource.resourceId == "FLUSA"

    def test_resource_workskills_validation(self):
        """Test ResourceWorkskillListResponse validates."""
        saved_response_path = Path(__file__).parent.parent / "saved_responses" / "resources" / "get_resource_workskills_200_success.json"

        with open(saved_response_path) as f:
            saved_data = json.load(f)

        response = ResourceWorkskillListResponse.model_validate(saved_data["response_data"])

        assert isinstance(response, ResourceWorkskillListResponse)
        assert hasattr(response, "items")

    def test_resource_route_validation(self):
        """Test ResourceRouteResponse validates."""
        saved_response_path = Path(__file__).parent.parent / "saved_responses" / "resources" / "get_resource_route_200_success.json"

        with open(saved_response_path) as f:
            saved_data = json.load(f)

        response = ResourceRouteResponse.model_validate(saved_data["response_data"])

        assert isinstance(response, ResourceRouteResponse)
        assert hasattr(response, "items")
        assert hasattr(response, "routeStartTime")

    def test_resource_assistants_validation(self):
        """Test ResourceAssistantsResponse validates against saved response."""
        saved_response_path = Path(__file__).parent.parent / "saved_responses" / "resources" / "get_resource_assistants_200_success.json"

        with open(saved_response_path) as f:
            saved_data = json.load(f)

        response = ResourceAssistantsResponse.model_validate(saved_data["response_data"])

        assert isinstance(response, ResourceAssistantsResponse)
        assert hasattr(response, "items")

    def test_resource_plans_validation(self):
        """Test ResourcePlansResponse validates against saved response."""
        saved_response_path = Path(__file__).parent.parent / "saved_responses" / "resources" / "get_resource_plans_200_success.json"

        with open(saved_response_path) as f:
            saved_data = json.load(f)

        response = ResourcePlansResponse.model_validate(saved_data["response_data"])

        assert isinstance(response, ResourcePlansResponse)
        assert hasattr(response, "items")

    def test_calendars_validation(self):
        """Test CalendarsListResponse validates against saved response."""
        saved_response_path = Path(__file__).parent.parent / "saved_responses" / "resources" / "get_calendars_200_success.json"

        with open(saved_response_path) as f:
            saved_data = json.load(f)

        response = CalendarsListResponse.model_validate(saved_data["response_data"])

        assert isinstance(response, CalendarsListResponse)


# ===================================================================
# GET ALL RESOURCES (ASYNC GENERATOR)
# ===================================================================


class TestAsyncGetAllResources:
    """Test async get_all_resources generator method."""

    def _make_resources_response(self, resource_ids: list[str], has_more: bool = False) -> dict:
        """Build a mock resource list response dict."""
        return {
            "totalResults": len(resource_ids),
            "hasMore": has_more,
            "items": [
                {
                    "resourceId": rid,
                    "name": f"Resource {rid}",
                    "resourceType": "technician",
                    "language": "en",
                    "timeZone": "UTC",
                }
                for rid in resource_ids
            ],
        }

    @pytest.mark.asyncio
    async def test_get_all_resources_returns_async_generator(self, mock_instance: AsyncOFSC):
        """Verify that get_all_resources returns an async generator."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self._make_resources_response(["R1", "R2"])
        mock_response.raise_for_status = Mock()

        mock_instance.core._client.get = AsyncMock(return_value=mock_response)

        result = mock_instance.core.get_all_resources()
        assert inspect.isasyncgen(result)

        # Exhaust the generator to avoid resource warning
        async for _ in result:
            pass

    @pytest.mark.asyncio
    async def test_get_all_resources_yields_resource_instances(self, mock_instance: AsyncOFSC):
        """Verify that each yielded item is a Resource instance."""
        from ofsc.models import Resource

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self._make_resources_response(["R1", "R2", "R3"])
        mock_response.raise_for_status = Mock()

        mock_instance.core._client.get = AsyncMock(return_value=mock_response)

        items = []
        async for item in mock_instance.core.get_all_resources():
            items.append(item)

        assert len(items) == 3
        for item in items:
            assert isinstance(item, Resource)
            assert hasattr(item, "resourceId")
            assert hasattr(item, "name")

    @pytest.mark.asyncio
    async def test_get_all_resources_fetches_all_pages(self, mock_instance: AsyncOFSC):
        """Verify that pagination works: multiple pages are fetched until hasMore is False."""
        page1_response = Mock()
        page1_response.status_code = 200
        page1_response.json.return_value = self._make_resources_response(["R1", "R2"], has_more=True)
        page1_response.raise_for_status = Mock()

        page2_response = Mock()
        page2_response.status_code = 200
        page2_response.json.return_value = self._make_resources_response(["R3", "R4"], has_more=False)
        page2_response.raise_for_status = Mock()

        mock_instance.core._client.get = AsyncMock(side_effect=[page1_response, page2_response])

        collected = []
        async for item in mock_instance.core.get_all_resources(limit=2):
            collected.append(item)

        assert len(collected) == 4
        resource_ids = [r.resourceId for r in collected]
        assert resource_ids == ["R1", "R2", "R3", "R4"]
        # Verify the API was called twice (two pages)
        assert mock_instance.core._client.get.call_count == 2

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_all_resources_matches_manual_pagination(self, async_instance: AsyncOFSC):
        """Verify get_all_resources yields same unique resources as manual get_resources pagination."""
        # Manual pagination
        manual_ids = set()
        offset = 0
        while True:
            page = await async_instance.core.get_resources(offset=offset, limit=10)
            for r in page.items:
                manual_ids.add(r.resourceId)
            if not page.hasMore:
                break
            offset += 10

        # Generator
        generator_ids = set()
        async for resource in async_instance.core.get_all_resources(limit=10):
            generator_ids.add(resource.resourceId)

        assert len(manual_ids) > 0, "No resources found in test environment"
        assert manual_ids == generator_ids

    @pytest.mark.asyncio
    async def test_get_all_resources_unique_resource_ids(self, mock_instance: AsyncOFSC):
        """Verify no duplicate resourceIds are yielded across pages."""
        page1_response = Mock()
        page1_response.status_code = 200
        page1_response.json.return_value = self._make_resources_response(["RA", "RB", "RC"], has_more=True)
        page1_response.raise_for_status = Mock()

        page2_response = Mock()
        page2_response.status_code = 200
        page2_response.json.return_value = self._make_resources_response(["RD", "RE"], has_more=False)
        page2_response.raise_for_status = Mock()

        mock_instance.core._client.get = AsyncMock(side_effect=[page1_response, page2_response])

        collected = []
        async for item in mock_instance.core.get_all_resources(limit=3):
            collected.append(item)

        resource_ids = [r.resourceId for r in collected]
        assert len(resource_ids) == len(set(resource_ids)), "Duplicate resourceIds found across pages"
        assert set(resource_ids) == {"RA", "RB", "RC", "RD", "RE"}
