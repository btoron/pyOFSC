"""Unit tests for AsyncClientBase helper methods."""

from unittest.mock import AsyncMock, Mock

import httpx
import pytest

from ofsc.async_client import AsyncOFSC
from ofsc.exceptions import (
    OFSCNetworkError,
    OFSCNotFoundError,
    OFSCAuthenticationError,
    OFSCValidationError,
)
from ofsc.models import Workzone, WorkzoneListResponse

# Complete Workzone dict that satisfies all required fields
_WORKZONE_DATA = {
    "workZoneLabel": "TEST",
    "workZoneName": "Test Zone",
    "status": "active",
    "travelArea": "urban",
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
async def mock_instance() -> AsyncOFSC:
    """Return an AsyncOFSC instance with dummy credentials."""
    async with AsyncOFSC(clientID="test", companyName="test", secret="test") as instance:
        yield instance


def _make_response(status: int = 200, json_data: dict | None = None, raise_exc: Exception | None = None) -> Mock:
    """Build a minimal httpx response mock."""
    mock = Mock()
    mock.status_code = status
    if json_data is not None:
        mock.json.return_value = json_data
    if raise_exc is not None:
        mock.raise_for_status.side_effect = raise_exc
    else:
        mock.raise_for_status = Mock()
    return mock


# ---------------------------------------------------------------------------
# _clean_response
# ---------------------------------------------------------------------------


class TestCleanResponse:
    """Tests for _clean_response helper."""

    @pytest.mark.asyncio
    async def test_removes_links_key(self, mock_instance: AsyncOFSC) -> None:
        """_clean_response removes the 'links' key from a dict."""
        data = {"items": [], "totalResults": 0, "links": [{"href": "..."}]}
        result = mock_instance.metadata._clean_response(data)
        assert "links" not in result
        assert result["items"] == []
        assert result["totalResults"] == 0

    @pytest.mark.asyncio
    async def test_no_op_when_links_absent(self, mock_instance: AsyncOFSC) -> None:
        """_clean_response is a no-op when 'links' is not present."""
        data = {"items": [1, 2], "totalResults": 2}
        result = mock_instance.metadata._clean_response(data)
        assert result == {"items": [1, 2], "totalResults": 2}

    @pytest.mark.asyncio
    async def test_returns_same_dict(self, mock_instance: AsyncOFSC) -> None:
        """_clean_response returns the same dict object (mutates in place)."""
        data = {"key": "value", "links": []}
        result = mock_instance.metadata._clean_response(data)
        assert result is data


# ---------------------------------------------------------------------------
# _get_paginated_list
# ---------------------------------------------------------------------------


class TestGetPaginatedList:
    """Tests for _get_paginated_list helper."""

    @pytest.mark.asyncio
    async def test_returns_validated_model(self, mock_instance: AsyncOFSC) -> None:
        """_get_paginated_list returns a validated Pydantic model."""
        mock_response = _make_response(json_data={"items": [], "totalResults": 0})
        mock_instance.metadata._client.get = AsyncMock(return_value=mock_response)

        result = await mock_instance.metadata._get_paginated_list(
            "/rest/ofscMetadata/v1/workZones",
            WorkzoneListResponse,
            "test context",
        )
        assert isinstance(result, WorkzoneListResponse)

    @pytest.mark.asyncio
    async def test_sends_offset_and_limit_params(self, mock_instance: AsyncOFSC) -> None:
        """_get_paginated_list passes offset and limit as query params."""
        mock_response = _make_response(json_data={"items": [], "totalResults": 0})
        mock_instance.metadata._client.get = AsyncMock(return_value=mock_response)

        await mock_instance.metadata._get_paginated_list(
            "/rest/ofscMetadata/v1/workZones",
            WorkzoneListResponse,
            "test context",
            offset=10,
            limit=50,
        )

        call_kwargs = mock_instance.metadata._client.get.call_args[1]
        assert call_kwargs["params"]["offset"] == 10
        assert call_kwargs["params"]["limit"] == 50

    @pytest.mark.asyncio
    async def test_merges_extra_params(self, mock_instance: AsyncOFSC) -> None:
        """_get_paginated_list merges extra_params into query string."""
        mock_response = _make_response(json_data={"items": [], "totalResults": 0})
        mock_instance.metadata._client.get = AsyncMock(return_value=mock_response)

        await mock_instance.metadata._get_paginated_list(
            "/rest/ofscMetadata/v1/workZones",
            WorkzoneListResponse,
            "test context",
            extra_params={"filter": "active"},
        )

        call_kwargs = mock_instance.metadata._client.get.call_args[1]
        assert call_kwargs["params"]["filter"] == "active"

    @pytest.mark.asyncio
    async def test_strips_links_from_response(self, mock_instance: AsyncOFSC) -> None:
        """_get_paginated_list removes 'links' before model validation."""
        mock_response = _make_response(json_data={"items": [], "totalResults": 0, "links": [{"href": "next"}]})
        mock_instance.metadata._client.get = AsyncMock(return_value=mock_response)

        # Should not raise a validation error from unexpected 'links' field
        result = await mock_instance.metadata._get_paginated_list(
            "/rest/ofscMetadata/v1/workZones",
            WorkzoneListResponse,
            "test context",
        )
        assert isinstance(result, WorkzoneListResponse)

    @pytest.mark.asyncio
    async def test_404_raises_ofsc_not_found_error(self, mock_instance: AsyncOFSC) -> None:
        """_get_paginated_list propagates 404 as OFSCNotFoundError."""
        mock_response = _make_response(status=404)
        mock_response.json.return_value = {"detail": "not found", "type": "about:blank", "title": "Not Found"}
        mock_response.text = "not found"
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError("404", request=Mock(), response=mock_response)
        mock_instance.metadata._client.get = AsyncMock(return_value=mock_response)

        with pytest.raises(OFSCNotFoundError):
            await mock_instance.metadata._get_paginated_list(
                "/rest/ofscMetadata/v1/workZones",
                WorkzoneListResponse,
                "test context",
            )

    @pytest.mark.asyncio
    async def test_transport_error_raises_ofsc_network_error(self, mock_instance: AsyncOFSC) -> None:
        """_get_paginated_list wraps TransportError as OFSCNetworkError."""
        mock_instance.metadata._client.get = AsyncMock(side_effect=httpx.TransportError("connection refused"))

        with pytest.raises(OFSCNetworkError):
            await mock_instance.metadata._get_paginated_list(
                "/rest/ofscMetadata/v1/workZones",
                WorkzoneListResponse,
                "test context",
            )


# ---------------------------------------------------------------------------
# _get_single_item
# ---------------------------------------------------------------------------


class TestGetSingleItem:
    """Tests for _get_single_item helper."""

    @pytest.mark.asyncio
    async def test_returns_validated_model(self, mock_instance: AsyncOFSC) -> None:
        """_get_single_item returns a validated Pydantic model."""
        mock_response = _make_response(json_data=_WORKZONE_DATA)
        mock_instance.metadata._client.get = AsyncMock(return_value=mock_response)

        result = await mock_instance.metadata._get_single_item(
            "/rest/ofscMetadata/v1/workZones/{label}",
            "TEST",
            Workzone,
            "test context",
        )
        assert isinstance(result, Workzone)
        assert result.workZoneLabel == "TEST"

    @pytest.mark.asyncio
    async def test_applies_quote_plus_to_label(self, mock_instance: AsyncOFSC) -> None:
        """_get_single_item URL-encodes the label with quote_plus."""
        mock_response = _make_response(json_data={**_WORKZONE_DATA, "workZoneLabel": "A B", "workZoneName": "A B"})
        mock_instance.metadata._client.get = AsyncMock(return_value=mock_response)

        await mock_instance.metadata._get_single_item(
            "/rest/ofscMetadata/v1/workZones/{label}",
            "A B",
            Workzone,
            "test context",
        )

        called_url = mock_instance.metadata._client.get.call_args[0][0]
        assert "A+B" in called_url

    @pytest.mark.asyncio
    async def test_404_raises_ofsc_not_found_error(self, mock_instance: AsyncOFSC) -> None:
        """_get_single_item propagates 404 as OFSCNotFoundError."""
        mock_response = _make_response(status=404)
        mock_response.json.return_value = {"detail": "not found", "type": "about:blank", "title": "Not Found"}
        mock_response.text = "not found"
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError("404", request=Mock(), response=mock_response)
        mock_instance.metadata._client.get = AsyncMock(return_value=mock_response)

        with pytest.raises(OFSCNotFoundError):
            await mock_instance.metadata._get_single_item(
                "/rest/ofscMetadata/v1/workZones/{label}",
                "NONEXISTENT",
                Workzone,
                "test context",
            )

    @pytest.mark.asyncio
    async def test_transport_error_raises_ofsc_network_error(self, mock_instance: AsyncOFSC) -> None:
        """_get_single_item wraps TransportError as OFSCNetworkError."""
        mock_instance.metadata._client.get = AsyncMock(side_effect=httpx.TransportError("timeout"))

        with pytest.raises(OFSCNetworkError):
            await mock_instance.metadata._get_single_item(
                "/rest/ofscMetadata/v1/workZones/{label}",
                "TEST",
                Workzone,
                "test context",
            )


# ---------------------------------------------------------------------------
# _get_all_items
# ---------------------------------------------------------------------------


class TestGetAllItems:
    """Tests for _get_all_items helper."""

    @pytest.mark.asyncio
    async def test_returns_validated_model(self, mock_instance: AsyncOFSC) -> None:
        """_get_all_items returns a validated Pydantic model."""
        mock_response = _make_response(json_data={"items": [], "totalResults": 0})
        mock_instance.metadata._client.get = AsyncMock(return_value=mock_response)

        result = await mock_instance.metadata._get_all_items(
            "/rest/ofscMetadata/v1/workZones",
            WorkzoneListResponse,
            "test context",
        )
        assert isinstance(result, WorkzoneListResponse)

    @pytest.mark.asyncio
    async def test_sends_no_pagination_params(self, mock_instance: AsyncOFSC) -> None:
        """_get_all_items does not send offset/limit params."""
        mock_response = _make_response(json_data={"items": [], "totalResults": 0})
        mock_instance.metadata._client.get = AsyncMock(return_value=mock_response)

        await mock_instance.metadata._get_all_items(
            "/rest/ofscMetadata/v1/workZones",
            WorkzoneListResponse,
            "test context",
        )

        # Should only pass headers, no params keyword
        call_kwargs = mock_instance.metadata._client.get.call_args[1]
        assert "params" not in call_kwargs

    @pytest.mark.asyncio
    async def test_transport_error_raises_ofsc_network_error(self, mock_instance: AsyncOFSC) -> None:
        """_get_all_items wraps TransportError as OFSCNetworkError."""
        mock_instance.metadata._client.get = AsyncMock(side_effect=httpx.TransportError("connection refused"))

        with pytest.raises(OFSCNetworkError):
            await mock_instance.metadata._get_all_items(
                "/rest/ofscMetadata/v1/workZones",
                WorkzoneListResponse,
                "test context",
            )


# ---------------------------------------------------------------------------
# _put_item
# ---------------------------------------------------------------------------


class TestPutItem:
    """Tests for _put_item helper."""

    @pytest.mark.asyncio
    async def test_returns_validated_model(self, mock_instance: AsyncOFSC) -> None:
        """_put_item returns a validated Pydantic model."""
        wz = Workzone.model_validate(_WORKZONE_DATA)
        mock_response = _make_response(json_data=_WORKZONE_DATA)
        mock_instance.metadata._client.put = AsyncMock(return_value=mock_response)

        result = await mock_instance.metadata._put_item(
            "/rest/ofscMetadata/v1/workZones/TEST",
            wz,
            Workzone,
            "test context",
        )
        assert isinstance(result, Workzone)

    @pytest.mark.asyncio
    async def test_uses_put_method(self, mock_instance: AsyncOFSC) -> None:
        """_put_item calls the PUT HTTP method."""
        wz = Workzone.model_validate(_WORKZONE_DATA)
        mock_response = _make_response(json_data=_WORKZONE_DATA)
        mock_instance.metadata._client.put = AsyncMock(return_value=mock_response)

        await mock_instance.metadata._put_item(
            "/rest/ofscMetadata/v1/workZones/TEST",
            wz,
            Workzone,
            "test context",
        )

        assert mock_instance.metadata._client.put.called

    @pytest.mark.asyncio
    async def test_400_raises_ofsc_validation_error(self, mock_instance: AsyncOFSC) -> None:
        """_put_item propagates 400 as OFSCValidationError."""
        wz = Workzone.model_validate(_WORKZONE_DATA)
        mock_response = _make_response(status=400)
        mock_response.json.return_value = {"detail": "bad request", "type": "about:blank", "title": "Bad Request"}
        mock_response.text = "bad request"
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError("400", request=Mock(), response=mock_response)
        mock_instance.metadata._client.put = AsyncMock(return_value=mock_response)

        with pytest.raises(OFSCValidationError):
            await mock_instance.metadata._put_item(
                "/rest/ofscMetadata/v1/workZones/TEST",
                wz,
                Workzone,
                "test context",
            )

    @pytest.mark.asyncio
    async def test_transport_error_raises_ofsc_network_error(self, mock_instance: AsyncOFSC) -> None:
        """_put_item wraps TransportError as OFSCNetworkError."""
        wz = Workzone.model_validate(_WORKZONE_DATA)
        mock_instance.metadata._client.put = AsyncMock(side_effect=httpx.TransportError("connection refused"))

        with pytest.raises(OFSCNetworkError):
            await mock_instance.metadata._put_item(
                "/rest/ofscMetadata/v1/workZones/TEST",
                wz,
                Workzone,
                "test context",
            )


# ---------------------------------------------------------------------------
# _post_item
# ---------------------------------------------------------------------------


class TestPostItem:
    """Tests for _post_item helper."""

    @pytest.mark.asyncio
    async def test_returns_validated_model(self, mock_instance: AsyncOFSC) -> None:
        """_post_item returns a validated Pydantic model."""
        wz = Workzone.model_validate({**_WORKZONE_DATA, "workZoneLabel": "NEW", "workZoneName": "New Zone"})
        mock_response = _make_response(json_data={**_WORKZONE_DATA, "workZoneLabel": "NEW", "workZoneName": "New Zone"})
        mock_instance.metadata._client.post = AsyncMock(return_value=mock_response)

        result = await mock_instance.metadata._post_item(
            "/rest/ofscMetadata/v1/workZones",
            wz,
            Workzone,
            "test context",
        )
        assert isinstance(result, Workzone)
        assert result.workZoneLabel == "NEW"

    @pytest.mark.asyncio
    async def test_uses_post_method(self, mock_instance: AsyncOFSC) -> None:
        """_post_item calls the POST HTTP method."""
        wz = Workzone.model_validate({**_WORKZONE_DATA, "workZoneLabel": "NEW", "workZoneName": "New Zone"})
        mock_response = _make_response(json_data={**_WORKZONE_DATA, "workZoneLabel": "NEW", "workZoneName": "New Zone"})
        mock_instance.metadata._client.post = AsyncMock(return_value=mock_response)

        await mock_instance.metadata._post_item(
            "/rest/ofscMetadata/v1/workZones",
            wz,
            Workzone,
            "test context",
        )

        assert mock_instance.metadata._client.post.called

    @pytest.mark.asyncio
    async def test_transport_error_raises_ofsc_network_error(self, mock_instance: AsyncOFSC) -> None:
        """_post_item wraps TransportError as OFSCNetworkError."""
        wz = Workzone.model_validate({**_WORKZONE_DATA, "workZoneLabel": "NEW", "workZoneName": "New Zone"})
        mock_instance.metadata._client.post = AsyncMock(side_effect=httpx.TransportError("connection refused"))

        with pytest.raises(OFSCNetworkError):
            await mock_instance.metadata._post_item(
                "/rest/ofscMetadata/v1/workZones",
                wz,
                Workzone,
                "test context",
            )


# ---------------------------------------------------------------------------
# _patch_item
# ---------------------------------------------------------------------------


class TestPatchItem:
    """Tests for _patch_item helper."""

    @pytest.mark.asyncio
    async def test_returns_validated_model(self, mock_instance: AsyncOFSC) -> None:
        """_patch_item returns a validated Pydantic model."""
        wz = Workzone.model_validate({**_WORKZONE_DATA, "workZoneName": "Updated Name"})
        mock_response = _make_response(json_data={**_WORKZONE_DATA, "workZoneName": "Updated Name"})
        mock_instance.metadata._client.patch = AsyncMock(return_value=mock_response)

        result = await mock_instance.metadata._patch_item(
            "/rest/ofscMetadata/v1/workZones/TEST",
            wz,
            Workzone,
            "test context",
        )
        assert isinstance(result, Workzone)

    @pytest.mark.asyncio
    async def test_uses_patch_method(self, mock_instance: AsyncOFSC) -> None:
        """_patch_item calls the PATCH HTTP method."""
        wz = Workzone.model_validate({**_WORKZONE_DATA, "workZoneName": "Updated"})
        mock_response = _make_response(json_data={**_WORKZONE_DATA, "workZoneName": "Updated"})
        mock_instance.metadata._client.patch = AsyncMock(return_value=mock_response)

        await mock_instance.metadata._patch_item(
            "/rest/ofscMetadata/v1/workZones/TEST",
            wz,
            Workzone,
            "test context",
        )

        assert mock_instance.metadata._client.patch.called

    @pytest.mark.asyncio
    async def test_404_raises_ofsc_not_found_error(self, mock_instance: AsyncOFSC) -> None:
        """_patch_item propagates 404 as OFSCNotFoundError."""
        wz = Workzone.model_validate({**_WORKZONE_DATA, "workZoneName": "X"})
        mock_response = _make_response(status=404)
        mock_response.json.return_value = {"detail": "not found", "type": "about:blank", "title": "Not Found"}
        mock_response.text = "not found"
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError("404", request=Mock(), response=mock_response)
        mock_instance.metadata._client.patch = AsyncMock(return_value=mock_response)

        with pytest.raises(OFSCNotFoundError):
            await mock_instance.metadata._patch_item(
                "/rest/ofscMetadata/v1/workZones/TEST",
                wz,
                Workzone,
                "test context",
            )

    @pytest.mark.asyncio
    async def test_transport_error_raises_ofsc_network_error(self, mock_instance: AsyncOFSC) -> None:
        """_patch_item wraps TransportError as OFSCNetworkError."""
        wz = Workzone.model_validate({**_WORKZONE_DATA, "workZoneName": "X"})
        mock_instance.metadata._client.patch = AsyncMock(side_effect=httpx.TransportError("connection refused"))

        with pytest.raises(OFSCNetworkError):
            await mock_instance.metadata._patch_item(
                "/rest/ofscMetadata/v1/workZones/TEST",
                wz,
                Workzone,
                "test context",
            )


# ---------------------------------------------------------------------------
# _delete_item
# ---------------------------------------------------------------------------


class TestDeleteItem:
    """Tests for _delete_item helper."""

    @pytest.mark.asyncio
    async def test_returns_none_on_success(self, mock_instance: AsyncOFSC) -> None:
        """_delete_item returns None on a successful delete."""
        mock_response = _make_response(status=204)
        mock_instance.metadata._client.delete = AsyncMock(return_value=mock_response)

        result = await mock_instance.metadata._delete_item(
            "/rest/ofscMetadata/v1/workZones/{label}",
            "TEST",
            "test context",
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_applies_quote_plus_to_label(self, mock_instance: AsyncOFSC) -> None:
        """_delete_item URL-encodes the label with quote_plus."""
        mock_response = _make_response(status=204)
        mock_instance.metadata._client.delete = AsyncMock(return_value=mock_response)

        await mock_instance.metadata._delete_item(
            "/rest/ofscMetadata/v1/workZones/{label}",
            "A B",
            "test context",
        )

        called_url = mock_instance.metadata._client.delete.call_args[0][0]
        assert "A+B" in called_url

    @pytest.mark.asyncio
    async def test_404_raises_ofsc_not_found_error(self, mock_instance: AsyncOFSC) -> None:
        """_delete_item propagates 404 as OFSCNotFoundError."""
        mock_response = _make_response(status=404)
        mock_response.json.return_value = {"detail": "not found", "type": "about:blank", "title": "Not Found"}
        mock_response.text = "not found"
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError("404", request=Mock(), response=mock_response)
        mock_instance.metadata._client.delete = AsyncMock(return_value=mock_response)

        with pytest.raises(OFSCNotFoundError):
            await mock_instance.metadata._delete_item(
                "/rest/ofscMetadata/v1/workZones/{label}",
                "NONEXISTENT",
                "test context",
            )

    @pytest.mark.asyncio
    async def test_401_raises_ofsc_authentication_error(self, mock_instance: AsyncOFSC) -> None:
        """_delete_item propagates 401 as OFSCAuthenticationError."""
        mock_response = _make_response(status=401)
        mock_response.json.return_value = {"detail": "unauthorized", "type": "about:blank", "title": "Unauthorized"}
        mock_response.text = "unauthorized"
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError("401", request=Mock(), response=mock_response)
        mock_instance.metadata._client.delete = AsyncMock(return_value=mock_response)

        with pytest.raises(OFSCAuthenticationError):
            await mock_instance.metadata._delete_item(
                "/rest/ofscMetadata/v1/workZones/{label}",
                "TEST",
                "test context",
            )

    @pytest.mark.asyncio
    async def test_transport_error_raises_ofsc_network_error(self, mock_instance: AsyncOFSC) -> None:
        """_delete_item wraps TransportError as OFSCNetworkError."""
        mock_instance.metadata._client.delete = AsyncMock(side_effect=httpx.TransportError("connection refused"))

        with pytest.raises(OFSCNetworkError):
            await mock_instance.metadata._delete_item(
                "/rest/ofscMetadata/v1/workZones/{label}",
                "TEST",
                "test context",
            )
