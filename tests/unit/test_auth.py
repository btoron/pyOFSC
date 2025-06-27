"""Tests for authentication functionality in OFSC v3.0."""

import os
import pytest
import base64
from unittest.mock import Mock, patch
import httpx

# Import directly using sys.path manipulation to avoid old dependencies
import sys
import os
import importlib.util

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Load modules directly
def load_module(module_name, file_path):
    if module_name in sys.modules:
        return sys.modules[module_name]
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# Load required modules
auth_module = load_module("ofsc.auth", os.path.join(project_root, "ofsc", "auth.py"))
base_module = load_module("ofsc.client.base", os.path.join(project_root, "ofsc", "client", "base.py"))
sync_module = load_module("ofsc.client.sync_client", os.path.join(project_root, "ofsc", "client", "sync_client.py"))
async_module = load_module("ofsc.client.async_client", os.path.join(project_root, "ofsc", "client", "async_client.py"))

# Import classes
BasicAuth = auth_module.BasicAuth
OAuth2Auth = auth_module.OAuth2Auth
create_auth = auth_module.create_auth
AuthenticationError = auth_module.AuthenticationError
OFSC = sync_module.OFSC
AsyncOFSC = async_module.AsyncOFSC


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
    def test_sync_client_basic_auth(self, test_credentials):
        """Test sync client with Basic Auth."""
        with OFSC(
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
    def test_sync_client_custom_auth(self, test_credentials, basic_auth):
        """Test sync client with custom auth instance."""
        with OFSC(
            instance="ignored",
            client_id="ignored", 
            client_secret="ignored",
            auth=basic_auth
        ) as client:
            assert client.auth is basic_auth
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_async_client_basic_auth(self, test_credentials):
        """Test async client with Basic Auth."""
        async with AsyncOFSC(
            instance=test_credentials["instance"],
            client_id=test_credentials["client_id"],
            client_secret=test_credentials["client_secret"]
        ) as client:
            assert isinstance(client.auth, BasicAuth)
            assert client.auth.is_valid()
            
            headers = client.auth.get_headers()
            assert "Authorization" in headers
            assert headers["Authorization"].startswith("Basic ")


class TestEnvironmentVariables:
    """Test environment variable loading."""
    
    @pytest.mark.unit
    def test_env_var_loading(self):
        """Test loading credentials from environment variables."""
        test_env = {
            'OFSC_INSTANCE': 'env_test_instance',
            'OFSC_CLIENT_ID': 'env_test_client',
            'OFSC_CLIENT_SECRET': 'env_test_secret'
        }
        
        with patch.dict(os.environ, test_env):
            with OFSC() as client:
                assert client.config.instance == 'env_test_instance'
                assert client.config.client_id == 'env_test_client'
                assert client.config.client_secret == 'env_test_secret'
    
    @pytest.mark.unit
    def test_explicit_params_override_env_vars(self):
        """Test that explicit parameters override environment variables."""
        test_env = {
            'OFSC_INSTANCE': 'env_instance',
            'OFSC_CLIENT_ID': 'env_client',
            'OFSC_CLIENT_SECRET': 'env_secret'
        }
        
        with patch.dict(os.environ, test_env):
            with OFSC(
                instance="explicit_instance",
                client_id="explicit_client",
                client_secret="explicit_secret"
            ) as client:
                assert client.config.instance == 'explicit_instance'
                assert client.config.client_id == 'explicit_client'
                assert client.config.client_secret == 'explicit_secret'
    
    @pytest.mark.unit
    def test_missing_credentials_error(self):
        """Test error when credentials are missing."""
        # Clear relevant env vars
        env_vars_to_clear = ['OFSC_INSTANCE', 'OFSC_CLIENT_ID', 'OFSC_CLIENT_SECRET']
        
        with patch.dict(os.environ, {}, clear=False):
            # Remove the specific env vars we're testing
            for var in env_vars_to_clear:
                if var in os.environ:
                    del os.environ[var]
            
            with pytest.raises(ValueError, match="instance must be provided"):
                OFSC()


class TestLiveAuthentication:
    """Live tests using real credentials from .env file."""
    
    @pytest.mark.integration
    def test_live_basic_auth_sync(self, live_sync_client):
        """Test Basic Auth with live credentials (sync)."""
        with live_sync_client as client:
            assert isinstance(client.auth, BasicAuth)
            assert client.auth.is_valid()
            
            # Test that we can get auth headers
            headers = client.auth.get_headers()
            assert "Authorization" in headers
            assert headers["Authorization"].startswith("Basic ")
            
            print(f"✅ Live sync client authenticated to: {client.base_url}")
    
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
    def test_live_env_var_loading(self, live_credentials):
        """Test loading live credentials from environment variables."""
        # This test verifies the .env file is properly configured
        with OFSC() as client:
            assert client.config.instance == live_credentials["instance"]
            assert client.config.client_id == live_credentials["client_id"]
            assert client.config.client_secret == live_credentials["client_secret"]
            
            print(f"✅ Live env vars loaded: {client.config.instance}")
            print(f"✅ Client URL: {client.base_url}")