"""Tests for async populate status endpoints (ME030G, ME057G)."""

from unittest.mock import AsyncMock, Mock

import pytest

from ofsc.async_client import AsyncOFSC
from ofsc.models import PopulateStatusResponse


# === GET POPULATE MAP LAYERS STATUS (ME030G) ===


class TestAsyncGetPopulateMapLayersStatus:
    """Model validation tests for get_populate_map_layers_status."""

    @pytest.mark.asyncio
    async def test_returns_correct_model(self, mock_instance: AsyncOFSC):
        """Test that get_populate_map_layers_status returns PopulateStatusResponse."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "completed",
            "time": "2024-01-15T10:30:00Z",
            "downloadId": 12345,
        }
        mock_response.raise_for_status = Mock()

        mock_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await mock_instance.metadata.get_populate_map_layers_status(12345)

        assert isinstance(result, PopulateStatusResponse)
        assert result.status == "completed"
        assert result.time == "2024-01-15T10:30:00Z"
        assert result.downloadId == 12345

    @pytest.mark.asyncio
    async def test_with_partial_fields(self, mock_instance: AsyncOFSC):
        """Test get_populate_map_layers_status with partial response (pending status)."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "pending",
            "downloadId": 99999,
        }
        mock_response.raise_for_status = Mock()

        mock_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await mock_instance.metadata.get_populate_map_layers_status(99999)

        assert isinstance(result, PopulateStatusResponse)
        assert result.status == "pending"
        assert result.time is None
        assert result.downloadId == 99999

    @pytest.mark.asyncio
    async def test_links_removed(self, mock_instance: AsyncOFSC):
        """Test that links field is removed from response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "completed",
            "downloadId": 1,
            "links": [{"rel": "self", "href": "http://example.com"}],
        }
        mock_response.raise_for_status = Mock()

        mock_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await mock_instance.metadata.get_populate_map_layers_status(1)

        assert isinstance(result, PopulateStatusResponse)
        assert not hasattr(result, "links")


# === GET POPULATE WORKZONE SHAPES STATUS (ME057G) ===


class TestAsyncGetPopulateWorkzoneShapesStatus:
    """Model validation tests for get_populate_workzone_shapes_status."""

    @pytest.mark.asyncio
    async def test_returns_correct_model(self, mock_instance: AsyncOFSC):
        """Test that get_populate_workzone_shapes_status returns PopulateStatusResponse."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "completed",
            "time": "2024-01-15T11:00:00Z",
            "downloadId": 67890,
        }
        mock_response.raise_for_status = Mock()

        mock_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await mock_instance.metadata.get_populate_workzone_shapes_status(67890)

        assert isinstance(result, PopulateStatusResponse)
        assert result.status == "completed"
        assert result.time == "2024-01-15T11:00:00Z"
        assert result.downloadId == 67890

    @pytest.mark.asyncio
    async def test_with_partial_fields(self, mock_instance: AsyncOFSC):
        """Test get_populate_workzone_shapes_status with partial response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "in_progress",
            "downloadId": 55555,
        }
        mock_response.raise_for_status = Mock()

        mock_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await mock_instance.metadata.get_populate_workzone_shapes_status(55555)

        assert isinstance(result, PopulateStatusResponse)
        assert result.status == "in_progress"
        assert result.time is None
        assert result.downloadId == 55555

    @pytest.mark.asyncio
    async def test_all_fields_optional(self, mock_instance: AsyncOFSC):
        """Test that all fields are optional (empty response)."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_response.raise_for_status = Mock()

        mock_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await mock_instance.metadata.get_populate_workzone_shapes_status(1)

        assert isinstance(result, PopulateStatusResponse)
        assert result.status is None
        assert result.time is None
        assert result.downloadId is None

    @pytest.mark.asyncio
    async def test_links_removed(self, mock_instance: AsyncOFSC):
        """Test that links field is removed from response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "completed",
            "downloadId": 1,
            "links": [{"rel": "self", "href": "http://example.com"}],
        }
        mock_response.raise_for_status = Mock()

        mock_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await mock_instance.metadata.get_populate_workzone_shapes_status(1)

        assert isinstance(result, PopulateStatusResponse)
        assert not hasattr(result, "links")
