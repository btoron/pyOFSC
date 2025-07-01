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
from ofsc.models.metadata import (
    ActivityTypeGroup,
    Property,
    PropertyListResponse,
    TimeSlotListResponse,
    WorkskillListResponse,
)
from ofsc.models.base import Translation, TranslationList
from ofsc.models.capacity import (
    CapacityAreaTimeIntervalListResponse,
    CapacityAreaTimeSlotListResponse,
    CapacityAreaWorkzoneListResponse,
    CapacityAreaCategoryListResponse,
    CapacityAreaOrganizationListResponse,
    CapacityCategoryRequest,
    CapacityCategoryResponse,
)


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
                        "href": "https://demo.fs.ocs.oraclecloud.com/rest/ofscMetadata/v1/metadata-catalog/timeSlots",
                    }
                ],
            },
            {
                "label": "all-day",
                "name": "All-Day",
                "active": True,
                "isAllDay": True,
                "links": [
                    {
                        "rel": "describedby",
                        "href": "https://demo.fs.ocs.oraclecloud.com/rest/ofscMetadata/v1/metadata-catalog/timeSlots",
                    }
                ],
            },
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


@pytest.fixture
def mock_capacity_area_categories_response():
    """Mock capacity area categories API response."""
    return {
        "items": [
            {
                "label": "EST",
                "name": "Estimation"
            }
        ],
        "totalResults": 1,
        "limit": 100,
        "offset": 0,
        "hasMore": False,
    }


@pytest.fixture
def mock_capacity_area_workzones_v2_response():
    """Mock capacity area work zones v2 API response."""
    return {
        "items": [
            {
                "workZoneLabel": "ALTAMONTE_SPRINGS",
                "workZoneName": "ALTAMONTE SPRINGS"
            }
        ],
        "totalResults": 1,
        "limit": 100,
        "offset": 0,
        "hasMore": False,
    }


@pytest.fixture
def mock_capacity_area_timeslots_response():
    """Mock capacity area time slots API response."""
    return {
        "items": [
            {
                "label": "08-10",
                "name": "08-10",
                "timeFrom": "08:00:00",
                "timeTo": "10:00:00"
            }
        ],
        "totalResults": 1,
        "limit": 100,
        "offset": 0,
        "hasMore": False,
    }


@pytest.fixture
def mock_capacity_area_timeintervals_response():
    """Mock capacity area time intervals API response."""
    return {
        "items": [
            {
                "timeFrom": "00",
                "timeTo": "08"
            },
            {
                "timeFrom": "08"
            }
        ],
        "totalResults": 2,
        "limit": 100,
        "offset": 0,
        "hasMore": False,
    }


@pytest.fixture
def mock_capacity_area_organizations_response():
    """Mock capacity area organizations API response."""
    return {
        "items": [
            {
                "label": "default",
                "name": "Supremo Fitness Organization",
                "type": "inhouse"
            }
        ],
        "totalResults": 1,
        "limit": 100,
        "offset": 0,
        "hasMore": False,
    }


@pytest.mark.asyncio
class TestCapacityAreaSubResourcesAPI:
    """Test Capacity Area Sub-Resource API endpoints (16-21)."""

    @respx.mock
    async def test_get_capacity_area_categories(self, mock_capacity_area_categories_response):
        """Test get_capacity_area_categories endpoint."""
        route = respx.get(
            "https://demo.fs.ocs.oraclecloud.com/rest/ofscMetadata/v1/capacityAreas/FLUSA/capacityCategories"
        )
        route.mock(return_value=Response(200, json=mock_capacity_area_categories_response))

        async with OFSC(
            instance="demo", client_id="test_id", client_secret="test_secret"
        ) as client:
            result = await client.metadata.get_capacity_area_categories("FLUSA")
            assert isinstance(result, CapacityAreaCategoryListResponse)
            assert result.totalResults == 1
            assert len(result.items) == 1
            assert result.items[0].label == "EST"
            assert result.items[0].name == "Estimation"

    @respx.mock
    async def test_get_capacity_area_workzones(self, mock_capacity_area_workzones_v2_response):
        """Test get_capacity_area_workzones endpoint."""
        route = respx.get(
            "https://demo.fs.ocs.oraclecloud.com/rest/ofscMetadata/v2/capacityAreas/FLUSA/workZones"
        )
        route.mock(return_value=Response(200, json=mock_capacity_area_workzones_v2_response))

        async with OFSC(
            instance="demo", client_id="test_id", client_secret="test_secret"
        ) as client:
            result = await client.metadata.get_capacity_area_workzones("FLUSA")
            assert isinstance(result, CapacityAreaWorkzoneListResponse)
            assert result.totalResults == 1
            assert len(result.items) == 1
            assert result.items[0].workZoneLabel == "ALTAMONTE_SPRINGS"
            assert result.items[0].workZoneName == "ALTAMONTE SPRINGS"

    @respx.mock
    async def test_get_capacity_area_timeslots(self, mock_capacity_area_timeslots_response):
        """Test get_capacity_area_timeslots endpoint."""
        route = respx.get(
            "https://demo.fs.ocs.oraclecloud.com/rest/ofscMetadata/v1/capacityAreas/FLUSA/timeSlots"
        )
        route.mock(return_value=Response(200, json=mock_capacity_area_timeslots_response))

        async with OFSC(
            instance="demo", client_id="test_id", client_secret="test_secret"
        ) as client:
            result = await client.metadata.get_capacity_area_timeslots("FLUSA")
            assert isinstance(result, CapacityAreaTimeSlotListResponse)
            assert result.totalResults == 1
            assert len(result.items) == 1
            assert result.items[0].label == "08-10"
            assert result.items[0].name == "08-10"
            assert result.items[0].timeFrom == "08:00:00"
            assert result.items[0].timeTo == "10:00:00"

    @respx.mock
    async def test_get_capacity_area_timeintervals(self, mock_capacity_area_timeintervals_response):
        """Test get_capacity_area_timeintervals endpoint."""
        route = respx.get(
            "https://demo.fs.ocs.oraclecloud.com/rest/ofscMetadata/v1/capacityAreas/FLUSA/timeIntervals"
        )
        route.mock(return_value=Response(200, json=mock_capacity_area_timeintervals_response))

        async with OFSC(
            instance="demo", client_id="test_id", client_secret="test_secret"
        ) as client:
            result = await client.metadata.get_capacity_area_timeintervals("FLUSA")
            assert isinstance(result, CapacityAreaTimeIntervalListResponse)
            assert result.totalResults == 2
            assert len(result.items) == 2
            assert result.items[0].timeFrom == "00"
            assert result.items[0].timeTo == "08"
            assert result.items[1].timeFrom == "08"
            assert result.items[1].timeTo is None  # Some intervals only have timeFrom

    @respx.mock
    async def test_get_capacity_area_organizations(self, mock_capacity_area_organizations_response):
        """Test get_capacity_area_organizations endpoint."""
        route = respx.get(
            "https://demo.fs.ocs.oraclecloud.com/rest/ofscMetadata/v1/capacityAreas/FLUSA/organizations"
        )
        route.mock(return_value=Response(200, json=mock_capacity_area_organizations_response))

        async with OFSC(
            instance="demo", client_id="test_id", client_secret="test_secret"
        ) as client:
            result = await client.metadata.get_capacity_area_organizations("FLUSA")
            assert isinstance(result, CapacityAreaOrganizationListResponse)
            assert result.totalResults == 1
            assert len(result.items) == 1
            assert result.items[0].label == "default"
            assert result.items[0].name == "Supremo Fitness Organization"
            assert result.items[0].type == "inhouse"

    @respx.mock
    async def test_capacity_area_label_validation(self):
        """Test label validation for capacity area sub-resource methods."""
        async with OFSC(
            instance="demo", client_id="test_id", client_secret="test_secret"
        ) as client:
            # Test empty label for all methods
            with pytest.raises(OFSValidationException):
                await client.metadata.get_capacity_area_categories("")
            
            with pytest.raises(OFSValidationException):
                await client.metadata.get_capacity_area_workzones("")
            
            with pytest.raises(OFSValidationException):
                await client.metadata.get_capacity_area_timeslots("")
            
            with pytest.raises(OFSValidationException):
                await client.metadata.get_capacity_area_timeintervals("")
            
            with pytest.raises(OFSValidationException):
                await client.metadata.get_capacity_area_organizations("")

    @respx.mock
    async def test_capacity_area_pagination_validation(self):
        """Test pagination parameter validation for capacity area sub-resource methods."""
        async with OFSC(
            instance="demo", client_id="test_id", client_secret="test_secret"
        ) as client:
            # Test invalid pagination for one method (they all use same validation)
            with pytest.raises(OFSValidationException):
                await client.metadata.get_capacity_area_categories("FLUSA", offset=-1)
            
            with pytest.raises(OFSValidationException):
                await client.metadata.get_capacity_area_categories("FLUSA", limit=0)
            
            with pytest.raises(OFSValidationException):
                await client.metadata.get_capacity_area_categories("FLUSA", limit=1001)


@pytest.fixture
def mock_activity_type_group_response():
    """Mock activity type group API response."""
    return {
        "label": "test_group",
        "name": "Test Activity Type Group",
        "activityTypes": [
            {"label": "activity_1"},
            {"label": "activity_2"}
        ],
        "translations": [
            {
                "language": "en",
                "name": "Test Activity Type Group",
                "languageISO": "en-US"
            }
        ],
        "links": [
            {
                "rel": "canonical",
                "href": "https://demo.fs.ocs.oraclecloud.com/rest/ofscMetadata/v1/activityTypeGroups/test_group"
            }
        ]
    }


@pytest.mark.asyncio
class TestActivityTypeGroupAPI:
    """Test Activity Type Group API endpoints including create/replace."""

    @respx.mock
    async def test_create_or_replace_activity_type_group_success(self, mock_activity_type_group_response):
        """Test successful creation/replacement of activity type group with translations."""
        route = respx.put(
            "https://demo.fs.ocs.oraclecloud.com/rest/ofscMetadata/v1/activityTypeGroups/test_group"
        )
        route.mock(return_value=Response(200, json=mock_activity_type_group_response))

        async with OFSC(
            instance="demo", client_id="test_id", client_secret="test_secret"
        ) as client:
            # Create translations
            translations = TranslationList([
                Translation(language="en", name="Test Activity Type Group", languageISO="en-US"),
                Translation(language="es", name="Grupo de Tipos de Actividad", languageISO="es-ES")
            ])
            
            result = await client.metadata.create_or_replace_activity_type_group("test_group", translations)
            
            assert isinstance(result, ActivityTypeGroup)
            assert result.label == "test_group"
            assert result.name == "Test Activity Type Group"

    @respx.mock
    async def test_create_or_replace_activity_type_group_minimal(self, mock_activity_type_group_response):
        """Test creation with no translations (empty request)."""
        route = respx.put(
            "https://demo.fs.ocs.oraclecloud.com/rest/ofscMetadata/v1/activityTypeGroups/minimal_group"
        )
        # Update mock response for minimal case
        minimal_response = {
            "label": "minimal_group",
            "name": "Minimal Group",
            "activityTypes": [],
            "links": [
                {
                    "rel": "canonical",
                    "href": "https://demo.fs.ocs.oraclecloud.com/rest/ofscMetadata/v1/activityTypeGroups/minimal_group"
                }
            ]
        }
        route.mock(return_value=Response(200, json=minimal_response))

        async with OFSC(
            instance="demo", client_id="test_id", client_secret="test_secret"
        ) as client:
            # Call with no translations (None)
            result = await client.metadata.create_or_replace_activity_type_group("minimal_group", None)
            
            assert isinstance(result, ActivityTypeGroup)
            assert result.label == "minimal_group"
            assert result.name == "Minimal Group"

    @respx.mock
    async def test_create_or_replace_activity_type_group_request_body(self):
        """Test that request body is properly serialized."""
        route = respx.put(
            "https://demo.fs.ocs.oraclecloud.com/rest/ofscMetadata/v1/activityTypeGroups/request_test"
        )
        route.mock(return_value=Response(200, json={"label": "request_test", "name": "Test"}))

        async with OFSC(
            instance="demo", client_id="test_id", client_secret="test_secret"
        ) as client:
            translations = TranslationList([
                Translation(language="en", name="Request Test Group", languageISO="en-US")
            ])
            
            await client.metadata.create_or_replace_activity_type_group("request_test", translations)
            
            # Verify the request was made with correct JSON body
            assert len(route.calls) == 1
            request_call = route.calls[0]
            assert request_call.request.method == "PUT"
            
            # Check request body contains expected fields
            request_json = request_call.request.content.decode('utf-8')
            assert '"translations"' in request_json
            assert '"language":"en"' in request_json
            assert '"name":"Request Test Group"' in request_json

    async def test_create_or_replace_activity_type_group_label_validation(self):
        """Test label parameter validation."""
        async with OFSC(
            instance="demo", client_id="test_id", client_secret="test_secret"
        ) as client:
            # Test empty label
            with pytest.raises(OFSValidationException):
                await client.metadata.create_or_replace_activity_type_group("", None)

    async def test_create_or_replace_activity_type_group_empty_translations(self):
        """Test with empty translations list."""
        async with OFSC(
            instance="demo", client_id="test_id", client_secret="test_secret"
        ) as client:
            # Empty translations list should work (sends empty request body)
            empty_translations = TranslationList([])
            # This should not raise an exception
            try:
                await client.metadata.create_or_replace_activity_type_group("test", empty_translations)
            except Exception as e:
                # Should only fail on network/API issues, not validation
                assert "validation" not in str(e).lower()

    @respx.mock
    async def test_create_or_replace_activity_type_group_http_error(self):
        """Test handling of HTTP errors."""
        route = respx.put(
            "https://demo.fs.ocs.oraclecloud.com/rest/ofscMetadata/v1/activityTypeGroups/error_test"
        )
        route.mock(return_value=Response(400, json={"error": "Bad Request"}))

        async with OFSC(
            instance="demo", client_id="test_id", client_secret="test_secret"
        ) as client:
            # The client should raise an appropriate exception for HTTP errors
            with pytest.raises(Exception):  # Should raise OFS exception for HTTP errors
                await client.metadata.create_or_replace_activity_type_group("error_test", None)


@pytest.fixture
def mock_capacity_category_response():
    """Mock capacity category API response."""
    return {
        "label": "TEST_CAT",
        "name": "Test Category",
        "active": True,
        "timeSlots": [],
        "workSkills": [],
        "workSkillGroups": [],
        "translations": [
            {
                "language": "en",
                "name": "Test Category",
                "languageISO": "en-US"
            }
        ],
        "links": [
            {
                "rel": "canonical",
                "href": "https://demo.fs.ocs.oraclecloud.com/rest/ofscMetadata/v1/capacityCategories/TEST_CAT"
            }
        ]
    }


@pytest.fixture
def mock_capacity_category_request():
    """Mock capacity category request data."""
    return CapacityCategoryRequest(
        label="TEST_CAT",
        name="Test Category",
        active=True,
        timeSlots=[],
        workSkills=[],
        workSkillGroups=[]
    )


@pytest.mark.asyncio
class TestCapacityCategoryAPI:
    """Test Capacity Category API endpoints including create/replace and delete."""

    @respx.mock
    async def test_create_or_replace_capacity_category_success(self, mock_capacity_category_response, mock_capacity_category_request):
        """Test successful creation/replacement of capacity category."""
        route = respx.put(
            "https://demo.fs.ocs.oraclecloud.com/rest/ofscMetadata/v1/capacityCategories/TEST_CAT"
        )
        route.mock(return_value=Response(200, json=mock_capacity_category_response))

        async with OFSC(
            instance="demo", client_id="test_id", client_secret="test_secret"
        ) as client:
            result = await client.metadata.create_or_replace_capacity_category("TEST_CAT", mock_capacity_category_request)
            
            assert isinstance(result, CapacityCategoryResponse)
            assert result.label == "TEST_CAT"
            assert result.name == "Test Category"
            assert result.active is True

    @respx.mock
    async def test_create_or_replace_capacity_category_request_body(self, mock_capacity_category_request):
        """Test that request body is properly serialized."""
        route = respx.put(
            "https://demo.fs.ocs.oraclecloud.com/rest/ofscMetadata/v1/capacityCategories/BODY_TEST"
        )
        route.mock(return_value=Response(200, json={"label": "BODY_TEST", "name": "Test", "active": True}))

        async with OFSC(
            instance="demo", client_id="test_id", client_secret="test_secret"
        ) as client:
            await client.metadata.create_or_replace_capacity_category("BODY_TEST", mock_capacity_category_request)
            
            # Verify the request was made with correct JSON body
            assert len(route.calls) == 1
            request_call = route.calls[0]
            assert request_call.request.method == "PUT"
            
            # Check request body contains expected fields
            request_json = request_call.request.content.decode('utf-8')
            assert '"label":"TEST_CAT"' in request_json
            assert '"name":"Test Category"' in request_json
            assert '"active":true' in request_json

    async def test_create_or_replace_capacity_category_label_validation(self):
        """Test label parameter validation."""
        async with OFSC(
            instance="demo", client_id="test_id", client_secret="test_secret"
        ) as client:
            mock_request = CapacityCategoryRequest(
                label="TEST",
                name="Test",
                active=True
            )
            
            # Test empty label
            with pytest.raises(OFSValidationException):
                await client.metadata.create_or_replace_capacity_category("", mock_request)

    @respx.mock
    async def test_create_or_replace_capacity_category_http_error(self):
        """Test handling of HTTP errors."""
        route = respx.put(
            "https://demo.fs.ocs.oraclecloud.com/rest/ofscMetadata/v1/capacityCategories/ERROR_TEST"
        )
        route.mock(return_value=Response(400, json={"error": "Bad Request"}))

        async with OFSC(
            instance="demo", client_id="test_id", client_secret="test_secret"
        ) as client:
            mock_request = CapacityCategoryRequest(
                label="ERROR_TEST",
                name="Error Test",
                active=True
            )
            
            # The client should raise an appropriate exception for HTTP errors
            with pytest.raises(Exception):  # Should raise OFS exception for HTTP errors
                await client.metadata.create_or_replace_capacity_category("ERROR_TEST", mock_request)

    @respx.mock
    async def test_delete_capacity_category_success(self):
        """Test successful deletion of capacity category."""
        route = respx.delete(
            "https://demo.fs.ocs.oraclecloud.com/rest/ofscMetadata/v1/capacityCategories/DELETE_TEST"
        )
        route.mock(return_value=Response(204))  # HTTP 204 No Content for successful deletion

        async with OFSC(
            instance="demo", client_id="test_id", client_secret="test_secret"
        ) as client:
            # Should not raise any exception
            await client.metadata.delete_capacity_category("DELETE_TEST")
            
            # Verify the request was made
            assert len(route.calls) == 1
            request_call = route.calls[0]
            assert request_call.request.method == "DELETE"

    async def test_delete_capacity_category_label_validation(self):
        """Test label parameter validation for delete."""
        async with OFSC(
            instance="demo", client_id="test_id", client_secret="test_secret"
        ) as client:
            # Test empty label
            with pytest.raises(OFSValidationException):
                await client.metadata.delete_capacity_category("")

    @respx.mock
    async def test_delete_capacity_category_http_error(self):
        """Test handling of HTTP errors for delete."""
        route = respx.delete(
            "https://demo.fs.ocs.oraclecloud.com/rest/ofscMetadata/v1/capacityCategories/NOT_FOUND"
        )
        route.mock(return_value=Response(404, json={"error": "Not Found"}))

        async with OFSC(
            instance="demo", client_id="test_id", client_secret="test_secret"
        ) as client:
            # The client should raise an appropriate exception for HTTP errors
            with pytest.raises(Exception):  # Should raise OFS exception for HTTP errors
                await client.metadata.delete_capacity_category("NOT_FOUND")

    @respx.mock
    async def test_create_or_replace_capacity_category_with_optional_fields(self):
        """Test creation with all optional fields."""
        full_response = {
            "label": "FULL_TEST",
            "name": "Full Test Category",
            "active": True,
            "timeSlots": [{"label": "08-10", "name": "08-10"}],
            "workSkills": [{"label": "EST", "name": "Estimation"}],
            "workSkillGroups": [{"label": "TECH", "name": "Technical"}],
            "translations": [
                {
                    "language": "en",
                    "name": "Full Test Category",
                    "languageISO": "en-US"
                },
                {
                    "language": "es", 
                    "name": "Categoría de Prueba Completa",
                    "languageISO": "es-ES"
                }
            ]
        }
        
        route = respx.put(
            "https://demo.fs.ocs.oraclecloud.com/rest/ofscMetadata/v1/capacityCategories/FULL_TEST"
        )
        route.mock(return_value=Response(200, json=full_response))

        async with OFSC(
            instance="demo", client_id="test_id", client_secret="test_secret"
        ) as client:
            full_request = CapacityCategoryRequest(
                label="FULL_TEST",
                name="Full Test Category",
                active=True,
                timeSlots=[{"label": "08-10", "name": "08-10"}],
                workSkills=[{"label": "EST", "name": "Estimation"}],
                workSkillGroups=[{"label": "TECH", "name": "Technical"}],
                translations=TranslationList([
                    Translation(language="en", name="Full Test Category", languageISO="en-US"),
                    Translation(language="es", name="Categoría de Prueba Completa", languageISO="es-ES")
                ])
            )
            
            result = await client.metadata.create_or_replace_capacity_category("FULL_TEST", full_request)
            
            assert isinstance(result, CapacityCategoryResponse)
            assert result.label == "FULL_TEST"
            assert result.name == "Full Test Category"
            assert result.active is True
            assert result.timeSlots is not None
            assert result.workSkills is not None
            assert result.workSkillGroups is not None
            assert result.translations is not None
