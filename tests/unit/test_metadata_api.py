"""Unit tests for Metadata API v3.0 implementation.

Tests the new metadata API implementation with:
- Parameter validation
- Response model integration
- Both sync and async client support
- Error handling
"""

import pytest
import respx
from httpx import Response

from ofsc.client import OFSC
from ofsc.exceptions import OFSValidationException
from ofsc.models.metadata import Property, PropertyListResponse, TimeSlot, TimeSlotListResponse, Workskill, WorkskillListResponse


@pytest.fixture
def mock_property_response():
    """Mock property API response."""
    return {
        "items": [
            {
                "label": "test_property",
                "name": "Test Property",
                "type": "string",
                "entity": "activity",
                "sharing": "private",
            }
        ],
        "totalResults": 1,
        "limit": 50,
        "offset": 0,
        "hasMore": False,
    }


@pytest.fixture
def mock_workskill_response():
    """Mock workskill API response."""
    return {
        "items": [
            {
                "label": "test_skill",
                "name": "Test Skill",
                "active": True,
                "sharing": "private",
            }
        ],
        "totalResults": 1,
        "limit": 100,
        "offset": 0,
        "hasMore": False,
    }


@pytest.fixture
def mock_timeslots_response():
    """Mock timeslots API response."""
    return {
        "items": [
            {
                "label": "08-10",
                "name": "08-10",
                "active": True,
                "isAllDay": False,
                "timeStart": "08:00",
                "timeEnd": "10:00",
                "links": [
                    {
                        "rel": "describedby",
                        "href": "https://demo.fs.ocs.oraclecloud.com/rest/ofscMetadata/v1/metadata-catalog/timeSlots"
                    }
                ]
            },
            {
                "label": "all-day",
                "name": "All-Day",
                "active": True,
                "isAllDay": True,
                "links": [
                    {
                        "rel": "describedby",
                        "href": "https://demo.fs.ocs.oraclecloud.com/rest/ofscMetadata/v1/metadata-catalog/timeSlots"
                    }
                ]
            }
        ],
        "totalResults": 2,
        "limit": 100,
        "offset": 0,
        "hasMore": False,
    }


@pytest.fixture
def mock_single_property_response():
    """Mock single property API response."""
    return {
        "label": "test_property",
        "name": "Test Property",
        "type": "string",
        "entity": "activity",
        "sharing": "private",
    }


@pytest.mark.asyncio
class TestMetadataAPIAsyncClient:
    """Test Metadata API with async-only client."""

    @respx.mock
    async def test_get_properties_success(self, mock_property_response):
        """Test get_properties with valid parameters."""
        route = respx.get(
            "https://demo.fs.ocs.oraclecloud.com/rest/ofscMetadata/v1/properties"
        )
        route.mock(return_value=Response(200, json=mock_property_response))

        async with OFSC(
            instance="demo", client_id="test_id", client_secret="test_secret"
        ) as client:
            result = await client.metadata.get_properties(offset=0, limit=50)
            assert isinstance(result, PropertyListResponse)
            assert result.totalResults == 1
            assert len(result.items) == 1
            assert result.items[0].label == "test_property"

    @respx.mock
    async def test_get_properties_parameter_validation(self):
        """Test parameter validation for get_properties."""
        async with OFSC(
            instance="demo", client_id="test_id", client_secret="test_secret"
        ) as client:
            # Test invalid offset
            with pytest.raises(OFSValidationException):
                await client.metadata.get_properties(offset=-1)

            # Test invalid limit
            with pytest.raises(OFSValidationException):
                await client.metadata.get_properties(limit=0)

            # Test limit too high
            with pytest.raises(OFSValidationException):
                await client.metadata.get_properties(limit=1001)

    @respx.mock
    async def test_get_property_by_label(self, mock_single_property_response):
        """Test get_property with valid label."""
        route = respx.get(
            "https://demo.fs.ocs.oraclecloud.com/rest/ofscMetadata/v1/properties/test_prop"
        )
        route.mock(return_value=Response(200, json=mock_single_property_response))

        async with OFSC(
            instance="demo", client_id="test_id", client_secret="test_secret"
        ) as client:
            result = await client.metadata.get_property("test_prop")
            assert isinstance(result, Property)
            assert result.label == "test_property"

    @respx.mock
    async def test_get_property_label_validation(self):
        """Test label validation for get_property."""
        async with OFSC(
            instance="demo", client_id="test_id", client_secret="test_secret"
        ) as client:
            # Test empty label
            with pytest.raises(OFSValidationException):
                await client.metadata.get_property("")

    @respx.mock
    async def test_get_workskills(self, mock_workskill_response):
        """Test get_workskills endpoint."""
        route = respx.get(
            "https://demo.fs.ocs.oraclecloud.com/rest/ofscMetadata/v1/workSkills"
        )
        route.mock(return_value=Response(200, json=mock_workskill_response))

        async with OFSC(
            instance="demo", client_id="test_id", client_secret="test_secret"
        ) as client:
            result = await client.metadata.get_workskills()
            assert isinstance(result, WorkskillListResponse)
            assert result.totalResults == 1
            assert len(result.items) == 1
            assert result.items[0].label == "test_skill"

    @respx.mock
    async def test_get_timeslots(self, mock_timeslots_response):
        """Test get_timeslots endpoint."""
        route = respx.get(
            "https://demo.fs.ocs.oraclecloud.com/rest/ofscMetadata/v1/timeSlots"
        )
        route.mock(return_value=Response(200, json=mock_timeslots_response))

        async with OFSC(
            instance="demo", client_id="test_id", client_secret="test_secret"
        ) as client:
            result = await client.metadata.get_timeslots()
            assert isinstance(result, TimeSlotListResponse)
            assert result.totalResults == 2
            assert len(result.items) == 2
            
            # Test regular timeslot
            regular_slot = result.items[0]
            assert regular_slot.label == "08-10"
            assert regular_slot.name == "08-10"
            assert regular_slot.active is True
            assert regular_slot.isAllDay is False
            assert regular_slot.timeStart == "08:00"
            assert regular_slot.timeEnd == "10:00"
            assert regular_slot.links is not None and len(regular_slot.links) == 1
            
            # Test all-day timeslot
            all_day_slot = result.items[1]
            assert all_day_slot.label == "all-day"
            assert all_day_slot.name == "All-Day"
            assert all_day_slot.active is True
            assert all_day_slot.isAllDay is True
            assert all_day_slot.timeStart is None
            assert all_day_slot.timeEnd is None
            assert all_day_slot.links is not None and len(all_day_slot.links) == 1

    @respx.mock
    async def test_get_timeslots_pagination(self, mock_timeslots_response):
        """Test get_timeslots with pagination parameters."""
        route = respx.get(
            "https://demo.fs.ocs.oraclecloud.com/rest/ofscMetadata/v1/timeSlots"
        )
        route.mock(return_value=Response(200, json=mock_timeslots_response))

        async with OFSC(
            instance="demo", client_id="test_id", client_secret="test_secret"
        ) as client:
            result = await client.metadata.get_timeslots(offset=10, limit=50)
            assert isinstance(result, TimeSlotListResponse)
            
            # Verify the request was made with correct parameters
            request = route.calls[0].request
            assert "offset=10" in str(request.url)
            assert "limit=50" in str(request.url)


