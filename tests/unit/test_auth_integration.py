"""Integration tests for authentication components with v3.0 error handling."""

import pytest

from ofsc.auth import BasicAuth, OAuth2Auth
from ofsc.client import OFSC
from ofsc.exceptions import (
    OFSAuthenticationException,
    OFSConfigurationException,
    OFSConnectionException
)


class TestAuthenticationIntegration:
    """Test authentication integration with v3.0 clients and error handling."""
    
    def test_basic_auth_creation(self):
        """Test BasicAuth creation with valid parameters."""
        auth = BasicAuth(
            instance="test_instance",
            client_id="test_client",
            client_secret="test_secret"
        )
        
        assert auth.instance == "test_instance"
        assert auth.client_id == "test_client"
        assert auth.client_secret == "test_secret"
        
        # Test header generation
        headers = auth.get_headers()
        assert "Authorization" in headers
        assert headers["Authorization"].startswith("Basic ")
    
    def test_oauth2_auth_creation(self):
        """Test OAuth2Auth creation with valid parameters."""
        auth = OAuth2Auth(
            instance="test_instance",
            client_id="test_client",
            client_secret="test_secret"
        )
        
        assert auth.instance == "test_instance"
        assert auth.client_id == "test_client"
        assert auth.client_secret == "test_secret"
    
    def test_async_client_creation_with_basic_auth(self):
        """Test OFSC client creation with Basic Auth."""
        client = OFSC(
            instance="test_instance",
            client_id="test_client",
            client_secret="test_secret",
            use_token=False
        )
        
        assert client.config.instance == "test_instance"
        assert isinstance(client.auth, BasicAuth)
        assert client.base_url == "https://test_instance.fs.ocs.oraclecloud.com"
    
    def test_async_client_creation_with_oauth2(self):
        """Test OFSC client creation with OAuth2."""
        client = OFSC(
            instance="test_instance",
            client_id="test_client",
            client_secret="test_secret",
            use_token=True
        )
        
        assert client.config.instance == "test_instance"
        assert isinstance(client.auth, OAuth2Auth)
        assert client.base_url == "https://test_instance.fs.ocs.oraclecloud.com"
    
    def test_client_creation_missing_credentials(self):
        """Test client creation with missing credentials raises appropriate exception."""
        import os
        
        # Clear environment variables to ensure test isolation
        env_backup = {}
        for var in ['OFSC_INSTANCE', 'OFSC_CLIENT_ID', 'OFSC_CLIENT_SECRET']:
            env_backup[var] = os.environ.get(var)
            if var in os.environ:
                del os.environ[var]
        
        try:
            with pytest.raises(OFSConfigurationException, match="instance must be provided"):
                OFSC(client_id="test", client_secret="test")  # Missing instance
            
            with pytest.raises(OFSConfigurationException, match="client_id must be provided"):
                OFSC(instance="test", client_secret="test")  # Missing client_id
            
            with pytest.raises(OFSConfigurationException, match="client_secret must be provided"):
                OFSC(instance="test", client_id="test")  # Missing client_secret
        
        finally:
            # Restore environment variables
            for var, value in env_backup.items():
                if value is not None:
                    os.environ[var] = value
    
    def test_base_url_generation(self):
        """Test automatic base URL generation from instance name."""
        test_cases = [
            ("demo", "https://demo.fs.ocs.oraclecloud.com"),
            ("test123", "https://test123.fs.ocs.oraclecloud.com"),
            ("my-instance", "https://my-instance.fs.ocs.oraclecloud.com")
        ]
        
        for instance, expected_url in test_cases:
            client = OFSC(
                instance=instance,
                client_id="test",
                client_secret="test"
            )
            assert client.base_url == expected_url
    
    def test_fault_tolerance_configuration(self):
        """Test that fault tolerance is properly configured."""
        client = OFSC(
            instance="test",
            client_id="test",
            client_secret="test"
        )
        
        # Check that fault tolerance components are initialized
        assert hasattr(client, '_retry_config')
        assert hasattr(client, '_circuit_breaker_config')
        
        # Default configuration should enable fault tolerance
        connection_config = client._connection_config
        assert connection_config.enable_retries is True
        assert connection_config.enable_circuit_breaker is True
        assert connection_config.max_retry_attempts > 0
        assert connection_config.circuit_breaker_failure_threshold > 0
    
    def test_custom_fault_tolerance_configuration(self):
        """Test custom fault tolerance configuration."""
        from ofsc.client.base import ConnectionConfig
        
        custom_config = ConnectionConfig(
            enable_retries=False,
            enable_circuit_breaker=False,
            max_retry_attempts=1,
            circuit_breaker_failure_threshold=2
        )
        
        client = OFSC(
            instance="test",
            client_id="test",
            client_secret="test",
            connection_config=custom_config
        )
        
        assert client._connection_config.enable_retries is False
        assert client._connection_config.enable_circuit_breaker is False
        assert client._connection_config.max_retry_attempts == 1
        assert client._connection_config.circuit_breaker_failure_threshold == 2
    
    def test_oauth2_error_handling_with_new_exceptions(self):
        """Test OAuth2 error handling uses new exception hierarchy."""
        # Create OAuth2 auth with invalid instance to trigger connection error
        oauth2_auth = OAuth2Auth(
            instance="invalid-test-instance-nonexistent",
            client_id="invalid",
            client_secret="invalid"
        )
        
        # Should raise OFSConnectionException for connection errors
        with pytest.raises((OFSAuthenticationException, OFSConnectionException)) as exc_info:
            oauth2_auth._request_token()
        
        # Verify exception is from our hierarchy
        assert isinstance(exc_info.value, (OFSAuthenticationException, OFSConnectionException))
    
    def test_context_manager_support(self):
        """Test that clients work as context managers."""
        async_client = OFSC(
            instance="test",
            client_id="test",
            client_secret="test"
        )
        
        # Test async context manager
        async def test_async_context():
            async with async_client as client:
                assert client is async_client
                assert hasattr(client, '_client')
        
        import asyncio
        asyncio.run(test_async_context())
    
    def test_auth_headers_generation(self):
        """Test authentication header generation."""
        # Test Basic Auth
        basic_client = OFSC(
            instance="test",
            client_id="user",
            client_secret="pass",
            use_token=False
        )
        
        basic_headers = basic_client._get_auth_headers()
        assert "Authorization" in basic_headers
        assert basic_headers["Authorization"].startswith("Basic ")
        
        # Test OAuth2 (without making actual token request)
        oauth_client = OFSC(
            instance="test",
            client_id="user",
            client_secret="pass", 
            use_token=True
        )
        
        # OAuth2 headers would require a token, so just verify the auth type
        assert isinstance(oauth_client.auth, OAuth2Auth)
    
    def test_environment_variable_loading(self, monkeypatch):
        """Test loading credentials from environment variables."""
        # Use monkeypatch for thread-safe environment variable testing
        monkeypatch.setenv('OFSC_INSTANCE', 'env_test')
        monkeypatch.setenv('OFSC_CLIENT_ID', 'env_client')
        monkeypatch.setenv('OFSC_CLIENT_SECRET', 'env_secret')
        
        client = OFSC()  # No parameters, should load from env
        
        assert client.config.instance == 'env_test'
        assert client.auth.client_id == 'env_client'
        assert client.auth.client_secret == 'env_secret'
    
    def test_client_string_representation(self):
        """Test client string representation."""
        client = OFSC(
            instance="test_instance",
            client_id="test",
            client_secret="test"
        )
        
        client_str = str(client)
        assert "test_instance" in client_str
        assert "BaseOFSClient" in client_str or "OFSC" in client_str
        assert "https://test_instance.fs.ocs.oraclecloud.com" in client_str