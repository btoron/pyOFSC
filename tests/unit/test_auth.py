"""Tests for authentication functionality in OFSC v3.0."""

import os
import pytest
import base64
from unittest.mock import patch

# Import v3.0 modules using standard imports
from ofsc.auth import BasicAuth, OAuth2Auth, create_auth
from ofsc.client import OFSC
from ofsc.exceptions import OFSConfigurationException


class TestBasicAuth:
    """Test Basic Authentication functionality."""
    
    @pytest.mark.unit
    def test_basic_auth_creation(self, test_credentials):
        """Test BasicAuth instance creation."""
        auth = BasicAuth(
            instance=test_credentials["instance"],
            client_id=test_credentials["client_id"],
            client_secret=test_credentials["client_secret"]
        )
        
        assert auth.instance == test_credentials["instance"]
        assert auth.client_id == test_credentials["client_id"]
        assert auth.client_secret == test_credentials["client_secret"]
        assert auth.is_valid()
    
    @pytest.mark.unit
    def test_basic_auth_headers(self, test_credentials):
        """Test BasicAuth header generation."""
        auth = BasicAuth(
            instance=test_credentials["instance"],
            client_id=test_credentials["client_id"],
            client_secret=test_credentials["client_secret"]
        )
        
        headers = auth.get_headers()
        
        assert "Authorization" in headers
        assert headers["Authorization"].startswith("Basic ")
        assert "Content-Type" in headers
        assert headers["Content-Type"] == "application/json"
        
        # Verify the auth string format
        auth_string = headers["Authorization"].replace("Basic ", "")
        decoded = base64.b64decode(auth_string).decode('utf-8')
        expected = f"{test_credentials['client_id']}@{test_credentials['instance']}:{test_credentials['client_secret']}"
        assert decoded == expected
    
    @pytest.mark.unit
    def test_basic_auth_invalid_credentials(self):
        """Test BasicAuth with invalid credentials."""
        auth = BasicAuth(instance="test", client_id="", client_secret="secret")
        assert not auth.is_valid()
        
        auth = BasicAuth(instance="test", client_id="client", client_secret="")
        assert not auth.is_valid()


class TestOAuth2Auth:
    """Test OAuth2 Authentication functionality."""
    
    @pytest.mark.unit
    def test_oauth2_auth_creation(self, test_credentials):
        """Test OAuth2Auth instance creation."""
        with patch('httpx.Client'):
            auth = OAuth2Auth(
                instance=test_credentials["instance"],
                client_id=test_credentials["client_id"],
                client_secret=test_credentials["client_secret"]
            )
            
            assert auth.instance == test_credentials["instance"]
            assert auth.client_id == test_credentials["client_id"]
            assert auth.client_secret == test_credentials["client_secret"]
            assert auth.base_url == f"https://{test_credentials['instance']}.fs.ocs.oraclecloud.com"
    
    @pytest.mark.unit
    def test_oauth2_auth_custom_base_url(self, test_credentials):
        """Test OAuth2Auth with custom base URL."""
        custom_url = "https://custom.example.com"
        
        with patch('httpx.Client'):
            auth = OAuth2Auth(
                instance=test_credentials["instance"],
                client_id=test_credentials["client_id"],
                client_secret=test_credentials["client_secret"],
                base_url=custom_url
            )
            
            assert auth.base_url == custom_url


class TestAuthFactory:
    """Test authentication factory function."""
    
    @pytest.mark.unit
    def test_create_basic_auth(self, test_credentials):
        """Test creating BasicAuth via factory."""
        auth = create_auth(
            instance=test_credentials["instance"],
            client_id=test_credentials["client_id"],
            client_secret=test_credentials["client_secret"],
            use_oauth2=False
        )
        
        assert isinstance(auth, BasicAuth)
        assert auth.instance == test_credentials["instance"]
    
    @pytest.mark.unit
    def test_create_oauth2_auth(self, test_credentials):
        """Test creating OAuth2Auth via factory."""
        with patch('httpx.Client'):
            auth = create_auth(
                instance=test_credentials["instance"],
                client_id=test_credentials["client_id"],
                client_secret=test_credentials["client_secret"],
                use_oauth2=True
            )
            
            assert isinstance(auth, OAuth2Auth)
            assert auth.instance == test_credentials["instance"]


class TestClientAuthentication:
    """Test authentication integration with clients."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_async_client_basic_auth(self, test_credentials):
        """Test async client with Basic Auth."""
        async with OFSC(
            instance=test_credentials["instance"],
            client_id=test_credentials["client_id"],
            client_secret=test_credentials["client_secret"]
        ) as client:
            assert isinstance(client.auth, BasicAuth)
            assert client.auth.is_valid()
            
            headers = client.auth.get_headers()
            assert "Authorization" in headers
            assert headers["Authorization"].startswith("Basic ")
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_async_client_custom_auth(self, test_credentials, basic_auth):
        """Test async client with custom auth instance."""
        async with OFSC(
            instance="ignored",
            client_id="ignored", 
            client_secret="ignored",
            auth=basic_auth
        ) as client:
            assert client.auth is basic_auth


class TestEnvironmentVariables:
    """Test environment variable loading."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_env_var_loading(self, monkeypatch):
        """Test loading credentials from environment variables."""
        # Use monkeypatch for thread-safe environment variable testing
        monkeypatch.setenv('OFSC_INSTANCE', 'env_test_instance')
        monkeypatch.setenv('OFSC_CLIENT_ID', 'env_test_client')
        monkeypatch.setenv('OFSC_CLIENT_SECRET', 'env_test_secret')
        
        async with OFSC() as client:
            assert client.config.instance == 'env_test_instance'
            assert client.config.client_id == 'env_test_client'
            assert client.config.client_secret == 'env_test_secret'
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_explicit_params_override_env_vars(self, monkeypatch):
        """Test that explicit parameters override environment variables."""
        # Use monkeypatch for thread-safe environment variable testing
        monkeypatch.setenv('OFSC_INSTANCE', 'env_instance')
        monkeypatch.setenv('OFSC_CLIENT_ID', 'env_client')
        monkeypatch.setenv('OFSC_CLIENT_SECRET', 'env_secret')
        
        async with OFSC(
            instance="explicit_instance",
            client_id="explicit_client",
            client_secret="explicit_secret"
        ) as client:
            assert client.config.instance == 'explicit_instance'
            assert client.config.client_id == 'explicit_client'
            assert client.config.client_secret == 'explicit_secret'
    
    @pytest.mark.unit
    def test_missing_credentials_error(self, monkeypatch):
        """Test error when credentials are missing."""
        # Use monkeypatch to ensure clean environment for testing
        env_vars_to_clear = ['OFSC_INSTANCE', 'OFSC_CLIENT_ID', 'OFSC_CLIENT_SECRET']
        
        for var in env_vars_to_clear:
            monkeypatch.delenv(var, raising=False)
        
        with pytest.raises(OFSConfigurationException, match="instance must be provided"):
            OFSC()


class TestLiveAuthentication:
    """Live tests using real credentials from .env file."""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_live_basic_auth_async(self, live_async_client):
        """Test Basic Auth with live credentials (async)."""
        async with live_async_client as client:
            assert isinstance(client.auth, BasicAuth)
            assert client.auth.is_valid()
            
            # Test that we can get auth headers
            headers = client.auth.get_headers()
            assert "Authorization" in headers
            assert headers["Authorization"].startswith("Basic ")
            
            print(f"✅ Live async client authenticated to: {client.base_url}")
    
    @pytest.mark.integration
    def test_live_oauth2_auth_creation(self, live_credentials):
        """Test OAuth2Auth creation with live credentials (no token request)."""
        # Test creation without triggering token request
        with patch('httpx.Client'):
            auth = OAuth2Auth(
                instance=live_credentials["instance"],
                client_id=live_credentials["client_id"],
                client_secret=live_credentials["client_secret"]
            )
            
            assert auth.instance == live_credentials["instance"]
            assert auth.client_id == live_credentials["client_id"]
            assert auth.client_secret == live_credentials["client_secret"]
            
            expected_url = f"https://{live_credentials['instance']}.fs.ocs.oraclecloud.com"
            assert auth.base_url == expected_url
            
            print(f"✅ OAuth2Auth created for: {auth.base_url}")
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_live_env_var_loading(self, live_credentials):
        """Test loading live credentials from environment variables."""
        # This test verifies the .env file is properly configured
        async with OFSC() as client:
            assert client.config.instance == live_credentials["instance"]
            assert client.config.client_id == live_credentials["client_id"]
            assert client.config.client_secret == live_credentials["client_secret"]
            
            print(f"✅ Live env vars loaded: {client.config.instance}")
            print(f"✅ Client URL: {client.base_url}")