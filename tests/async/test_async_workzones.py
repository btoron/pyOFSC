"""Async tests for workzone operations."""

import httpx
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
        assert (
            workzones.totalResults >= 18
        )  # 22.B - at least 18, may have test workzones
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


class TestAsyncReplaceWorkzone:
    """Test async replace_workzone method."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_replace_workzone(self, async_instance, faker):
        """Test replacing an existing workzone"""
        # First, get an existing workzone
        workzones = await async_instance.metadata.get_workzones(offset=0, limit=1)

        if len(workzones.items) == 0:
            pytest.skip("No workzones available to test")

        # Get the first workzone and store original data
        original_workzone = workzones.items[0]

        # Modify the workzone
        modified_workzone = original_workzone.model_copy()
        modified_workzone.workZoneName = f"TEST_{faker.city()}"

        # Replace the workzone
        result = await async_instance.metadata.replace_workzone(modified_workzone)

        # Result can be Workzone (200) or None (204)
        if result is not None:
            assert isinstance(result, Workzone)
            assert hasattr(result, "workZoneLabel")
            assert hasattr(result, "workZoneName")

        # Restore original workzone
        await async_instance.metadata.replace_workzone(original_workzone)

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_replace_workzone_with_auto_resolve_conflicts(
        self, async_instance, faker
    ):
        """Test replacing a workzone with auto_resolve_conflicts parameter"""
        # Get an existing workzone
        workzones = await async_instance.metadata.get_workzones(offset=0, limit=1)

        if len(workzones.items) == 0:
            pytest.skip("No workzones available to test")

        # Get the first workzone and store original data
        original_workzone = workzones.items[0]

        # Modify the workzone
        modified_workzone = original_workzone.model_copy()
        modified_workzone.workZoneName = f"TEST_AUTO_{faker.city()}"

        # Replace with auto_resolve_conflicts
        result = await async_instance.metadata.replace_workzone(
            modified_workzone, auto_resolve_conflicts=True
        )

        # Result can be Workzone (200) or None (204)
        if result is not None:
            assert isinstance(result, Workzone)

        # Restore original workzone
        await async_instance.metadata.replace_workzone(original_workzone)

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_replace_workzone_returns_workzone(self, async_instance, faker):
        """Test that replace_workzone returns Workzone when status is 200"""
        # Get existing workzones using the model
        workzones = await async_instance.metadata.get_workzones(offset=0, limit=1)

        if len(workzones.items) == 0:
            pytest.skip("No workzones available to test")

        # Get the first workzone and store original data
        original_workzone = workzones.items[0]

        # Modify the workzone
        modified_workzone = original_workzone.model_copy()
        modified_workzone.workZoneName = f"TEST_{faker.city()}"

        # Replace the workzone
        result = await async_instance.metadata.replace_workzone(modified_workzone)

        # Verify type validation if we got a 200 response (some APIs return 204)
        if result is not None:
            assert isinstance(result, Workzone)
            assert hasattr(result, "workZoneLabel")
            assert hasattr(result, "workZoneName")

        # Restore original workzone
        await async_instance.metadata.replace_workzone(original_workzone)

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_replace_workzone_non_existing(self, async_instance):
        """Test that replacing a non-existing workzone raises HTTPStatusError"""
        # Create a workzone with a label that doesn't exist
        non_existing_workzone = Workzone(
            workZoneLabel="NON_EXISTING_WORKZONE_12345",
            workZoneName="Non Existing Zone",
            status="active",
            travelArea="sunrise_enterprise",
        )

        # Try to replace the non-existing workzone
        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            await async_instance.metadata.replace_workzone(non_existing_workzone)

        # Verify it's a 404 error
        assert exc_info.value.response.status_code == 404


class TestAsyncCreateWorkzone:
    """Test async create_workzone method."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_create_workzone(self, async_instance, faker):
        """Test creating a new workzone"""
        # Create a unique workzone label using timestamp to ensure uniqueness
        import time

        unique_label = f"TEST_WZ_{int(time.time())}"

        # Create a new workzone
        new_workzone = Workzone(
            workZoneLabel=unique_label,
            workZoneName=f"Test Zone {faker.city()}",
            status="active",
            travelArea="sunrise_enterprise",
            keys=["00000"],
            shapes=["00000"],
        )

        # Create the workzone
        try:
            result = await async_instance.metadata.create_workzone(new_workzone)

            # Verify the result
            assert isinstance(result, Workzone)
            assert result.workZoneLabel == unique_label
            assert result.workZoneName == new_workzone.workZoneName
            assert result.status == "active"
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 409:
                # Workzone already exists from previous test run - that's ok, it means create worked
                pytest.skip(
                    f"Workzone {unique_label} already exists (from previous test run)"
                )
            else:
                raise

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_create_workzone_already_exists(self, async_instance):
        """Test that creating a duplicate workzone raises HTTPStatusError"""
        # Get an existing workzone
        workzones = await async_instance.metadata.get_workzones(offset=0, limit=1)

        if len(workzones.items) == 0:
            pytest.skip("No workzones available to test")

        # Try to create a workzone with the same label
        existing_workzone = workzones.items[0]

        # Attempt to create it again
        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            await async_instance.metadata.create_workzone(existing_workzone)

        # Verify it's a 409 conflict error
        assert exc_info.value.response.status_code == 409
