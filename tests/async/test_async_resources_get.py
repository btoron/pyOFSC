"""Tests for async resource GET operations."""

import json
from datetime import date
from pathlib import Path

import pytest

from ofsc.async_client import AsyncOFSC
from ofsc.exceptions import OFSCNotFoundError
from ofsc.models import (
    AssignedLocationsResponse,
    CalendarView,
    InventoryListResponse,
    LocationListResponse,
    PositionHistoryResponse,
    Resource,
    ResourceListResponse,
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
        result = await async_instance.core.get_resources(
            limit=2, expand_inventories=True, expand_workskills=True
        )

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
        result = await async_instance.core.get_resource_workschedules(
            "33001", date.today()
        )

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

        result = await async_instance.core.get_resource_calendar(
            "33001", date_from, date_to
        )

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

        result = await async_instance.core.get_assigned_locations(
            "33001", date_from, date_to
        )

        assert isinstance(result, AssignedLocationsResponse)

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_position_history(self, async_instance: AsyncOFSC):
        """Test get_position_history."""
        result = await async_instance.core.get_position_history("33001", date.today())

        assert isinstance(result, PositionHistoryResponse)
        assert hasattr(result, "items")


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


# ===================================================================
# SAVED RESPONSE VALIDATION
# ===================================================================


class TestAsyncResourceSavedResponses:
    """Test model validation against saved API responses."""

    def test_resources_list_response_validation(self):
        """Test ResourceListResponse validates against saved response."""
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "resources"
            / "get_resources_200_success.json"
        )

        with open(saved_response_path) as f:
            saved_data = json.load(f)

        response = ResourceListResponse.model_validate(saved_data["response_data"])

        assert isinstance(response, ResourceListResponse)
        assert hasattr(response, "items")
        assert len(response.items) > 0
        assert all(isinstance(r, Resource) for r in response.items)

    def test_resource_individual_validation(self):
        """Test Resource model validates against individual resource."""
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "resources"
            / "get_resource_individual_200_success.json"
        )

        with open(saved_response_path) as f:
            saved_data = json.load(f)

        resource = Resource.model_validate(saved_data["response_data"])

        assert isinstance(resource, Resource)
        assert resource.resourceId == "33001"

    def test_resource_bucket_validation(self):
        """Test Resource model validates against bucket resource."""
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "resources"
            / "get_resource_bucket_200_success.json"
        )

        with open(saved_response_path) as f:
            saved_data = json.load(f)

        resource = Resource.model_validate(saved_data["response_data"])

        assert isinstance(resource, Resource)
        assert resource.resourceId == "FLUSA"

    def test_resource_workskills_validation(self):
        """Test ResourceWorkskillListResponse validates."""
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "resources"
            / "get_resource_workskills_200_success.json"
        )

        with open(saved_response_path) as f:
            saved_data = json.load(f)

        response = ResourceWorkskillListResponse.model_validate(
            saved_data["response_data"]
        )

        assert isinstance(response, ResourceWorkskillListResponse)
        assert hasattr(response, "items")

    def test_resource_route_validation(self):
        """Test ResourceRouteResponse validates."""
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "resources"
            / "get_resource_route_200_success.json"
        )

        with open(saved_response_path) as f:
            saved_data = json.load(f)

        response = ResourceRouteResponse.model_validate(saved_data["response_data"])

        assert isinstance(response, ResourceRouteResponse)
        assert hasattr(response, "items")
        assert hasattr(response, "routeStartTime")
