"""Tests for async exception handling."""

import pytest
import httpx
from unittest.mock import AsyncMock, Mock

from ofsc.async_client import AsyncOFSC
from ofsc.exceptions import (
    OFSCAuthenticationError,
    OFSCAuthorizationError,
    OFSCConflictError,
    OFSCNetworkError,
    OFSCNotFoundError,
    OFSCRateLimitError,
    OFSCServerError,
    OFSCValidationError,
)


@pytest.mark.asyncio
async def test_not_found_error():
    """Test that 404 errors raise OFSCNotFoundError."""
    async with AsyncOFSC(
        clientID="test",
        companyName="test",
        secret="test",
    ) as client:
        # Mock the response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {
            "type": "about:blank",
            "title": "Not Found",
            "detail": "The requested workzone could not be found",
        }

        client.metadata._client.get = AsyncMock(
            side_effect=httpx.HTTPStatusError(
                "404", request=Mock(), response=mock_response
            )
        )

        with pytest.raises(OFSCNotFoundError) as exc_info:
            await client.metadata.get_workzone("nonexistent")

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "The requested workzone could not be found"
        assert exc_info.value.title == "Not Found"
        assert "nonexistent" in str(exc_info.value)


@pytest.mark.asyncio
async def test_authentication_error():
    """Test that 401 errors raise OFSCAuthenticationError."""
    async with AsyncOFSC(
        clientID="test",
        companyName="test",
        secret="test",
    ) as client:
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "type": "about:blank",
            "title": "Unauthorized",
            "detail": "Authentication credentials are missing or invalid",
        }

        client.metadata._client.get = AsyncMock(
            side_effect=httpx.HTTPStatusError(
                "401", request=Mock(), response=mock_response
            )
        )

        with pytest.raises(OFSCAuthenticationError) as exc_info:
            await client.metadata.get_workzones()

        assert exc_info.value.status_code == 401
        assert "Authentication credentials" in exc_info.value.detail


@pytest.mark.asyncio
async def test_authorization_error():
    """Test that 403 errors raise OFSCAuthorizationError."""
    async with AsyncOFSC(
        clientID="test",
        companyName="test",
        secret="test",
    ) as client:
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.json.return_value = {
            "type": "about:blank",
            "title": "Forbidden",
            "detail": "You do not have permission to access this resource",
        }

        client.metadata._client.get = AsyncMock(
            side_effect=httpx.HTTPStatusError(
                "403", request=Mock(), response=mock_response
            )
        )

        with pytest.raises(OFSCAuthorizationError) as exc_info:
            await client.metadata.get_workzone("test")

        assert exc_info.value.status_code == 403
        assert "permission" in exc_info.value.detail


@pytest.mark.asyncio
async def test_conflict_error():
    """Test that 409 errors raise OFSCConflictError."""
    from ofsc.models import Workzone

    async with AsyncOFSC(
        clientID="test",
        companyName="test",
        secret="test",
    ) as client:
        mock_response = Mock()
        mock_response.status_code = 409
        mock_response.json.return_value = {
            "type": "about:blank",
            "title": "Conflict",
            "detail": "Workzone already exists",
        }

        client.metadata._client.post = AsyncMock(
            side_effect=httpx.HTTPStatusError(
                "409", request=Mock(), response=mock_response
            )
        )

        workzone = Workzone(
            workZoneLabel="test",
            workZoneName="Test",
            status="active",
            travelArea="area1",
        )

        with pytest.raises(OFSCConflictError) as exc_info:
            await client.metadata.create_workzone(workzone)

        assert exc_info.value.status_code == 409
        assert "already exists" in exc_info.value.detail


@pytest.mark.asyncio
async def test_validation_error():
    """Test that 400 errors raise OFSCValidationError."""
    from ofsc.models import Workzone

    async with AsyncOFSC(
        clientID="test",
        companyName="test",
        secret="test",
    ) as client:
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "type": "about:blank",
            "title": "Bad Request",
            "detail": "Invalid workzone label format",
        }

        client.metadata._client.post = AsyncMock(
            side_effect=httpx.HTTPStatusError(
                "400", request=Mock(), response=mock_response
            )
        )

        workzone = Workzone(
            workZoneLabel="invalid label",
            workZoneName="Test",
            status="active",
            travelArea="area1",
        )

        with pytest.raises(OFSCValidationError) as exc_info:
            await client.metadata.create_workzone(workzone)

        assert exc_info.value.status_code == 400
        assert "Invalid" in exc_info.value.detail


@pytest.mark.asyncio
async def test_rate_limit_error():
    """Test that 429 errors raise OFSCRateLimitError."""
    async with AsyncOFSC(
        clientID="test",
        companyName="test",
        secret="test",
    ) as client:
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.json.return_value = {
            "type": "about:blank",
            "title": "Too Many Requests",
            "detail": "Rate limit exceeded. Please try again later.",
        }

        client.metadata._client.get = AsyncMock(
            side_effect=httpx.HTTPStatusError(
                "429", request=Mock(), response=mock_response
            )
        )

        with pytest.raises(OFSCRateLimitError) as exc_info:
            await client.metadata.get_workzones()

        assert exc_info.value.status_code == 429
        assert "Rate limit" in exc_info.value.detail


@pytest.mark.asyncio
async def test_server_error():
    """Test that 5xx errors raise OFSCServerError."""
    async with AsyncOFSC(
        clientID="test",
        companyName="test",
        secret="test",
    ) as client:
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {
            "type": "about:blank",
            "title": "Internal Server Error",
            "detail": "An unexpected error occurred on the server",
        }

        client.metadata._client.get = AsyncMock(
            side_effect=httpx.HTTPStatusError(
                "500", request=Mock(), response=mock_response
            )
        )

        with pytest.raises(OFSCServerError) as exc_info:
            await client.metadata.get_workzone("test")

        assert exc_info.value.status_code == 500
        assert "server" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_network_error():
    """Test that network errors raise OFSCNetworkError."""
    async with AsyncOFSC(
        clientID="test",
        companyName="test",
        secret="test",
    ) as client:
        client.metadata._client.get = AsyncMock(
            side_effect=httpx.ConnectError("Connection refused")
        )

        with pytest.raises(OFSCNetworkError) as exc_info:
            await client.metadata.get_workzones()

        assert "Network error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_exception_chain_preserved():
    """Test that original httpx exception is preserved in the chain."""
    async with AsyncOFSC(
        clientID="test",
        companyName="test",
        secret="test",
    ) as client:
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {
            "type": "about:blank",
            "title": "Not Found",
            "detail": "Resource not found",
        }

        client.metadata._client.get = AsyncMock(
            side_effect=httpx.HTTPStatusError(
                "404", request=Mock(), response=mock_response
            )
        )

        with pytest.raises(OFSCNotFoundError) as exc_info:
            await client.metadata.get_workzone("test")

        # Verify the exception chain
        assert isinstance(exc_info.value.__cause__, httpx.HTTPStatusError)


@pytest.mark.asyncio
async def test_error_response_parsing_non_json():
    """Test error parsing when response is not JSON."""
    async with AsyncOFSC(
        clientID="test",
        companyName="test",
        secret="test",
    ) as client:
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_response.json.side_effect = Exception("Not JSON")

        client.metadata._client.get = AsyncMock(
            side_effect=httpx.HTTPStatusError(
                "500", request=Mock(), response=mock_response
            )
        )

        with pytest.raises(OFSCServerError) as exc_info:
            await client.metadata.get_workzone("test")

        # Should fallback to text content
        assert exc_info.value.detail == "Internal Server Error"
        assert exc_info.value.error_type == "about:blank"
