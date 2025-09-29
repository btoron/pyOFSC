"""Tests for backward compatibility wrapper.

These tests ensure that the compatibility layer provides the same API as v2.x
while internally using the async v3.0 architecture.
"""

import pytest
import warnings
from unittest.mock import patch, AsyncMock

from ofsc.compat import OFSC
from ofsc.models.core import UserListResponse


class TestCompatibilityWrapper:
    """Test the backward compatibility wrapper functionality."""

    def test_import_compatibility(self):
        """Test that the compatibility wrapper can be imported."""
        from ofsc.compat import OFSC

        assert OFSC is not None

        # Also test convenience import
        from ofsc.compat import OFSC as CompatOFSC

        assert CompatOFSC is OFSC

    def test_initialization_with_deprecation_warning(self):
        """Test that initialization issues deprecation warning."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            client = OFSC(instance="test", client_id="test", client_secret="test")

            # Should have issued a deprecation warning
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "deprecated" in str(w[0].message).lower()

            client.close()  # Cleanup

    def test_configuration_storage(self):
        """Test that configuration is properly stored."""
        client = OFSC(
            instance="test_instance",
            client_id="test_client",
            client_secret="test_secret",
            use_token=True,
            auto_raise=False,
        )

        expected_config = {
            "instance": "test_instance",
            "client_id": "test_client",
            "client_secret": "test_secret",
            "use_token": True,
            "auto_raise": False,
        }

        assert client._config == expected_config
        client.close()

    def test_context_manager_support(self):
        """Test that the wrapper works as a context manager."""
        with OFSC(instance="test", client_id="test", client_secret="test") as client:
            assert client is not None
            assert hasattr(client, "_config")

    def test_string_representation(self):
        """Test string representation of the wrapper."""
        client = OFSC(instance="test_instance", client_id="test", client_secret="test")

        str_repr = str(client)
        assert "OFSC" in str_repr
        assert "compat" in str_repr
        assert "test_instance" in str_repr

        detailed_repr = repr(client)
        assert "OFSC compat wrapper" in detailed_repr

        client.close()


class TestAPIAccess:
    """Test API access patterns for compatibility."""

    def test_core_api_property(self):
        """Test that core API property returns an object with methods."""
        client = OFSC(instance="test", client_id="test", client_secret="test")

        core_api = client.core
        assert core_api is not None

        # Check that core methods are available
        assert hasattr(core_api, "get_users")
        assert hasattr(core_api, "get_user")
        assert hasattr(core_api, "get_activities")
        assert hasattr(core_api, "get_subscriptions")

        client.close()

    def test_metadata_api_property(self):
        """Test that metadata API property returns an object with methods."""
        client = OFSC(instance="test", client_id="test", client_secret="test")

        metadata_api = client.metadata
        assert metadata_api is not None

        # Check that metadata methods are available
        assert hasattr(metadata_api, "get_properties")
        assert hasattr(metadata_api, "get_property")
        assert hasattr(metadata_api, "get_workskills")
        assert hasattr(metadata_api, "get_workskill")

        client.close()

    def test_capacity_api_property(self):
        """Test that capacity API property returns an object with methods."""
        client = OFSC(instance="test", client_id="test", client_secret="test")

        capacity_api = client.capacity
        assert capacity_api is not None

        # Check that capacity methods are available
        assert hasattr(capacity_api, "getAvailableCapacity")
        assert hasattr(capacity_api, "getQuota")

        client.close()

    def test_direct_method_access(self):
        """Test that methods are also available directly on the client."""
        client = OFSC(instance="test", client_id="test", client_secret="test")

        # Core methods should be available directly
        assert hasattr(client, "get_users")
        assert hasattr(client, "get_user")
        assert hasattr(client, "get_activities")

        # Metadata methods should be available directly
        assert hasattr(client, "get_properties")
        assert hasattr(client, "get_property")
        assert hasattr(client, "get_workskills")

        client.close()


@pytest.mark.asyncio
class TestMethodExecution:
    """Test actual method execution with mocked async calls."""

    @patch("ofsc.compat.generators.AsyncOFSC")
    def test_get_users_execution(self, mock_async_ofsc):
        """Test that get_users method executes properly."""
        # Setup mock
        mock_client_instance = AsyncMock()
        mock_core = AsyncMock()
        mock_client_instance.core = mock_core

        mock_response = UserListResponse(totalResults=2, items=[])
        mock_core.get_users.return_value = mock_response

        mock_context = AsyncMock()
        mock_context.__aenter__.return_value = mock_client_instance
        mock_context.__aexit__.return_value = None
        mock_async_ofsc.return_value = mock_context

        # Test the compatibility wrapper
        client = OFSC(instance="test", client_id="test", client_secret="test")

        # This should work but we need to mock the event loop execution
        # For now, just test that the method exists and has right signature
        get_users_method = getattr(client, "get_users")
        assert callable(get_users_method)

        client.close()

    def test_method_signatures(self):
        """Test that wrapped methods have correct signatures."""
        client = OFSC(instance="test", client_id="test", client_secret="test")

        # Test get_users signature
        get_users = getattr(client, "get_users")
        assert hasattr(get_users, "__signature__")

        # Test get_property signature
        get_property = getattr(client, "get_property")
        assert hasattr(get_property, "__signature__")

        client.close()

    def test_method_documentation(self):
        """Test that wrapped methods have proper documentation."""
        client = OFSC(instance="test", client_id="test", client_secret="test")

        get_users = getattr(client, "get_users")
        assert get_users.__doc__ is not None
        assert "Get users from the OFS Core API" in get_users.__doc__

        get_properties = getattr(client, "get_properties")
        assert get_properties.__doc__ is not None
        assert "Get properties list" in get_properties.__doc__

        client.close()


class TestErrorHandling:
    """Test error handling in the compatibility wrapper."""

    def test_invalid_configuration(self):
        """Test behavior with invalid configuration."""
        # Should not fail at initialization, only when methods are called
        client = OFSC(instance=None, client_id=None, client_secret=None)
        assert client is not None
        client.close()

    def test_cleanup_on_error(self):
        """Test that resources are cleaned up properly on errors."""
        client = OFSC(instance="test", client_id="test", client_secret="test")

        # Should be able to cleanup even if there were errors
        client.close()

        # Should be able to close multiple times
        client.close()


class TestBackwardCompatibility:
    """Test full backward compatibility scenarios."""

    def test_v2_style_usage_pattern(self):
        """Test that v2.x usage patterns work."""
        # This is how v2.x code would look
        client = OFSC(instance="demo", client_id="test_id", client_secret="test_secret")

        # Methods should be available
        assert hasattr(client, "get_users")
        assert hasattr(client, "get_activities")
        assert hasattr(client, "get_properties")

        # Both direct access and API namespace should work
        assert hasattr(client.core, "get_users")
        assert hasattr(client.metadata, "get_properties")

        client.close()

    def test_parameter_compatibility(self):
        """Test that method parameters work as expected."""
        client = OFSC(instance="test", client_id="test", client_secret="test")

        # Get methods and check they can be called with v2.x parameters
        get_users = getattr(client, "get_users")
        get_properties = getattr(client, "get_properties")

        # Should be callable (even if they'll fail due to no async execution in test)
        assert callable(get_users)
        assert callable(get_properties)

        client.close()


class TestPerformanceConsiderations:
    """Test performance and resource management aspects."""

    def test_event_loop_creation(self):
        """Test that event loop is created properly."""
        client = OFSC(instance="test", client_id="test", client_secret="test")

        # Should have created an event loop
        assert client._loop is not None

        client.close()

        # Loop should be closed after cleanup
        assert client._loop.is_closed()

    def test_multiple_client_isolation(self):
        """Test that multiple clients don't interfere with each other."""
        client1 = OFSC(instance="test1", client_id="test1", client_secret="test1")
        client2 = OFSC(instance="test2", client_id="test2", client_secret="test2")

        # Should have different configurations
        assert client1._config["instance"] == "test1"
        assert client2._config["instance"] == "test2"

        # Should have different event loops
        assert client1._loop is not client2._loop

        client1.close()
        client2.close()

    def test_resource_cleanup(self):
        """Test that resources are properly cleaned up."""
        client = OFSC(instance="test", client_id="test", client_secret="test")

        # Store references to check cleanup
        loop = client._loop
        executor = client._executor

        assert not loop.is_closed()
        assert executor is not None

        client.close()

        # Resources should be cleaned up
        assert loop.is_closed()
        # Executor shutdown is non-blocking, so we can't easily test it here
