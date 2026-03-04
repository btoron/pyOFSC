"""Tests for async capacity areas metadata methods."""

import json
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

from ofsc.async_client import AsyncOFSC
from ofsc.exceptions import OFSCNotFoundError
from ofsc.models import (
    CapacityArea,
    CapacityAreaCapacityCategoriesResponse,
    CapacityAreaCapacityCategory,
    CapacityAreaChildrenResponse,
    CapacityAreaListResponse,
    CapacityAreaOrganization,
    CapacityAreaOrganizationsResponse,
    CapacityAreaTimeInterval,
    CapacityAreaTimeIntervalsResponse,
    CapacityAreaTimeSlot,
    CapacityAreaTimeSlotsResponse,
    CapacityAreaWorkZone,
    CapacityAreaWorkZonesResponse,
    CapacityAreaWorkZoneV1,
    CapacityAreaWorkZonesV1Response,
)


# === GET CAPACITY AREAS (LIST) ===


class TestAsyncGetCapacityAreasLive:
    """Live tests for get_capacity_areas against actual API."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_capacity_areas(self, async_instance: AsyncOFSC):
        """Test get_capacity_areas with actual API - validates structure."""
        result = await async_instance.metadata.get_capacity_areas()

        assert isinstance(result, CapacityAreaListResponse)
        assert hasattr(result, "items")
        assert len(result.items) > 0

        # Validate first item structure
        first_area = result.items[0]
        assert isinstance(first_area, CapacityArea)
        assert hasattr(first_area, "label")

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_capacity_areas_with_expand_parent(self, async_instance: AsyncOFSC):
        """Test get_capacity_areas with expandParent=True."""
        result = await async_instance.metadata.get_capacity_areas(expandParent=True)

        assert isinstance(result, CapacityAreaListResponse)
        assert len(result.items) > 0

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_capacity_areas_with_fields(self, async_instance: AsyncOFSC):
        """Test get_capacity_areas with custom fields."""
        result = await async_instance.metadata.get_capacity_areas(fields=["label", "name", "status"])

        assert isinstance(result, CapacityAreaListResponse)
        assert len(result.items) > 0

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_capacity_areas_active_only(self, async_instance: AsyncOFSC):
        """Test get_capacity_areas with activeOnly=True."""
        result = await async_instance.metadata.get_capacity_areas(activeOnly=True)

        assert isinstance(result, CapacityAreaListResponse)

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_capacity_areas_areas_only(self, async_instance: AsyncOFSC):
        """Test get_capacity_areas with areasOnly=True."""
        result = await async_instance.metadata.get_capacity_areas(areasOnly=True)

        assert isinstance(result, CapacityAreaListResponse)

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_all_capacity_areas_individually(self, async_instance: AsyncOFSC):
        """Test getting all capacity areas individually to validate all configurations.

        This test:
        1. Retrieves all capacity areas
        2. Iterates through each one
        3. Retrieves each area individually by label
        4. Validates that all models parse correctly

        This ensures the models can handle all real-world configuration variations.
        """
        # First get all capacity areas
        all_areas = await async_instance.metadata.get_capacity_areas()

        assert isinstance(all_areas, CapacityAreaListResponse)
        assert len(all_areas.items) > 0

        # Track results for reporting
        successful = 0
        failed = []

        # Iterate through each area and get it individually
        for area in all_areas.items:
            try:
                individual_area = await async_instance.metadata.get_capacity_area(area.label)

                # Validate the returned area
                assert isinstance(individual_area, CapacityArea)
                assert individual_area.label == area.label

                successful += 1
            except Exception as e:
                failed.append({"label": area.label, "error": str(e)})

        # Report results
        print("\nCapacity Areas validation:")
        print(f"  Total areas: {len(all_areas.items)}")
        print(f"  Successful: {successful}")
        print(f"  Failed: {len(failed)}")

        if failed:
            print("\nFailed areas:")
            for failure in failed:
                print(f"  - {failure['label']}: {failure['error']}")

        # All areas should be retrieved successfully
        assert len(failed) == 0, f"Failed to retrieve {len(failed)} areas: {failed}"
        assert successful == len(all_areas.items)


class TestAsyncGetCapacityAreas:
    """Model validation tests for get_capacity_areas."""

    @pytest.mark.asyncio
    async def test_get_capacity_areas_with_model(self, mock_instance: AsyncOFSC):
        """Test that get_capacity_areas returns CapacityAreaListResponse model."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {"label": "AREA1"},
                {"label": "AREA2"},
            ],
            "links": [],
        }

        mock_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await mock_instance.metadata.get_capacity_areas()

        assert isinstance(result, CapacityAreaListResponse)
        assert len(result.items) == 2
        assert result.items[0].label == "AREA1"
        assert result.items[1].label == "AREA2"

    @pytest.mark.asyncio
    async def test_get_capacity_areas_field_types(self, mock_instance: AsyncOFSC):
        """Test that fields have correct types."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [{"label": "TEST_AREA"}],
        }

        mock_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await mock_instance.metadata.get_capacity_areas()

        assert isinstance(result.items[0].label, str)


# === GET CAPACITY AREA (SINGLE) ===


class TestAsyncGetCapacityAreaLive:
    """Live tests for get_capacity_area against actual API."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_capacity_area(self, async_instance: AsyncOFSC):
        """Test get_capacity_area with actual API."""
        # First get all areas to find a valid label
        areas = await async_instance.metadata.get_capacity_areas()
        assert len(areas.items) > 0

        # Get the first area by label
        test_label = areas.items[0].label
        result = await async_instance.metadata.get_capacity_area(test_label)

        assert isinstance(result, CapacityArea)
        assert result.label == test_label

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_capacity_area_not_found(self, async_instance: AsyncOFSC):
        """Test get_capacity_area with non-existent label."""
        with pytest.raises(OFSCNotFoundError):
            await async_instance.metadata.get_capacity_area("NONEXISTENT_AREA_12345")


class TestAsyncGetCapacityArea:
    """Model validation tests for get_capacity_area."""

    @pytest.mark.asyncio
    async def test_get_capacity_area_with_model(self, mock_instance: AsyncOFSC):
        """Test that get_capacity_area returns CapacityArea model."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "label": "TEST_AREA",
            "name": "Test Area",
            "status": "active",
        }

        mock_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await mock_instance.metadata.get_capacity_area("TEST_AREA")

        assert isinstance(result, CapacityArea)
        assert result.label == "TEST_AREA"
        assert result.name == "Test Area"


# === SAVED RESPONSE VALIDATION ===


@pytest.mark.uses_local_data
class TestAsyncCapacityAreasSavedResponses:
    """Test that saved API responses validate against Pydantic models."""

    def test_capacity_area_list_response_validation(self):
        """Test CapacityAreaListResponse model validates against saved response."""
        saved_response_path = Path(__file__).parent.parent / "saved_responses" / "capacity_areas" / "get_capacity_areas_200_success.json"
        with open(saved_response_path) as f:
            saved_data = json.load(f)

        response = CapacityAreaListResponse.model_validate(saved_data["response_data"])

        assert isinstance(response, CapacityAreaListResponse)
        assert len(response.items) >= 5  # At least 5 areas in test data
        assert all(isinstance(area, CapacityArea) for area in response.items)

    def test_capacity_area_expanded_validation(self):
        """Test CapacityAreaListResponse with expanded parent validates."""
        saved_response_path = Path(__file__).parent.parent / "saved_responses" / "capacity_areas" / "get_capacity_areas_expanded_200_success.json"
        with open(saved_response_path) as f:
            saved_data = json.load(f)

        response = CapacityAreaListResponse.model_validate(saved_data["response_data"])

        assert isinstance(response, CapacityAreaListResponse)
        assert len(response.items) >= 5

    def test_capacity_area_single_validation(self):
        """Test CapacityArea model validates against saved single response."""
        saved_response_path = Path(__file__).parent.parent / "saved_responses" / "capacity_areas" / "get_capacity_area_200_success.json"
        with open(saved_response_path) as f:
            saved_data = json.load(f)

        area = CapacityArea.model_validate(saved_data["response_data"])

        assert isinstance(area, CapacityArea)
        assert area.label == "FLUSA"


# === GET CAPACITY AREA CAPACITY CATEGORIES (ME012G) ===


class TestAsyncGetCapacityAreaCapacityCategoriesLive:
    """Live tests for get_capacity_area_capacity_categories against actual API."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_capacity_area_capacity_categories(self, async_instance: AsyncOFSC):
        """Test get_capacity_area_capacity_categories with actual API."""
        areas = await async_instance.metadata.get_capacity_areas()
        assert len(areas.items) > 0
        test_label = areas.items[0].label

        result = await async_instance.metadata.get_capacity_area_capacity_categories(test_label)

        assert isinstance(result, CapacityAreaCapacityCategoriesResponse)
        assert hasattr(result, "items")

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_capacity_area_capacity_categories_not_found(self, async_instance: AsyncOFSC):
        """Test get_capacity_area_capacity_categories with non-existent label."""
        from ofsc.exceptions import OFSCNotFoundError

        with pytest.raises(OFSCNotFoundError):
            await async_instance.metadata.get_capacity_area_capacity_categories("NONEXISTENT_AREA_12345")


class TestAsyncGetCapacityAreaCapacityCategories:
    """Model validation tests for get_capacity_area_capacity_categories."""

    @pytest.mark.asyncio
    async def test_returns_correct_model(self, mock_instance: AsyncOFSC):
        """Test that get_capacity_area_capacity_categories returns correct model."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {"label": "CAT1", "name": "Category 1", "status": "active"},
                {"label": "CAT2", "name": "Category 2", "status": "inactive"},
            ]
        }
        mock_response.raise_for_status = Mock()

        mock_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await mock_instance.metadata.get_capacity_area_capacity_categories("AREA1")

        assert isinstance(result, CapacityAreaCapacityCategoriesResponse)
        assert len(result.items) == 2
        assert isinstance(result.items[0], CapacityAreaCapacityCategory)
        assert result.items[0].label == "CAT1"
        assert result.items[0].status == "active"

    @pytest.mark.asyncio
    async def test_empty_items(self, mock_instance: AsyncOFSC):
        """Test get_capacity_area_capacity_categories with empty items."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": []}
        mock_response.raise_for_status = Mock()

        mock_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await mock_instance.metadata.get_capacity_area_capacity_categories("AREA1")

        assert isinstance(result, CapacityAreaCapacityCategoriesResponse)
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_iterable(self, mock_instance: AsyncOFSC):
        """Test that result is iterable."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": [{"label": "CAT1"}, {"label": "CAT2"}]}
        mock_response.raise_for_status = Mock()

        mock_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await mock_instance.metadata.get_capacity_area_capacity_categories("AREA1")

        labels = [cat.label for cat in result]
        assert labels == ["CAT1", "CAT2"]


# === GET CAPACITY AREA WORKZONES v2 (ME013G) ===


class TestAsyncGetCapacityAreaWorkzonesLive:
    """Live tests for get_capacity_area_workzones against actual API."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_capacity_area_workzones(self, async_instance: AsyncOFSC):
        """Test get_capacity_area_workzones with actual API."""
        areas = await async_instance.metadata.get_capacity_areas()
        assert len(areas.items) > 0
        test_label = areas.items[0].label

        result = await async_instance.metadata.get_capacity_area_workzones(test_label)

        assert isinstance(result, CapacityAreaWorkZonesResponse)
        assert hasattr(result, "items")

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_capacity_area_workzones_not_found(self, async_instance: AsyncOFSC):
        """Test get_capacity_area_workzones with non-existent label."""
        with pytest.raises(OFSCNotFoundError):
            await async_instance.metadata.get_capacity_area_workzones("NONEXISTENT_AREA_12345")


class TestAsyncGetCapacityAreaWorkzones:
    """Model validation tests for get_capacity_area_workzones."""

    @pytest.mark.asyncio
    async def test_returns_correct_model(self, mock_instance: AsyncOFSC):
        """Test that get_capacity_area_workzones returns CapacityAreaWorkZonesResponse."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {"workZoneLabel": "WZ1", "workZoneName": "Workzone 1"},
                {"workZoneLabel": "WZ2", "workZoneName": "Workzone 2"},
            ]
        }
        mock_response.raise_for_status = Mock()

        mock_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await mock_instance.metadata.get_capacity_area_workzones("AREA1")

        assert isinstance(result, CapacityAreaWorkZonesResponse)
        assert len(result.items) == 2
        assert isinstance(result.items[0], CapacityAreaWorkZone)
        assert result.items[0].workZoneLabel == "WZ1"

    @pytest.mark.asyncio
    async def test_empty_items(self, mock_instance: AsyncOFSC):
        """Test get_capacity_area_workzones with empty items."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": []}
        mock_response.raise_for_status = Mock()

        mock_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await mock_instance.metadata.get_capacity_area_workzones("AREA1")

        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_iterable(self, mock_instance: AsyncOFSC):
        """Test that result is iterable."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": [{"workZoneLabel": "WZ1"}, {"workZoneLabel": "WZ2"}]}
        mock_response.raise_for_status = Mock()

        mock_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await mock_instance.metadata.get_capacity_area_workzones("AREA1")

        labels = [wz.workZoneLabel for wz in result]
        assert labels == ["WZ1", "WZ2"]


# === GET CAPACITY AREA WORKZONES v1 (ME014G) ===


class TestAsyncGetCapacityAreaWorkzonesV1:
    """Model validation tests for get_capacity_area_workzones_v1."""

    @pytest.mark.asyncio
    async def test_returns_correct_model(self, mock_instance: AsyncOFSC):
        """Test that get_capacity_area_workzones_v1 returns CapacityAreaWorkZonesV1Response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": [{"label": "WZ1"}, {"label": "WZ2"}]}
        mock_response.raise_for_status = Mock()

        mock_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await mock_instance.metadata.get_capacity_area_workzones_v1("AREA1")

        assert isinstance(result, CapacityAreaWorkZonesV1Response)
        assert len(result.items) == 2
        assert isinstance(result.items[0], CapacityAreaWorkZoneV1)
        assert result.items[0].label == "WZ1"

    @pytest.mark.asyncio
    async def test_empty_items(self, mock_instance: AsyncOFSC):
        """Test get_capacity_area_workzones_v1 with empty items."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": []}
        mock_response.raise_for_status = Mock()

        mock_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await mock_instance.metadata.get_capacity_area_workzones_v1("AREA1")

        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_iterable(self, mock_instance: AsyncOFSC):
        """Test that result is iterable."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": [{"label": "WZ1"}]}
        mock_response.raise_for_status = Mock()

        mock_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await mock_instance.metadata.get_capacity_area_workzones_v1("AREA1")

        assert list(result)[0].label == "WZ1"


# === GET CAPACITY AREA TIME SLOTS (ME015G) ===


class TestAsyncGetCapacityAreaTimeSlotsLive:
    """Live tests for get_capacity_area_time_slots against actual API."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_capacity_area_time_slots(self, async_instance: AsyncOFSC):
        """Test get_capacity_area_time_slots with actual API."""
        areas = await async_instance.metadata.get_capacity_areas()
        assert len(areas.items) > 0
        test_label = areas.items[0].label

        result = await async_instance.metadata.get_capacity_area_time_slots(test_label)

        assert isinstance(result, CapacityAreaTimeSlotsResponse)
        assert hasattr(result, "items")

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_capacity_area_time_slots_not_found(self, async_instance: AsyncOFSC):
        """Test get_capacity_area_time_slots with non-existent label."""
        with pytest.raises(OFSCNotFoundError):
            await async_instance.metadata.get_capacity_area_time_slots("NONEXISTENT_AREA_12345")


class TestAsyncGetCapacityAreaTimeSlots:
    """Model validation tests for get_capacity_area_time_slots."""

    @pytest.mark.asyncio
    async def test_returns_correct_model(self, mock_instance: AsyncOFSC):
        """Test that get_capacity_area_time_slots returns CapacityAreaTimeSlotsResponse."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "label": "TS1",
                    "name": "Morning",
                    "timeFrom": "08:00",
                    "timeTo": "12:00",
                },
                {
                    "label": "TS2",
                    "name": "Afternoon",
                    "timeFrom": "13:00",
                    "timeTo": "17:00",
                },
            ]
        }
        mock_response.raise_for_status = Mock()

        mock_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await mock_instance.metadata.get_capacity_area_time_slots("AREA1")

        assert isinstance(result, CapacityAreaTimeSlotsResponse)
        assert len(result.items) == 2
        assert isinstance(result.items[0], CapacityAreaTimeSlot)
        assert result.items[0].label == "TS1"
        assert result.items[0].timeFrom == "08:00"

    @pytest.mark.asyncio
    async def test_empty_items(self, mock_instance: AsyncOFSC):
        """Test get_capacity_area_time_slots with empty items."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": []}
        mock_response.raise_for_status = Mock()

        mock_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await mock_instance.metadata.get_capacity_area_time_slots("AREA1")

        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_iterable(self, mock_instance: AsyncOFSC):
        """Test that result is iterable."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": [{"label": "TS1"}, {"label": "TS2"}]}
        mock_response.raise_for_status = Mock()

        mock_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await mock_instance.metadata.get_capacity_area_time_slots("AREA1")

        labels = [ts.label for ts in result]
        assert labels == ["TS1", "TS2"]


# === GET CAPACITY AREA TIME INTERVALS (ME016G) ===


class TestAsyncGetCapacityAreaTimeIntervalsLive:
    """Live tests for get_capacity_area_time_intervals against actual API."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_capacity_area_time_intervals(self, async_instance: AsyncOFSC):
        """Test get_capacity_area_time_intervals with actual API."""
        areas = await async_instance.metadata.get_capacity_areas()
        assert len(areas.items) > 0
        test_label = areas.items[0].label

        result = await async_instance.metadata.get_capacity_area_time_intervals(test_label)

        assert isinstance(result, CapacityAreaTimeIntervalsResponse)
        assert hasattr(result, "items")

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_capacity_area_time_intervals_not_found(self, async_instance: AsyncOFSC):
        """Test get_capacity_area_time_intervals with non-existent label."""
        with pytest.raises(OFSCNotFoundError):
            await async_instance.metadata.get_capacity_area_time_intervals("NONEXISTENT_AREA_12345")


class TestAsyncGetCapacityAreaTimeIntervals:
    """Model validation tests for get_capacity_area_time_intervals."""

    @pytest.mark.asyncio
    async def test_returns_correct_model(self, mock_instance: AsyncOFSC):
        """Test that get_capacity_area_time_intervals returns correct model."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {"timeFrom": "08:00", "timeTo": "12:00"},
                {"timeFrom": "13:00", "timeTo": "17:00"},
            ]
        }
        mock_response.raise_for_status = Mock()

        mock_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await mock_instance.metadata.get_capacity_area_time_intervals("AREA1")

        assert isinstance(result, CapacityAreaTimeIntervalsResponse)
        assert len(result.items) == 2
        assert isinstance(result.items[0], CapacityAreaTimeInterval)
        assert result.items[0].timeFrom == "08:00"

    @pytest.mark.asyncio
    async def test_empty_items(self, mock_instance: AsyncOFSC):
        """Test get_capacity_area_time_intervals with empty items."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": []}
        mock_response.raise_for_status = Mock()

        mock_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await mock_instance.metadata.get_capacity_area_time_intervals("AREA1")

        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_iterable(self, mock_instance: AsyncOFSC):
        """Test that result is iterable."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": [{"timeFrom": "08:00", "timeTo": "12:00"}]}
        mock_response.raise_for_status = Mock()

        mock_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await mock_instance.metadata.get_capacity_area_time_intervals("AREA1")

        intervals = list(result)
        assert intervals[0].timeFrom == "08:00"


# === GET CAPACITY AREA ORGANIZATIONS (ME017G) ===


class TestAsyncGetCapacityAreaOrganizationsLive:
    """Live tests for get_capacity_area_organizations against actual API."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_capacity_area_organizations(self, async_instance: AsyncOFSC):
        """Test get_capacity_area_organizations with actual API."""
        areas = await async_instance.metadata.get_capacity_areas()
        assert len(areas.items) > 0
        test_label = areas.items[0].label

        result = await async_instance.metadata.get_capacity_area_organizations(test_label)

        assert isinstance(result, CapacityAreaOrganizationsResponse)
        assert hasattr(result, "items")

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_capacity_area_organizations_not_found(self, async_instance: AsyncOFSC):
        """Test get_capacity_area_organizations with non-existent label."""
        with pytest.raises(OFSCNotFoundError):
            await async_instance.metadata.get_capacity_area_organizations("NONEXISTENT_AREA_12345")


class TestAsyncGetCapacityAreaOrganizations:
    """Model validation tests for get_capacity_area_organizations."""

    @pytest.mark.asyncio
    async def test_returns_correct_model(self, mock_instance: AsyncOFSC):
        """Test that get_capacity_area_organizations returns correct model."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {"label": "ORG1", "name": "Organization 1", "type": "inhouse"},
                {"label": "ORG2", "name": "Organization 2", "type": "contractor"},
            ]
        }
        mock_response.raise_for_status = Mock()

        mock_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await mock_instance.metadata.get_capacity_area_organizations("AREA1")

        assert isinstance(result, CapacityAreaOrganizationsResponse)
        assert len(result.items) == 2
        assert isinstance(result.items[0], CapacityAreaOrganization)
        assert result.items[0].label == "ORG1"
        assert result.items[0].type == "inhouse"

    @pytest.mark.asyncio
    async def test_empty_items(self, mock_instance: AsyncOFSC):
        """Test get_capacity_area_organizations with empty items."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": []}
        mock_response.raise_for_status = Mock()

        mock_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await mock_instance.metadata.get_capacity_area_organizations("AREA1")

        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_iterable(self, mock_instance: AsyncOFSC):
        """Test that result is iterable."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": [{"label": "ORG1"}, {"label": "ORG2"}]}
        mock_response.raise_for_status = Mock()

        mock_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await mock_instance.metadata.get_capacity_area_organizations("AREA1")

        labels = [org.label for org in result]
        assert labels == ["ORG1", "ORG2"]


# === GET CAPACITY AREA CHILDREN (ME018G) ===


class TestAsyncGetCapacityAreaChildrenLive:
    """Live tests for get_capacity_area_children against actual API."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_capacity_area_children(self, async_instance: AsyncOFSC):
        """Test get_capacity_area_children with actual API."""
        areas = await async_instance.metadata.get_capacity_areas()
        assert len(areas.items) > 0
        test_label = areas.items[0].label

        result = await async_instance.metadata.get_capacity_area_children(test_label)

        assert isinstance(result, CapacityAreaChildrenResponse)
        assert hasattr(result, "items")

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_capacity_area_children_not_found(self, async_instance: AsyncOFSC):
        """Test get_capacity_area_children with non-existent label."""
        with pytest.raises(OFSCNotFoundError):
            await async_instance.metadata.get_capacity_area_children("NONEXISTENT_AREA_12345")


class TestAsyncGetCapacityAreaChildren:
    """Model validation tests for get_capacity_area_children."""

    @pytest.mark.asyncio
    async def test_returns_correct_model(self, mock_instance: AsyncOFSC):
        """Test that get_capacity_area_children returns CapacityAreaChildrenResponse."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {"label": "CHILD1", "name": "Child Area 1", "type": "area"},
                {"label": "CHILD2", "name": "Child Area 2", "type": "area"},
            ]
        }
        mock_response.raise_for_status = Mock()

        mock_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await mock_instance.metadata.get_capacity_area_children("AREA1")

        assert isinstance(result, CapacityAreaChildrenResponse)
        assert len(result.items) == 2
        assert isinstance(result.items[0], CapacityArea)
        assert result.items[0].label == "CHILD1"

    @pytest.mark.asyncio
    async def test_with_query_params(self, mock_instance: AsyncOFSC):
        """Test get_capacity_area_children with query parameters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": [{"label": "CHILD1", "status": "active"}]}
        mock_response.raise_for_status = Mock()

        mock_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await mock_instance.metadata.get_capacity_area_children("AREA1", status="active", type="area")

        assert isinstance(result, CapacityAreaChildrenResponse)
        assert len(result.items) == 1

    @pytest.mark.asyncio
    async def test_empty_items(self, mock_instance: AsyncOFSC):
        """Test get_capacity_area_children with empty items."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": []}
        mock_response.raise_for_status = Mock()

        mock_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await mock_instance.metadata.get_capacity_area_children("AREA1")

        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_iterable(self, mock_instance: AsyncOFSC):
        """Test that result is iterable."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": [{"label": "CHILD1"}, {"label": "CHILD2"}]}
        mock_response.raise_for_status = Mock()

        mock_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await mock_instance.metadata.get_capacity_area_children("AREA1")

        labels = [child.label for child in result]
        assert labels == ["CHILD1", "CHILD2"]


# === CROSS-API: CAPACITY AREA WORKZONES vs RESOURCE WORKZONES ===


class TestAsyncCapacityAreaVsResourceWorkzones:
    """Cross-API validation: compare workzones from metadata and core APIs."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_capacity_area_workzones_match_resource_workzones(self, async_instance: AsyncOFSC):
        """Validate that get_capacity_area_workzones and get_resource_workzones
        return the same workzone labels when queried with the same label.
        """
        # Get a valid capacity area label
        areas = await async_instance.metadata.get_capacity_areas()
        assert len(areas.items) > 0
        label = areas.items[0].label

        # Get workzones from metadata API (ME013G v2)
        ca_workzones = await async_instance.metadata.get_capacity_area_workzones(label)
        ca_labels = {wz.workZoneLabel for wz in ca_workzones}

        # Get workzones from core API (same label as resource_id)
        res_workzones = await async_instance.core.get_resource_workzones(label)
        res_labels = {wz.workZone for wz in res_workzones if wz.workZone}

        # The workzone labels from both APIs should match
        assert ca_labels == res_labels, f"Workzone mismatch for '{label}': metadata={ca_labels - res_labels}, core={res_labels - ca_labels}"
