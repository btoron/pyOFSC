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
from ofsc.models.metadata import Property, Workskill


@pytest.fixture
def mock_property_response():
    """Mock property API response."""
    return {
        "label": "test_property",
        "name": "Test Property",
        "type": "string",
        "entity": "activity",
        "sharing": "private",
    }


@pytest.fixture
def mock_workskill_response():
    """Mock workskill API response."""
    return {
        "label": "test_skill",
        "name": "Test Skill",
        "active": True,
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
            assert isinstance(result, Property)
            assert result.label == "test_property"

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
    async def test_get_property_by_label(self, mock_property_response):
        """Test get_property with valid label."""
        route = respx.get(
            "https://demo.fs.ocs.oraclecloud.com/rest/ofscMetadata/v1/properties/test_prop"
        )
        route.mock(return_value=Response(200, json=mock_property_response))

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
            assert isinstance(result, Workskill)
            assert result.label == "test_skill"


