"""Async tests for OAuth2 token endpoint (AU002P)."""

from unittest.mock import AsyncMock, Mock

import httpx
import pytest

from ofsc.async_client import AsyncOFSC
from ofsc.exceptions import OFSCAuthenticationError, OFSCValidationError
from ofsc.models import OAuthTokenResponse, OFSOAuthRequest


TOKEN_RESPONSE = {
    "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.test",
    "token_type": "bearer",
    "expires_in": 3600,
}


# region Mocked tests


class TestAsyncGetToken:
    """Mocked tests for get_token (AU002P)."""

    @pytest.mark.asyncio
    async def test_returns_model(self, mock_instance: AsyncOFSC):
        """Test that get_token returns OAuthTokenResponse."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = TOKEN_RESPONSE
        mock_response.raise_for_status = Mock()
        mock_instance.oauth2._client.post = AsyncMock(return_value=mock_response)

        result = await mock_instance.oauth2.get_token()

        assert isinstance(result, OAuthTokenResponse)
        assert result.access_token == TOKEN_RESPONSE["access_token"]
        assert result.token_type == "bearer"
        assert result.expires_in == 3600

    @pytest.mark.asyncio
    async def test_uses_v2_url(self, mock_instance: AsyncOFSC):
        """Test that get_token calls the v2 endpoint."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = TOKEN_RESPONSE
        mock_response.raise_for_status = Mock()
        mock_post = AsyncMock(return_value=mock_response)
        mock_instance.oauth2._client.post = mock_post

        await mock_instance.oauth2.get_token()

        call_url = mock_post.call_args[0][0]
        assert "/rest/oauthTokenService/v2/token" in call_url

    @pytest.mark.asyncio
    async def test_uses_form_encoded_content_type(self, mock_instance: AsyncOFSC):
        """Test that the request uses application/x-www-form-urlencoded."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = TOKEN_RESPONSE
        mock_response.raise_for_status = Mock()
        mock_post = AsyncMock(return_value=mock_response)
        mock_instance.oauth2._client.post = mock_post

        await mock_instance.oauth2.get_token()

        call_headers = mock_post.call_args[1]["headers"]
        assert call_headers["Content-Type"] == "application/x-www-form-urlencoded"

    @pytest.mark.asyncio
    async def test_custom_request(self, mock_instance: AsyncOFSC):
        """Test that a custom OFSOAuthRequest is passed as form data."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = TOKEN_RESPONSE
        mock_response.raise_for_status = Mock()
        mock_post = AsyncMock(return_value=mock_response)
        mock_instance.oauth2._client.post = mock_post

        request = OFSOAuthRequest(grant_type="client_credentials")
        await mock_instance.oauth2.get_token(request)

        call_data = mock_post.call_args[1]["data"]
        assert call_data["grant_type"] == "client_credentials"

    @pytest.mark.asyncio
    async def test_invalid_credentials_raises_authentication_error(
        self, mock_instance: AsyncOFSC
    ):
        """Test that a 401 response raises OFSCAuthenticationError."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_response.json.return_value = {
            "type": "https://example.com/errors/unauthorized",
            "title": "Unauthorized",
            "detail": "Invalid client credentials",
        }
        error = httpx.HTTPStatusError(
            "401 Unauthorized", request=Mock(), response=mock_response
        )
        mock_instance.oauth2._client.post = AsyncMock(side_effect=error)

        with pytest.raises(OFSCAuthenticationError):
            await mock_instance.oauth2.get_token()

    @pytest.mark.asyncio
    async def test_bad_request_raises_validation_error(self, mock_instance: AsyncOFSC):
        """Test that a 400 response raises OFSCValidationError."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_response.json.return_value = {
            "type": "about:blank",
            "title": "Bad Request",
            "detail": "Invalid grant_type",
        }
        error = httpx.HTTPStatusError(
            "400 Bad Request", request=Mock(), response=mock_response
        )
        mock_instance.oauth2._client.post = AsyncMock(side_effect=error)

        with pytest.raises(OFSCValidationError):
            await mock_instance.oauth2.get_token()


# endregion

# region Live tests


class TestAsyncGetTokenLive:
    """Live tests for get_token against actual OFSC API."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_token(self, async_instance: AsyncOFSC):
        """Test get_token returns a valid token from the real API."""
        result = await async_instance.oauth2.get_token()

        assert isinstance(result, OAuthTokenResponse)
        assert result.access_token
        assert result.token_type.lower() == "bearer"
        assert result.expires_in > 0

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_token_with_explicit_request(self, async_instance: AsyncOFSC):
        """Test get_token with an explicit client_credentials request."""
        request = OFSOAuthRequest(grant_type="client_credentials")
        result = await async_instance.oauth2.get_token(request)

        assert isinstance(result, OAuthTokenResponse)
        assert result.access_token


# endregion

# region E2E tests


class TestAsyncTokenAuthE2E:
    """E2E tests: get token, then use it for API calls."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_token_auth_get_activity_types(self, async_instance: AsyncOFSC):
        """Get token, create token-authed client, compare activity_types results."""
        # 1. Get activity types with normal Basic auth
        basic_result = await async_instance.metadata.get_activity_types()

        # 2. Get OAuth token
        token_response = await async_instance.oauth2.get_token()

        # 3. Create new client using the token
        async with AsyncOFSC(
            clientID=async_instance._config.clientID,
            companyName=async_instance._config.companyName,
            secret=async_instance._config.secret,
            root=async_instance._config.root,
            useToken=True,
            access_token=token_response.access_token,
        ) as token_client:
            # 4. Get activity types with token auth
            token_result = await token_client.metadata.get_activity_types()

        # 5. Compare results
        assert token_result.totalResults == basic_result.totalResults
        assert len(token_result) == len(basic_result)
        assert {at.label for at in token_result} == {at.label for at in basic_result}


# endregion
