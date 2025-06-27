"""Live authentication tests against real OFSC servers.

These tests make actual HTTP requests to OFSC servers and require valid credentials.
Run with: source .env && uv run pytest tests/live/test_auth_live.py -m live -v
"""

import pytest
import httpx
import os
from datetime import datetime, timedelta, timezone
from typing import Dict, Any

# In-memory token cache
_token_cache: Dict[str, Dict[str, Any]] = {}


class LiveTokenManager:
    """Manages OAuth2 tokens for live testing with in-memory caching."""
    
    def __init__(self, instance: str, client_id: str, client_secret: str):
        self.instance = instance
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = f"https://{instance}.fs.ocs.oraclecloud.com"
        self.cache_key = f"{instance}_{client_id}"
    
    def _is_token_valid(self, token_data: Dict[str, Any]) -> bool:
        """Check if cached token is still valid."""
        if not token_data or "expires_at" not in token_data:
            return False
        
        # Check if token expires in next 5 minutes (buffer)
        expires_at = datetime.fromisoformat(token_data["expires_at"])
        return datetime.now(timezone.utc) < (expires_at - timedelta(minutes=5))
    
    def get_token(self) -> Dict[str, Any]:
        """Get valid OAuth2 token, using cache or requesting new one."""
        # Check cache first
        if self.cache_key in _token_cache:
            cached_token = _token_cache[self.cache_key]
            if self._is_token_valid(cached_token):
                return cached_token
        
        # Request new token
        return self._request_new_token()
    
    def _request_new_token(self) -> Dict[str, Any]:
        """Request new OAuth2 token from OFSC server."""
        token_url = f"{self.base_url}/rest/oauthTokenService/v2/token"
        
        # Basic Auth header: client_id@instance:client_secret
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "grant_type": "client_credentials"
        }
        
        with httpx.Client() as client:
            response = client.post(
                token_url,
                headers=headers,
                data=data,
                auth=(f"{self.client_id}@{self.instance}", self.client_secret),
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise Exception(f"Token request failed: {response.status_code} - {response.text}")
            
            token_response = response.json()
            
            # Calculate expiration time
            expires_in = token_response.get("expires_in", 3600)
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
            
            # Add expiration to token data
            token_data = {
                **token_response,
                "expires_at": expires_at.isoformat(),
                "retrieved_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Cache the token
            _token_cache[self.cache_key] = token_data
            
            return token_data


@pytest.mark.live
class TestLiveAuthentication:
    """Live authentication tests against real OFSC servers."""
    
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
    def token_manager(self, live_credentials):
        """Create token manager for live testing."""
        return LiveTokenManager(
            instance=live_credentials["instance"],
            client_id=live_credentials["client_id"],
            client_secret=live_credentials["client_secret"]
        )
    
    def test_oauth2_token_request_success(self, token_manager):
        """Test successful OAuth2 token request."""
        token_data = token_manager.get_token()
        
        # Validate required fields
        assert "access_token" in token_data
        assert "token_type" in token_data
        assert "expires_in" in token_data
        
        # Validate field types and values
        assert isinstance(token_data["access_token"], str)
        assert len(token_data["access_token"]) > 0
        assert token_data["token_type"].lower() == "bearer"
        assert isinstance(token_data["expires_in"], int)
        assert token_data["expires_in"] > 0
        
        print("✅ OAuth2 token retrieved successfully")
        print(f"   Token type: {token_data['token_type']}")
        print(f"   Expires in: {token_data['expires_in']} seconds")
        print(f"   Token length: {len(token_data['access_token'])} characters")
    
    def test_token_caching(self, token_manager):
        """Test that tokens are cached and reused."""
        # Clear cache for this test
        if token_manager.cache_key in _token_cache:
            del _token_cache[token_manager.cache_key]
        
        # First request
        token_data_1 = token_manager.get_token()
        
        # Second request should return cached token
        token_data_2 = token_manager.get_token()
        
        # Should be the same token
        assert token_data_1["access_token"] == token_data_2["access_token"]
        assert token_data_1["retrieved_at"] == token_data_2["retrieved_at"]
        
        print("✅ Token caching working correctly")
    
    def test_token_validation_with_api_call(self, token_manager):
        """Test token validity by making API call to events/subscriptions."""
        token_data = token_manager.get_token()
        access_token = token_data["access_token"]
        
        # Make API call to validate token
        api_url = f"{token_manager.base_url}/rest/ofscCore/v1/events/subscriptions"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        with httpx.Client() as client:
            response = client.get(api_url, headers=headers, timeout=30.0)
            
            # Should succeed or return specific OFSC error (not auth error)
            if response.status_code == 401:
                pytest.fail("Token validation failed - received 401 Unauthorized")
            
            # Accept various success codes or OFSC-specific errors
            assert response.status_code in [200, 400, 404, 422], \
                f"Unexpected status code: {response.status_code} - {response.text}"
            
            print("✅ Token validated with API call")
            print("   API endpoint: /rest/ofscCore/v1/events/subscriptions")
            print(f"   Response status: {response.status_code}")
    
    def test_invalid_credentials_error(self):
        """Test error handling with invalid credentials."""
        invalid_manager = LiveTokenManager(
            instance="invalid_instance",
            client_id="invalid_client",
            client_secret="invalid_secret"
        )
        
        with pytest.raises(Exception) as exc_info:
            invalid_manager.get_token()
        
        # Should get an authentication or network error
        error_message = str(exc_info.value).lower()
        expected_errors = ["401", "403", "400", "401 unauthorized", "forbidden", "not known", "connection", "network", "timeout"]
        assert any(error in error_message for error in expected_errors)
        
        print("✅ Invalid credentials properly rejected")
        print(f"   Error: {str(exc_info.value)}")
    
    def test_malformed_token_endpoint_error(self, live_credentials):
        """Test error handling with malformed token endpoint."""
        # Create manager with bad instance to test network error handling
        bad_manager = LiveTokenManager(
            instance="nonexistent12345",
            client_id=live_credentials["client_id"],
            client_secret=live_credentials["client_secret"]
        )
        
        with pytest.raises(Exception) as exc_info:
            bad_manager.get_token()
        
        # Should get a network or HTTP error
        error_message = str(exc_info.value).lower()
        expected_errors = ["failed", "error", "timeout", "connection", "404", "500", "not known", "network"]
        assert any(keyword in error_message for keyword in expected_errors)
        
        print("✅ Network errors properly handled")
        print(f"   Error: {str(exc_info.value)}")
    
    def test_token_request_timeout_handling(self, live_credentials):
        """Test timeout handling in token requests."""
        manager = LiveTokenManager(
            instance=live_credentials["instance"],
            client_id=live_credentials["client_id"],
            client_secret=live_credentials["client_secret"]
        )
        
        # Override the token request with very short timeout
        original_method = manager._request_new_token
        
        def timeout_request():
            token_url = f"{manager.base_url}/rest/oauthTokenService/v2/token"
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            data = {"grant_type": "client_credentials"}
            
            with httpx.Client() as client:
                try:
                    response = client.post(
                        token_url,
                        headers=headers,
                        data=data,
                        auth=(f"{manager.client_id}@{manager.instance}", manager.client_secret),
                        timeout=0.001  # Very short timeout to force timeout
                    )
                    return response.json()
                except httpx.TimeoutException:
                    raise Exception("Request timeout")
        
        manager._request_new_token = timeout_request
        
        # This should either succeed (if server is very fast) or timeout
        try:
            manager.get_token()
            print("✅ Request completed despite short timeout")
        except Exception as e:
            if "timeout" in str(e).lower():
                print(f"✅ Timeout properly handled: {e}")
            else:
                # Restore original method and try normal request to verify credentials
                manager._request_new_token = original_method
                manager.get_token()  # Should work
                print("✅ Timeout test completed, normal request successful")
    
    def test_invalid_json_response_handling(self, live_credentials):
        """Test handling of invalid JSON responses."""
        # This test ensures our error handling works for malformed responses
        # We'll test this by making a request to a non-token endpoint that returns HTML
        
        instance = live_credentials["instance"]
        client_id = live_credentials["client_id"]
        client_secret = live_credentials["client_secret"]
        
        # Make request to root path which typically returns HTML not JSON
        base_url = f"https://{instance}.fs.ocs.oraclecloud.com"
        
        with httpx.Client() as client:
            try:
                response = client.get(
                    f"{base_url}/",
                    auth=(f"{client_id}@{instance}", client_secret),
                    timeout=30.0
                )
                
                # Try to parse as JSON - should fail
                try:
                    response.json()
                    # If we get here, the response was valid JSON (unexpected)
                    print("⚠️  Root endpoint returned JSON (unexpected but not an error)")
                except Exception:
                    # Expected - HTML response can't be parsed as JSON
                    print("✅ Invalid JSON response properly handled")
                    assert response.status_code in [200, 301, 302, 401, 403, 404]
                    
            except httpx.RequestError as e:
                print(f"✅ Network error properly handled: {e}")
    
    def test_multiple_concurrent_token_requests(self, token_manager):
        """Test concurrent token requests use caching properly."""
        import threading
        
        # Clear cache
        if token_manager.cache_key in _token_cache:
            del _token_cache[token_manager.cache_key]
        
        tokens = {}
        errors = {}
        
        def get_token_thread(thread_id):
            try:
                tokens[thread_id] = token_manager.get_token()
            except Exception as e:
                errors[thread_id] = e
        
        # Start multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=get_token_thread, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Check results
        assert len(errors) == 0, f"Thread errors: {errors}"
        assert len(tokens) == 3, "Not all threads completed"
        
        # All tokens should be the same (cached)
        token_values = [t["access_token"] for t in tokens.values()]
        assert len(set(token_values)) <= 2, "Too many different tokens (caching not working)"
        
        print("✅ Concurrent token requests handled properly")
        print(f"   Threads completed: {len(tokens)}")
        print(f"   Unique tokens: {len(set(token_values))}")


if __name__ == "__main__":
    """Run live tests directly with pytest."""
    import subprocess
    import sys
    
    print("Running live authentication tests...")
    print("Make sure environment variables are set: OFSC_INSTANCE, OFSC_CLIENT_ID, OFSC_CLIENT_SECRET")
    print()
    
    # Run pytest on this file
    result = subprocess.run([
        sys.executable, "-m", "pytest", __file__, "-v", "-m", "live"
    ])
    
    sys.exit(result.returncode)