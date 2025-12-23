"""Async tests for workzone operations."""

import pytest

from ofsc.models import Workzone, WorkzoneListResponse


class TestAsyncGetWorkzonesLive:
    """Live tests against actual API (similar to sync version)."""

    @pytest.mark.asyncio
    async def test_get_workzones(self, async_instance):
        """Test get_workzones with actual API - validates known data"""
        workzones = await async_instance.metadata.get_workzones(offset=0, limit=1000)

        # Verify type validation
        assert isinstance(workzones, WorkzoneListResponse)
        assert workzones.totalResults is not None
        assert workzones.totalResults == 18  # 22.B - known test data
        assert workzones.items[0].workZoneLabel == "ALTAMONTE_SPRINGS"
        assert workzones.items[1].workZoneName == "CASSELBERRY"


class TestAsyncGetWorkzones:
    """Test async get_workzones method."""

    @pytest.mark.asyncio
    async def test_get_workzones_with_model(self, async_instance):
        """Test that get_workzones returns WorkzoneListResponse model"""
        workzones = await async_instance.metadata.get_workzones(offset=0, limit=100)

        # Verify type validation
        assert isinstance(workzones, WorkzoneListResponse)
        assert hasattr(workzones, "items")
        assert hasattr(workzones, "totalResults")
        assert isinstance(workzones.items, list)

        # Verify items are Workzone instances
        if len(workzones.items) > 0:
            assert isinstance(workzones.items[0], Workzone)
            assert hasattr(workzones.items[0], "workZoneLabel")
            assert hasattr(workzones.items[0], "workZoneName")

    @pytest.mark.asyncio
    async def test_get_workzones_pagination(self, async_instance):
        """Test get_workzones with pagination"""
        # Get first page
        page1 = await async_instance.metadata.get_workzones(offset=0, limit=5)
        assert isinstance(page1, WorkzoneListResponse)
        assert len(page1.items) <= 5

        # Get second page if there are enough workzones
        if page1.totalResults > 5:
            page2 = await async_instance.metadata.get_workzones(offset=5, limit=5)
            assert isinstance(page2, WorkzoneListResponse)
            # Pages should have different items
            if len(page1.items) > 0 and len(page2.items) > 0:
                assert page1.items[0].workZoneLabel != page2.items[0].workZoneLabel

    @pytest.mark.asyncio
    async def test_get_workzones_total_results(self, async_instance):
        """Test that totalResults is populated"""
        workzones = await async_instance.metadata.get_workzones(offset=0, limit=100)
        assert workzones.totalResults is not None
        assert isinstance(workzones.totalResults, int)
        assert workzones.totalResults >= 0


class TestAsyncGetWorkzone:
    """Test async get_workzone method."""

    @pytest.mark.asyncio
    async def test_get_workzone(self, async_instance):
        """Test getting a single workzone by label"""
        # First get a list of workzones to get a valid label
        workzones = await async_instance.metadata.get_workzones(offset=0, limit=1)

        if len(workzones.items) == 0:
            pytest.skip("No workzones available to test")

        # Get the label of the first workzone
        label = workzones.items[0].workZoneLabel

        # Get the specific workzone
        workzone = await async_instance.metadata.get_workzone(label)

        # Verify type validation
        assert isinstance(workzone, Workzone)
        assert workzone.workZoneLabel == label
        assert hasattr(workzone, "workZoneName")
        assert hasattr(workzone, "status")
        assert hasattr(workzone, "travelArea")

    @pytest.mark.asyncio
    async def test_get_workzone_details(self, async_instance):
        """Test that get_workzone returns complete workzone details"""
        # Get a known workzone
        workzones = await async_instance.metadata.get_workzones(offset=0, limit=1)

        if len(workzones.items) == 0:
            pytest.skip("No workzones available to test")

        label = workzones.items[0].workZoneLabel

        # Get detailed workzone
        workzone = await async_instance.metadata.get_workzone(label)

        # Verify all expected fields are present
        assert isinstance(workzone, Workzone)
        assert workzone.workZoneLabel == label
        assert workzone.workZoneName is not None
        assert workzone.status in ["active", "inactive"]
        assert workzone.travelArea is not None
