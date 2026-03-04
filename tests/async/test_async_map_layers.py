"""Tests for async map layers metadata methods."""

import json
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

from ofsc.async_client import AsyncOFSC
from ofsc.exceptions import OFSCNotFoundError
from ofsc.models import MapLayer, MapLayerListResponse


# === GET MAP LAYERS (LIST) ===


class TestAsyncGetMapLayersLive:
    """Live tests for get_map_layers against actual API."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_map_layers(self, async_instance: AsyncOFSC):
        """Test get_map_layers with actual API - validates structure."""
        result = await async_instance.metadata.get_map_layers()

        assert isinstance(result, MapLayerListResponse)
        assert hasattr(result, "items")
        assert result.totalResults >= 0

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_map_layers_pagination(self, async_instance: AsyncOFSC):
        """Test get_map_layers with pagination."""
        result = await async_instance.metadata.get_map_layers(offset=0, limit=2)

        assert isinstance(result, MapLayerListResponse)
        assert len(result.items) <= 2


class TestAsyncGetMapLayersModel:
    """Model validation tests for get_map_layers."""

    @pytest.mark.asyncio
    async def test_get_map_layers_returns_model(self, mock_instance: AsyncOFSC):
        """Test that get_map_layers returns MapLayerListResponse model."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "label": "LAYER1",
                    "status": "active",
                    "text": "Map Layer 1",
                    "shapeTitleColumn": "title",
                    "tableColumns": ["col1", "col2"],
                },
                {
                    "label": "LAYER2",
                    "status": "inactive",
                    "text": "Map Layer 2",
                },
            ],
            "totalResults": 2,
            "links": [],
        }

        mock_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await mock_instance.metadata.get_map_layers()

        assert isinstance(result, MapLayerListResponse)
        assert len(result.items) == 2
        assert result.items[0].label == "LAYER1"
        assert result.items[1].label == "LAYER2"

    @pytest.mark.asyncio
    async def test_get_map_layers_field_types(self, mock_instance: AsyncOFSC):
        """Test that fields have correct types."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "label": "TEST_LAYER",
                    "status": "active",
                    "text": "Test Layer",
                }
            ],
            "totalResults": 1,
        }

        mock_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await mock_instance.metadata.get_map_layers()

        assert isinstance(result.items[0].label, str)
        assert result.items[0].status.value == "active"


# === GET MAP LAYER (SINGLE) ===


class TestAsyncGetMapLayerLive:
    """Live tests for get_map_layer against actual API."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_map_layer_not_found(self, async_instance: AsyncOFSC):
        """Test get_map_layer with non-existent label."""
        with pytest.raises(OFSCNotFoundError):
            await async_instance.metadata.get_map_layer("NONEXISTENT_LAYER_12345")


class TestAsyncGetMapLayerModel:
    """Model validation tests for get_map_layer."""

    @pytest.mark.asyncio
    async def test_get_map_layer_returns_model(self, mock_instance: AsyncOFSC):
        """Test that get_map_layer returns MapLayer model."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "label": "TEST_LAYER",
            "status": "active",
            "text": "Test Layer",
            "shapeTitleColumn": "title",
            "tableColumns": ["col1", "col2"],
            "shapeHintColumns": [
                {
                    "defaultName": "Field 1",
                    "sourceColumn": "source1",
                    "pluginFormField": "field1",
                }
            ],
            "shapeHintButton": {"actionType": "plugin", "label": "View"},
        }

        mock_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await mock_instance.metadata.get_map_layer("TEST_LAYER")

        assert isinstance(result, MapLayer)
        assert result.label == "TEST_LAYER"
        assert result.status.value == "active"
        assert result.text == "Test Layer"


# === SAVED RESPONSE VALIDATION ===


@pytest.mark.uses_local_data
class TestAsyncMapLayersSavedResponses:
    """Test that saved API responses validate against Pydantic models."""

    def test_map_layer_list_response_validation(self):
        """Test MapLayerListResponse model validates against saved response."""
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "map_layers"
            / "get_map_layers_200_success.json"
        )
        with open(saved_response_path) as f:
            saved_data = json.load(f)

        response = MapLayerListResponse.model_validate(saved_data["response_data"])

        assert isinstance(response, MapLayerListResponse)
        assert isinstance(response.totalResults, int)
        assert len(response.items) == response.totalResults

    def test_map_layer_single_validation(self):
        """Test MapLayer model validates against saved single response."""
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "map_layers"
            / "get_map_layer_200_success.json"
        )
        with open(saved_response_path) as f:
            saved_data = json.load(f)

        layer = MapLayer.model_validate(saved_data["response_data"])

        assert isinstance(layer, MapLayer)
        assert layer.label == "CUSTOM_LAYER_1"
        assert layer.status.value == "active"
        assert layer.text == "Custom Map Layer 1"
        assert layer.shapeTitleColumn == "title"
        assert len(layer.tableColumns) == 3
        assert len(layer.shapeHintColumns) == 2
        assert layer.shapeHintButton.actionType.value == "plugin"
