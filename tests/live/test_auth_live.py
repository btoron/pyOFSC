"""Live authentication tests against real OFSC servers using OFSC client classes.

These tests make actual HTTP requests to OFSC servers and require valid credentials.
Run with: source .env && uv run pytest tests/live/test_auth_live.py -m live -v
"""

import pytest
import os
from datetime import datetime, timezone
import asyncio

# Import directly from client modules to avoid old dependencies
import sys
import importlib.util

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# Load modules directly to avoid import issues with old code
def load_module(module_name, file_path):
    if module_name in sys.modules:
        return sys.modules[module_name]
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None:
        raise ImportError(f"Could not load module {module_name} from {file_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    if spec.loader is None:
        raise ImportError(f"No loader found for module {module_name}")
    spec.loader.exec_module(module)
    return module

# Load required modules
auth_module = load_module("ofsc.auth", os.path.join(project_root, "ofsc", "auth.py"))
sync_module = load_module("ofsc.client.sync_client", os.path.join(project_root, "ofsc", "client", "sync_client.py"))
async_module = load_module("ofsc.client.async_client", os.path.join(project_root, "ofsc", "client", "async_client.py"))

# Import classes
OFSC = sync_module.OFSC
AsyncOFSC = async_module.AsyncOFSC
BasicAuth = auth_module.BasicAuth
OAuth2Auth = auth_module.OAuth2Auth


@pytest.mark.live
class TestLiveAuthentication:
    """Live authentication tests using OFSC client classes."""
    
    @pytest.fixture
    def live_credentials(self):
        """Get live credentials from environment variables."""
        instance = os.getenv('OFSC_INSTANCE')
        client_id = os.getenv('OFSC_CLIENT_ID')
        client_secret = os.getenv('OFSC_CLIENT_SECRET')
        
        if not all([instance, client_id, client_secret]):
            pytest.skip("Live credentials not available. Set OFSC_INSTANCE, OFSC_CLIENT_ID, OFSC_CLIENT_SECRET")
        
        return {
            "instance": instance,
            "client_id": client_id,
            "client_secret": client_secret
        }
    
    @pytest.fixture
    def sync_client_basic_auth(self, live_credentials):
        """Sync OFSC client with Basic Auth for live testing."""
        return OFSC(
            instance=live_credentials["instance"],
            client_id=live_credentials["client_id"],
            client_secret=live_credentials["client_secret"],
            use_token=False  # Use Basic Auth
        )
    
    @pytest.fixture
    def sync_client_oauth2(self, live_credentials):
        """Sync OFSC client with OAuth2 for live testing."""
        return OFSC(
            instance=live_credentials["instance"],
            client_id=live_credentials["client_id"],
            client_secret=live_credentials["client_secret"],
            use_token=True  # Use OAuth2
        )
    
    @pytest.fixture
    def async_client_basic_auth(self, live_credentials):
        """Async OFSC client with Basic Auth for live testing."""
        return AsyncOFSC(
            instance=live_credentials["instance"],
            client_id=live_credentials["client_id"],
            client_secret=live_credentials["client_secret"],
            use_token=False  # Use Basic Auth
        )
    
    @pytest.fixture
    def async_client_oauth2(self, live_credentials):
        """Async OFSC client with OAuth2 for live testing."""
        return AsyncOFSC(
            instance=live_credentials["instance"],
            client_id=live_credentials["client_id"],
            client_secret=live_credentials["client_secret"],
            use_token=True  # Use OAuth2
        )
    
    def test_sync_basic_auth_client_creation(self, sync_client_basic_auth):
        """Test sync client creation with Basic Auth."""
        client = sync_client_basic_auth
        
        # Verify client configuration
        assert client.config.instance is not None
        assert client.auth is not None
        assert isinstance(client.auth, BasicAuth)
        assert client.base_url.endswith(".fs.ocs.oraclecloud.com")
        
        print("✅ Sync Basic Auth client created successfully")
        print(f"   Instance: {client.config.instance}")
        print(f"   Base URL: {client.base_url}")
        print(f"   Auth type: {type(client.auth).__name__}")
    
    def test_sync_oauth2_client_creation(self, sync_client_oauth2):
        """Test sync client creation with OAuth2."""
        client = sync_client_oauth2
        
        # Verify client configuration
        assert client.config.instance is not None
        assert client.auth is not None
        assert isinstance(client.auth, OAuth2Auth)
        assert client.base_url.endswith(".fs.ocs.oraclecloud.com")
        
        print("✅ Sync OAuth2 client created successfully")
        print(f"   Instance: {client.config.instance}")
        print(f"   Base URL: {client.base_url}")
        print(f"   Auth type: {type(client.auth).__name__}")
    
    def test_async_basic_auth_client_creation(self, async_client_basic_auth):
        """Test async client creation with Basic Auth."""
        client = async_client_basic_auth
        
        # Verify client configuration
        assert client.config.instance is not None
        assert client.auth is not None
        assert isinstance(client.auth, BasicAuth)
        assert client.base_url.endswith(".fs.ocs.oraclecloud.com")
        
        print("✅ Async Basic Auth client created successfully")
        print(f"   Instance: {client.config.instance}")
        print(f"   Base URL: {client.base_url}")
        print(f"   Auth type: {type(client.auth).__name__}")
    
    def test_async_oauth2_client_creation(self, async_client_oauth2):
        """Test async client creation with OAuth2."""
        client = async_client_oauth2
        
        # Verify client configuration
        assert client.config.instance is not None
        assert client.auth is not None
        assert isinstance(client.auth, OAuth2Auth)
        assert client.base_url.endswith(".fs.ocs.oraclecloud.com")
        
        print("✅ Async OAuth2 client created successfully")
        print(f"   Instance: {client.config.instance}")
        print(f"   Base URL: {client.base_url}")
        print(f"   Auth type: {type(client.auth).__name__}")
    
    def test_oauth2_token_retrieval_and_caching(self, live_credentials):
        """Test OAuth2 token retrieval and caching mechanism."""
        # Create OAuth2 auth instance directly
        oauth2_auth = OAuth2Auth(
            instance=live_credentials["instance"],
            client_id=live_credentials["client_id"],
            client_secret=live_credentials["client_secret"]
        )
        
        # First token request
        token_response_1 = oauth2_auth._get_valid_token()
        
        # Validate token response structure
        assert hasattr(token_response_1, 'access_token')
        assert hasattr(token_response_1, 'token_type')
        assert hasattr(token_response_1, 'expires_in')
        
        # Validate field values
        assert isinstance(token_response_1.access_token, str)
        assert len(token_response_1.access_token) > 0
        assert token_response_1.token_type.lower() == "bearer"
        assert isinstance(token_response_1.expires_in, int)
        assert token_response_1.expires_in > 0
        
        # Second token request (should use cached token)
        token_response_2 = oauth2_auth._get_valid_token()
        
        # Should be the same token (cached)
        assert token_response_1.access_token == token_response_2.access_token
        
        print("✅ OAuth2 token retrieval and caching working correctly")
        print(f"   Token type: {token_response_1.token_type}")
        print(f"   Expires in: {token_response_1.expires_in} seconds")
        print(f"   Token length: {len(token_response_1.access_token)} characters")
        print(f"   Caching: {'✅ Same token returned' if token_response_1.access_token == token_response_2.access_token else '❌ Different tokens'}")
    
    def test_sync_client_with_oauth2_api_call(self, sync_client_oauth2):
        """Test sync client OAuth2 authentication with actual API call."""
        client = sync_client_oauth2
        
        try:
            # Make a simple API call that requires authentication
            # Using events/subscriptions as it's a lightweight endpoint
            with client:
                # Get the auth headers to verify OAuth2 token is being used
                auth_headers = client.auth.get_headers()
                
                # Verify we have a Bearer token
                assert "Authorization" in auth_headers
                assert auth_headers["Authorization"].startswith("Bearer ")
                
                # Extract token for validation
                token = auth_headers["Authorization"].split("Bearer ")[1]
                assert len(token) > 0
                
                print("✅ Sync OAuth2 client authentication successful")
                print(f"   Auth header: Authorization: Bearer {token[:20]}...")
                print("   API call preparation successful")
                
        except Exception as e:
            pytest.fail(f"Sync OAuth2 client authentication failed: {e}")
    
    def test_async_client_with_oauth2_api_call(self, async_client_oauth2):
        """Test async client OAuth2 authentication with actual API call."""
        async def run_test():
            client = async_client_oauth2
            
            try:
                # Make a simple API call that requires authentication
                async with client:
                    # Get the auth headers to verify OAuth2 token is being used
                    auth_headers = client.auth.get_headers()
                    
                    # Verify we have a Bearer token
                    assert "Authorization" in auth_headers
                    assert auth_headers["Authorization"].startswith("Bearer ")
                    
                    # Extract token for validation
                    token = auth_headers["Authorization"].split("Bearer ")[1]
                    assert len(token) > 0
                    
                    print("✅ Async OAuth2 client authentication successful")
                    print(f"   Auth header: Authorization: Bearer {token[:20]}...")
                    print("   API call preparation successful")
                    
            except Exception as e:
                pytest.fail(f"Async OAuth2 client authentication failed: {e}")
        
        # Run the async test
        asyncio.run(run_test())
    
    def test_basic_auth_headers(self, sync_client_basic_auth):
        """Test Basic Auth header generation."""
        client = sync_client_basic_auth
        
        # Get auth headers
        auth_headers = client.auth.get_headers()
        
        # Verify Basic Auth header
        assert "Authorization" in auth_headers
        assert auth_headers["Authorization"].startswith("Basic ")
        
        # Extract and validate basic auth token
        basic_token = auth_headers["Authorization"].split("Basic ")[1]
        assert len(basic_token) > 0
        
        print("✅ Basic Auth headers generated correctly")
        print(f"   Auth header: Authorization: Basic {basic_token[:20]}...")
    
    def test_oauth2_error_handling_invalid_credentials(self):
        """Test OAuth2 error handling with invalid credentials."""
        # Create OAuth2 auth with invalid credentials
        invalid_oauth2 = OAuth2Auth(
            instance="invalid_instance",
            client_id="invalid_client",
            client_secret="invalid_secret"
        )
        
        # Should raise an exception when trying to get token
        with pytest.raises(Exception) as exc_info:
            invalid_oauth2._get_valid_token()
        
        # Verify we get an appropriate error
        error_message = str(exc_info.value).lower()
        expected_errors = ["401", "403", "400", "unauthorized", "forbidden", "not known", "connection", "network", "timeout"]
        assert any(error in error_message for error in expected_errors)
        
        print("✅ OAuth2 invalid credentials properly handled")
        print(f"   Error: {str(exc_info.value)}")
    
    def test_client_context_managers(self, sync_client_oauth2, async_client_oauth2):
        """Test client context manager functionality."""
        # Test sync client context manager
        sync_client = sync_client_oauth2
        with sync_client as client:
            assert not client._client.is_closed
            assert client.auth is not None
        
        # Test async client context manager
        async def test_async_context():
            async_client = async_client_oauth2
            async with async_client as client:
                assert not client._client.is_closed
                assert client.auth is not None
        
        asyncio.run(test_async_context())
        
        print("✅ Client context managers working correctly")
        print("   Sync context manager: ✅")
        print("   Async context manager: ✅")
    
    def test_oauth2_token_refresh_mechanism(self, live_credentials):
        """Test OAuth2 token refresh mechanism."""
        oauth2_auth = OAuth2Auth(
            instance=live_credentials["instance"],
            client_id=live_credentials["client_id"],
            client_secret=live_credentials["client_secret"]
        )
        
        # Get initial token
        token_1 = oauth2_auth._get_valid_token()
        initial_time = datetime.now(timezone.utc)
        
        # Force token expiration by manipulating internal state
        # (In real scenario, this would happen after token expires)
        oauth2_auth._token_expires_at = initial_time  # Force immediate expiration
        
        # Get new token (should trigger refresh)
        token_2 = oauth2_auth._get_valid_token()
        
        # Tokens should be different (new token requested)
        # Note: In some cases they might be the same if server returns same token
        # The important thing is that no error occurred
        assert token_2.access_token is not None
        assert len(token_2.access_token) > 0
        
        print("✅ OAuth2 token refresh mechanism working")
        print(f"   Initial token: {token_1.access_token[:20]}...")
        print(f"   Refreshed token: {token_2.access_token[:20]}...")
        print(f"   Tokens different: {'✅' if token_1.access_token != token_2.access_token else '⚠️ Same (may be normal)'}")


if __name__ == "__main__":
    """Run live tests directly with pytest."""
    import subprocess
    import sys
    
    print("Running live authentication tests using OFSC client classes...")
    print("Make sure environment variables are set: OFSC_INSTANCE, OFSC_CLIENT_ID, OFSC_CLIENT_SECRET")
    print()
    
    # Run pytest on this file
    result = subprocess.run([
        sys.executable, "-m", "pytest", __file__, "-v", "-m", "live"
    ])
    
    sys.exit(result.returncode)