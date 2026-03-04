"""Tests for async metadata write operations (issue #138)."""

from unittest.mock import AsyncMock, Mock

import pytest

from ofsc.async_client import AsyncOFSC
from ofsc.exceptions import OFSCNotFoundError
from ofsc.models import (
    ActivityType,
    ActivityTypeGroup,
    Application,
    CapacityCategory,
    Form,
    InventoryType,
    LinkTemplate,
    MapLayer,
    Property,
    Shift,
    Workzone,
    WorkzoneListResponse,
)


def _mock_response(
    status_code: int, json_data: dict | None = None, content: bool = False
):
    """Build a mock httpx response."""
    mock = Mock()
    mock.status_code = status_code
    mock.raise_for_status = Mock()
    if json_data is not None:
        mock.json.return_value = json_data
    if not content:
        mock.content = b"" if status_code == 204 else b"{}"
    return mock


# ============================================================
# Activity Type Groups — PUT
# ============================================================


_ATG_DATA = {
    "label": "RESIDENTIAL",
    "name": "Residential",
    "translations": [{"language": "en", "name": "Residential", "languageISO": "en-US"}],
}


class TestCreateOrReplaceActivityTypeGroup:
    """Tests for create_or_replace_activity_type_group."""

    @pytest.mark.asyncio
    async def test_create_or_replace_returns_model(self, async_instance: AsyncOFSC):
        """Test that create_or_replace_activity_type_group returns ActivityTypeGroup."""
        mock_response = _mock_response(200, _ATG_DATA)
        async_instance.metadata._client.put = AsyncMock(return_value=mock_response)

        data = ActivityTypeGroup.model_validate(_ATG_DATA)
        result = await async_instance.metadata.create_or_replace_activity_type_group(
            data
        )

        assert isinstance(result, ActivityTypeGroup)
        assert result.label == "RESIDENTIAL"
        async_instance.metadata._client.put.assert_called_once()
        call_url = async_instance.metadata._client.put.call_args[0][0]
        assert "activityTypeGroups/RESIDENTIAL" in call_url

    @pytest.mark.asyncio
    async def test_links_stripped_from_response(self, async_instance: AsyncOFSC):
        """Test that 'links' key is stripped from response."""
        mock_response = _mock_response(200, {**_ATG_DATA, "links": []})
        async_instance.metadata._client.put = AsyncMock(return_value=mock_response)

        data = ActivityTypeGroup.model_validate(_ATG_DATA)
        result = await async_instance.metadata.create_or_replace_activity_type_group(
            data
        )
        assert isinstance(result, ActivityTypeGroup)


# ============================================================
# Activity Types — PUT
# ============================================================


_AT_DATA = {
    "label": "INSTALL",
    "name": "Installation",
    "active": True,
    "colors": None,
    "defaultDuration": 60,
    "features": None,
    "groupLabel": None,
    "translations": [
        {"language": "en", "name": "Installation", "languageISO": "en-US"}
    ],
}

_AT_SPACE_DATA = {
    "label": "TYPE A",
    "name": "Type A",
    "active": True,
    "colors": None,
    "defaultDuration": 30,
    "features": None,
    "groupLabel": None,
    "translations": [{"language": "en", "name": "Type A", "languageISO": "en-US"}],
}


class TestCreateOrReplaceActivityType:
    """Tests for create_or_replace_activity_type."""

    @pytest.mark.asyncio
    async def test_create_or_replace_returns_model(self, async_instance: AsyncOFSC):
        """Test that create_or_replace_activity_type returns ActivityType."""
        mock_response = _mock_response(200, _AT_DATA)
        async_instance.metadata._client.put = AsyncMock(return_value=mock_response)

        data = ActivityType.model_validate(_AT_DATA)
        result = await async_instance.metadata.create_or_replace_activity_type(data)

        assert isinstance(result, ActivityType)
        assert result.label == "INSTALL"
        call_url = async_instance.metadata._client.put.call_args[0][0]
        assert "activityTypes/INSTALL" in call_url

    @pytest.mark.asyncio
    async def test_label_is_url_encoded(self, async_instance: AsyncOFSC):
        """Test that label with special chars is URL encoded in path."""
        mock_response = _mock_response(200, _AT_SPACE_DATA)
        async_instance.metadata._client.put = AsyncMock(return_value=mock_response)

        data = ActivityType.model_validate(_AT_SPACE_DATA)
        await async_instance.metadata.create_or_replace_activity_type(data)

        call_url = async_instance.metadata._client.put.call_args[0][0]
        assert "TYPE+A" in call_url or "TYPE%20A" in call_url


# ============================================================
# Applications — PUT, PATCH, POST
# ============================================================


_APP_DATA = {
    "label": "MY_APP",
    "name": "My App",
    "status": "active",
    "tokenService": "oauth",
}


class TestCreateOrReplaceApplication:
    """Tests for create_or_replace_application."""

    @pytest.mark.asyncio
    async def test_create_or_replace_returns_model(self, async_instance: AsyncOFSC):
        """Test that create_or_replace_application returns Application."""
        mock_response = _mock_response(200, _APP_DATA)
        async_instance.metadata._client.put = AsyncMock(return_value=mock_response)

        data = Application.model_validate(_APP_DATA)
        result = await async_instance.metadata.create_or_replace_application(data)

        assert isinstance(result, Application)
        assert result.label == "MY_APP"
        call_url = async_instance.metadata._client.put.call_args[0][0]
        assert "applications/MY_APP" in call_url


class TestUpdateApplicationApiAccess:
    """Tests for update_application_api_access."""

    @pytest.mark.asyncio
    async def test_update_returns_api_access(self, async_instance: AsyncOFSC):
        """Test that update_application_api_access returns an ApplicationApiAccess."""
        # Use a label not in API_TYPE_MAP → StructuredApiAccess (only needs label/name/status)
        mock_response = _mock_response(
            200,
            {"label": "outboundAPI", "name": "Outbound API", "status": "active"},
        )
        async_instance.metadata._client.patch = AsyncMock(return_value=mock_response)

        result = await async_instance.metadata.update_application_api_access(
            "MY_APP", "outboundAPI", {"status": "active"}
        )

        # parse_application_api_access returns a union type — just check it's not None
        assert result is not None
        call_url = async_instance.metadata._client.patch.call_args[0][0]
        assert "applications/MY_APP/apiAccess/outboundAPI" in call_url

    @pytest.mark.asyncio
    async def test_update_passes_body(self, async_instance: AsyncOFSC):
        """Test that update sends correct body."""
        mock_response = _mock_response(
            200, {"label": "outboundAPI", "name": "Outbound API", "status": "inactive"}
        )
        async_instance.metadata._client.patch = AsyncMock(return_value=mock_response)

        patch_data = {"status": "inactive"}
        await async_instance.metadata.update_application_api_access(
            "MY_APP", "outboundAPI", patch_data
        )

        call_kwargs = async_instance.metadata._client.patch.call_args[1]
        assert call_kwargs["json"] == patch_data


class TestGenerateApplicationClientSecret:
    """Tests for generate_application_client_secret."""

    @pytest.mark.asyncio
    async def test_generate_returns_dict(self, async_instance: AsyncOFSC):
        """Test that generate_application_client_secret returns a dict."""
        mock_response = _mock_response(
            200,
            {"clientSecret": "abc123xyz"},
        )
        async_instance.metadata._client.post = AsyncMock(return_value=mock_response)

        result = await async_instance.metadata.generate_application_client_secret(
            "MY_APP"
        )

        assert isinstance(result, dict)
        assert result["clientSecret"] == "abc123xyz"
        call_url = async_instance.metadata._client.post.call_args[0][0]
        assert "applications/MY_APP/custom-actions/generateClientSecret" in call_url


# ============================================================
# Capacity Categories — PUT, DELETE
# ============================================================


class TestCreateOrReplaceCapacityCategory:
    """Tests for create_or_replace_capacity_category."""

    @pytest.mark.asyncio
    async def test_create_or_replace_returns_model(self, async_instance: AsyncOFSC):
        """Test that create_or_replace_capacity_category returns CapacityCategory."""
        mock_response = _mock_response(
            200,
            {"label": "BASIC", "name": "Basic Category", "active": True},
        )
        async_instance.metadata._client.put = AsyncMock(return_value=mock_response)

        data = CapacityCategory(label="BASIC", name="Basic Category", active=True)
        result = await async_instance.metadata.create_or_replace_capacity_category(data)

        assert isinstance(result, CapacityCategory)
        assert result.label == "BASIC"
        call_url = async_instance.metadata._client.put.call_args[0][0]
        assert "capacityCategories/BASIC" in call_url


class TestDeleteCapacityCategory:
    """Tests for delete_capacity_category."""

    @pytest.mark.asyncio
    async def test_delete_returns_none(self, async_instance: AsyncOFSC):
        """Test that delete_capacity_category returns None on success."""
        mock_response = _mock_response(204)
        async_instance.metadata._client.delete = AsyncMock(return_value=mock_response)

        result = await async_instance.metadata.delete_capacity_category("BASIC")

        assert result is None
        call_url = async_instance.metadata._client.delete.call_args[0][0]
        assert "capacityCategories/BASIC" in call_url

    @pytest.mark.asyncio
    async def test_delete_not_found_raises(self, async_instance: AsyncOFSC):
        """Test that 404 raises OFSCNotFoundError."""
        import httpx

        mock_request = Mock()
        mock_request.method = "DELETE"
        mock_request.url = Mock()

        error_response = Mock(spec=httpx.Response)
        error_response.status_code = 404
        error_response.json.return_value = {
            "type": "https://example.com/not-found",
            "title": "Not Found",
            "detail": "Capacity category not found",
        }
        error_response.request = mock_request
        error_response.text = '{"type":"not-found","title":"Not Found","detail":"..."}'

        http_error = httpx.HTTPStatusError(
            "404", request=mock_request, response=error_response
        )

        mock_response = Mock()
        mock_response.raise_for_status = Mock(side_effect=http_error)
        async_instance.metadata._client.delete = AsyncMock(return_value=mock_response)

        with pytest.raises(OFSCNotFoundError):
            await async_instance.metadata.delete_capacity_category("NONEXISTENT")


# ============================================================
# Forms — PUT, DELETE
# ============================================================


class TestCreateOrReplaceForm:
    """Tests for create_or_replace_form."""

    @pytest.mark.asyncio
    async def test_create_or_replace_returns_model(self, async_instance: AsyncOFSC):
        """Test that create_or_replace_form returns Form."""
        mock_response = _mock_response(
            200,
            {"label": "INSPECTION", "name": "Inspection Form"},
        )
        async_instance.metadata._client.put = AsyncMock(return_value=mock_response)

        data = Form(label="INSPECTION", name="Inspection Form")
        result = await async_instance.metadata.create_or_replace_form(data)

        assert isinstance(result, Form)
        assert result.label == "INSPECTION"
        call_url = async_instance.metadata._client.put.call_args[0][0]
        assert "forms/INSPECTION" in call_url


class TestDeleteForm:
    """Tests for delete_form."""

    @pytest.mark.asyncio
    async def test_delete_returns_none(self, async_instance: AsyncOFSC):
        """Test that delete_form returns None on success."""
        mock_response = _mock_response(204)
        async_instance.metadata._client.delete = AsyncMock(return_value=mock_response)

        result = await async_instance.metadata.delete_form("INSPECTION")

        assert result is None
        call_url = async_instance.metadata._client.delete.call_args[0][0]
        assert "forms/INSPECTION" in call_url


# ============================================================
# Inventory Types — PUT
# ============================================================


class TestCreateOrReplaceInventoryType:
    """Tests for create_or_replace_inventory_type."""

    @pytest.mark.asyncio
    async def test_create_or_replace_returns_model(self, async_instance: AsyncOFSC):
        """Test that create_or_replace_inventory_type returns InventoryType."""
        mock_response = _mock_response(
            200,
            {"label": "CABLE", "active": True, "nonSerialized": False},
        )
        async_instance.metadata._client.put = AsyncMock(return_value=mock_response)

        data = InventoryType(label="CABLE", active=True)
        result = await async_instance.metadata.create_or_replace_inventory_type(data)

        assert isinstance(result, InventoryType)
        assert result.label == "CABLE"
        call_url = async_instance.metadata._client.put.call_args[0][0]
        assert "inventoryTypes/CABLE" in call_url


# ============================================================
# Link Templates — POST, PATCH
# ============================================================


_LINK_TEMPLATE_DATA = {
    "label": "FOLLOW_UP",
    "name": "Follow Up",
    "active": True,
    "linkType": "finishToStart",
    "translations": [{"language": "en", "name": "Follow Up"}],
}


class TestCreateLinkTemplate:
    """Tests for create_link_template."""

    @pytest.mark.asyncio
    async def test_create_returns_model(self, async_instance: AsyncOFSC):
        """Test that create_link_template returns LinkTemplate."""
        mock_response = _mock_response(201, _LINK_TEMPLATE_DATA)
        async_instance.metadata._client.post = AsyncMock(return_value=mock_response)

        data = LinkTemplate.model_validate(_LINK_TEMPLATE_DATA)
        result = await async_instance.metadata.create_link_template(data)

        assert isinstance(result, LinkTemplate)
        assert result.label == "FOLLOW_UP"
        call_url = async_instance.metadata._client.post.call_args[0][0]
        assert "linkTemplates" in call_url
        # Label is a path parameter per swagger (POST to /linkTemplates/{label})
        assert "FOLLOW_UP" in call_url


class TestUpdateLinkTemplate:
    """Tests for update_link_template."""

    @pytest.mark.asyncio
    async def test_update_returns_model(self, async_instance: AsyncOFSC):
        """Test that update_link_template returns LinkTemplate."""
        updated = {**_LINK_TEMPLATE_DATA, "name": "Follow Up Updated"}
        mock_response = _mock_response(200, updated)
        async_instance.metadata._client.patch = AsyncMock(return_value=mock_response)

        data = LinkTemplate.model_validate(_LINK_TEMPLATE_DATA)
        result = await async_instance.metadata.update_link_template(data)

        assert isinstance(result, LinkTemplate)
        assert result.label == "FOLLOW_UP"
        call_url = async_instance.metadata._client.patch.call_args[0][0]
        assert "linkTemplates/FOLLOW_UP" in call_url


# ============================================================
# Map Layers — PUT, POST, POST file upload
# ============================================================


class TestCreateOrReplaceMapLayer:
    """Tests for create_or_replace_map_layer."""

    @pytest.mark.asyncio
    async def test_create_or_replace_returns_model(self, async_instance: AsyncOFSC):
        """Test that create_or_replace_map_layer returns MapLayer."""
        mock_response = _mock_response(
            200,
            {"label": "COVERAGE", "name": "Coverage Layer", "status": "active"},
        )
        async_instance.metadata._client.put = AsyncMock(return_value=mock_response)

        data = MapLayer(label="COVERAGE", name="Coverage Layer", status="active")
        result = await async_instance.metadata.create_or_replace_map_layer(data)

        assert isinstance(result, MapLayer)
        assert result.label == "COVERAGE"
        call_url = async_instance.metadata._client.put.call_args[0][0]
        assert "mapLayers/COVERAGE" in call_url


class TestCreateMapLayer:
    """Tests for create_map_layer."""

    @pytest.mark.asyncio
    async def test_create_returns_model(self, async_instance: AsyncOFSC):
        """Test that create_map_layer returns MapLayer."""
        mock_response = _mock_response(
            201,
            {"label": "NEW_LAYER", "name": "New Layer", "status": "active"},
        )
        async_instance.metadata._client.post = AsyncMock(return_value=mock_response)

        data = MapLayer(label="NEW_LAYER", name="New Layer", status="active")
        result = await async_instance.metadata.create_map_layer(data)

        assert isinstance(result, MapLayer)
        assert result.label == "NEW_LAYER"
        call_url = async_instance.metadata._client.post.call_args[0][0]
        assert "/mapLayers" in call_url
        assert "NEW_LAYER" not in call_url  # POST to collection, not /{label}


class TestPopulateMapLayers:
    """Tests for populate_map_layers."""

    @pytest.mark.asyncio
    async def test_populate_from_bytes(self, async_instance: AsyncOFSC):
        """Test populate_map_layers with bytes input."""
        mock_response = _mock_response(204)
        async_instance.metadata._client.post = AsyncMock(return_value=mock_response)

        result = await async_instance.metadata.populate_map_layers(b"csv,data\nrow1")

        assert result is None
        call_url = async_instance.metadata._client.post.call_args[0][0]
        assert "populateLayers" in call_url

    @pytest.mark.asyncio
    async def test_populate_from_path(self, async_instance: AsyncOFSC, tmp_path):
        """Test populate_map_layers with Path input."""
        mock_response = _mock_response(204)
        async_instance.metadata._client.post = AsyncMock(return_value=mock_response)

        csv_file = tmp_path / "layers.csv"
        csv_file.write_bytes(b"label,name\nLAYER1,Layer 1")

        result = await async_instance.metadata.populate_map_layers(csv_file)

        assert result is None
        call_kwargs = async_instance.metadata._client.post.call_args[1]
        assert "files" in call_kwargs


# ============================================================
# Plugins — POST install
# ============================================================


class TestInstallPlugin:
    """Tests for install_plugin."""

    @pytest.mark.asyncio
    async def test_install_returns_dict(self, async_instance: AsyncOFSC):
        """Test that install_plugin returns a dict."""
        mock_response = _mock_response(
            200,
            {"status": "installed"},
        )
        async_instance.metadata._client.post = AsyncMock(return_value=mock_response)

        result = await async_instance.metadata.install_plugin("MY_PLUGIN")

        assert isinstance(result, dict)
        call_url = async_instance.metadata._client.post.call_args[0][0]
        assert "plugins/MY_PLUGIN/custom-actions/install" in call_url

    @pytest.mark.asyncio
    async def test_install_204_returns_empty_dict(self, async_instance: AsyncOFSC):
        """Test that 204 No Content returns empty dict."""
        mock_response = _mock_response(204)
        mock_response.content = b""
        async_instance.metadata._client.post = AsyncMock(return_value=mock_response)

        result = await async_instance.metadata.install_plugin("MY_PLUGIN")

        assert result == {}


# ============================================================
# Properties — PATCH
# ============================================================


class TestUpdateProperty:
    """Tests for update_property."""

    @pytest.mark.asyncio
    async def test_update_returns_model(self, async_instance: AsyncOFSC):
        """Test that update_property returns Property."""
        mock_response = _mock_response(
            200,
            {
                "label": "customer_name",
                "name": "Customer Name",
                "type": "string",
                "translations": [{"language": "en", "name": "Customer Name"}],
            },
        )
        async_instance.metadata._client.patch = AsyncMock(return_value=mock_response)

        data = Property.model_validate(
            {
                "label": "customer_name",
                "name": "Customer Name Updated",
                "type": "string",
                "translations": [{"language": "en", "name": "Customer Name Updated"}],
            }
        )
        result = await async_instance.metadata.update_property(data)

        assert isinstance(result, Property)
        assert result.label == "customer_name"
        call_url = async_instance.metadata._client.patch.call_args[0][0]
        assert "properties/customer_name" in call_url

    @pytest.mark.asyncio
    async def test_update_uses_patch_method(self, async_instance: AsyncOFSC):
        """Test that update_property uses PATCH not PUT."""
        mock_response = _mock_response(
            200,
            {
                "label": "prop1",
                "name": "Property 1",
                "type": "string",
                "translations": [{"language": "en", "name": "Property 1"}],
            },
        )
        async_instance.metadata._client.patch = AsyncMock(return_value=mock_response)

        data = Property.model_validate(
            {
                "label": "prop1",
                "name": "Property 1",
                "type": "string",
                "translations": [{"language": "en", "name": "Property 1"}],
            }
        )
        await async_instance.metadata.update_property(data)

        # patch was called, not put
        assert async_instance.metadata._client.patch.called


# ============================================================
# Shifts — PUT, DELETE
# ============================================================


_SHIFT_REGULAR_DATA = {
    "label": "8-17",
    "name": "First shift 8-17",
    "active": True,
    "type": "regular",
    "workTimeStart": "08:00:00",
    "workTimeEnd": "17:00:00",
}

_SHIFT_ONCALL_DATA = {
    "label": "on-call",
    "name": "On Call",
    "active": True,
    "type": "on-call",
    "workTimeStart": "00:00:00",
    "workTimeEnd": "23:59:59",
}


class TestCreateOrReplaceShift:
    """Tests for create_or_replace_shift."""

    @pytest.mark.asyncio
    async def test_create_or_replace_returns_model(self, async_instance: AsyncOFSC):
        """Test that create_or_replace_shift returns Shift."""
        mock_response = _mock_response(200, _SHIFT_REGULAR_DATA)
        async_instance.metadata._client.put = AsyncMock(return_value=mock_response)

        data = Shift.model_validate(_SHIFT_REGULAR_DATA)
        result = await async_instance.metadata.create_or_replace_shift(data)

        assert isinstance(result, Shift)
        assert result.label == "8-17"
        call_url = async_instance.metadata._client.put.call_args[0][0]
        assert "shifts/8-17" in call_url

    @pytest.mark.asyncio
    async def test_label_url_encoded(self, async_instance: AsyncOFSC):
        """Test that label with hyphens is URL encoded."""
        mock_response = _mock_response(200, _SHIFT_ONCALL_DATA)
        async_instance.metadata._client.put = AsyncMock(return_value=mock_response)

        data = Shift.model_validate(_SHIFT_ONCALL_DATA)
        await async_instance.metadata.create_or_replace_shift(data)

        call_url = async_instance.metadata._client.put.call_args[0][0]
        assert "on-call" in call_url or "on%2Dcall" in call_url


class TestDeleteShift:
    """Tests for delete_shift."""

    @pytest.mark.asyncio
    async def test_delete_returns_none(self, async_instance: AsyncOFSC):
        """Test that delete_shift returns None on success."""
        mock_response = _mock_response(204)
        async_instance.metadata._client.delete = AsyncMock(return_value=mock_response)

        result = await async_instance.metadata.delete_shift("8-17")

        assert result is None
        call_url = async_instance.metadata._client.delete.call_args[0][0]
        assert "shifts" in call_url


# ============================================================
# Work Zones — bulk PUT, bulk PATCH, POST file upload
# ============================================================


_WZ_DATA = {
    "workZoneLabel": "WZ1",
    "workZoneName": "Zone 1",
    "status": "active",
    "travelArea": "US",
}

_WZ2_DATA = {
    "workZoneLabel": "WZ2",
    "workZoneName": "Zone 2",
    "status": "active",
    "travelArea": "US",
}


class TestReplaceWorkzones:
    """Tests for replace_workzones (bulk PUT)."""

    @pytest.mark.asyncio
    async def test_replace_returns_list_response(self, async_instance: AsyncOFSC):
        """Test that replace_workzones returns WorkzoneListResponse."""
        mock_response = _mock_response(
            200,
            {"items": [_WZ_DATA, _WZ2_DATA], "totalResults": 2},
        )
        async_instance.metadata._client.put = AsyncMock(return_value=mock_response)

        data = [Workzone.model_validate(_WZ_DATA), Workzone.model_validate(_WZ2_DATA)]
        result = await async_instance.metadata.replace_workzones(data)

        assert isinstance(result, WorkzoneListResponse)
        assert len(result.items) == 2
        call_url = async_instance.metadata._client.put.call_args[0][0]
        assert call_url.endswith("/workZones")

    @pytest.mark.asyncio
    async def test_replace_sends_items_body(self, async_instance: AsyncOFSC):
        """Test that replace_workzones sends {"items": [...]} body."""
        mock_response = _mock_response(200, {"items": [], "totalResults": 0})
        async_instance.metadata._client.put = AsyncMock(return_value=mock_response)

        await async_instance.metadata.replace_workzones([])

        call_kwargs = async_instance.metadata._client.put.call_args[1]
        assert "json" in call_kwargs
        assert "items" in call_kwargs["json"]


class TestUpdateWorkzones:
    """Tests for update_workzones (bulk PATCH)."""

    @pytest.mark.asyncio
    async def test_update_returns_list_response(self, async_instance: AsyncOFSC):
        """Test that update_workzones returns WorkzoneListResponse."""
        wz_updated = {**_WZ_DATA, "workZoneName": "Zone 1 Updated"}
        mock_response = _mock_response(
            200,
            {"items": [wz_updated], "totalResults": 1},
        )
        async_instance.metadata._client.patch = AsyncMock(return_value=mock_response)

        data = [Workzone.model_validate(_WZ_DATA)]
        result = await async_instance.metadata.update_workzones(data)

        assert isinstance(result, WorkzoneListResponse)
        assert len(result.items) == 1
        call_url = async_instance.metadata._client.patch.call_args[0][0]
        assert call_url.endswith("/workZones")

    @pytest.mark.asyncio
    async def test_update_uses_patch_method(self, async_instance: AsyncOFSC):
        """Test that update_workzones uses PATCH not PUT."""
        mock_response = _mock_response(200, {"items": [], "totalResults": 0})
        async_instance.metadata._client.patch = AsyncMock(return_value=mock_response)

        await async_instance.metadata.update_workzones([])

        assert async_instance.metadata._client.patch.called


class TestPopulateWorkzoneShapes:
    """Tests for populate_workzone_shapes."""

    @pytest.mark.asyncio
    async def test_populate_from_bytes(self, async_instance: AsyncOFSC):
        """Test populate_workzone_shapes with bytes input."""
        mock_response = _mock_response(204)
        async_instance.metadata._client.post = AsyncMock(return_value=mock_response)

        result = await async_instance.metadata.populate_workzone_shapes(b"shape,data")

        assert result is None
        call_url = async_instance.metadata._client.post.call_args[0][0]
        assert "populateShapes" in call_url

    @pytest.mark.asyncio
    async def test_populate_from_path(self, async_instance: AsyncOFSC, tmp_path):
        """Test populate_workzone_shapes with Path input."""
        mock_response = _mock_response(204)
        async_instance.metadata._client.post = AsyncMock(return_value=mock_response)

        shapes_file = tmp_path / "shapes.csv"
        shapes_file.write_bytes(b"zone,shape\nWZ1,polygon")

        result = await async_instance.metadata.populate_workzone_shapes(shapes_file)

        assert result is None
        call_kwargs = async_instance.metadata._client.post.call_args[1]
        assert "files" in call_kwargs
