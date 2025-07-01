"""Validation tests for Core API models against response examples.

This module tests that Core API Pydantic models correctly parse real API responses
from the response_examples directory.
"""

import json
import pytest
from pathlib import Path

from ofsc.models.core import (
    Resource,
    User,
    ResourcePosition,
)


class TestCoreModelsValidation:
    """Test Core API model validation against real response examples."""
    
    @pytest.fixture
    def response_examples_path(self):
        """Path to response examples directory."""
        return Path(__file__).parent.parent.parent / "response_examples"
    
    def test_resource_model_validation(self, response_examples_path):
        """Test Resource model against get_resources response."""
        response_file = response_examples_path / "163_get_resources.json"
        
        if not response_file.exists():
            pytest.skip("Resource response example not found")
        
        with open(response_file) as f:
            data = json.load(f)
        
        # Skip metadata
        if "_metadata" in data:
            del data["_metadata"]
        
        # Test individual resource items
        if "items" in data and data["items"]:
            for item in data["items"][:3]:  # Test first 3 items
                resource = Resource(**item)
                assert resource.resourceId is not None
                assert resource.name is not None
                assert resource.resourceType is not None
                
                # Test v3.0 enhanced fields
                if hasattr(resource, 'resourceInternalId'):
                    assert isinstance(resource.resourceInternalId, (int, type(None)))
                if hasattr(resource, 'timeZoneIANA'):
                    assert isinstance(resource.timeZoneIANA, (str, type(None)))
    
    def test_user_model_validation(self, response_examples_path):
        """Test User model against get_users response."""
        response_file = response_examples_path / "219_get_users.json"
        
        if not response_file.exists():
            pytest.skip("User response example not found")
        
        with open(response_file) as f:
            data = json.load(f)
        
        # Skip metadata
        if "_metadata" in data:
            del data["_metadata"]
        
        # Test individual user items
        if "items" in data and data["items"]:
            for item in data["items"][:3]:  # Test first 3 items
                user = User(**item)
                assert user.login is not None
                
                # Test v3.0 enhanced fields
                if hasattr(user, 'userType'):
                    assert isinstance(user.userType, (str, type(None)))
                if hasattr(user, 'timeZoneIANA'):
                    assert isinstance(user.timeZoneIANA, (str, type(None)))
    
    def test_resource_position_model_validation(self, response_examples_path):
        """Test ResourcePosition model against last known positions response."""
        response_file = response_examples_path / "214_get_last_known_positions_of_resources.json"
        
        if not response_file.exists():
            pytest.skip("Resource position response example not found")
        
        with open(response_file) as f:
            data = json.load(f)
        
        # Skip metadata
        if "_metadata" in data:
            del data["_metadata"]
        
        # Test individual position items
        if "items" in data and data["items"]:
            for item in data["items"][:3]:  # Test first 3 items
                position = ResourcePosition(**item)
                assert position.resourceId is not None
                
                # Should handle both error messages and actual positions
                if position.errorMessage:
                    assert isinstance(position.errorMessage, str)
                else:
                    # Should have coordinate data if no error
                    assert position.latitude is not None or position.longitude is not None
    
    def test_base_ofs_response_integration(self, response_examples_path):
        """Test that Core models properly inherit BaseOFSResponse functionality."""
        response_file = response_examples_path / "163_get_resources.json"
        
        if not response_file.exists():
            pytest.skip("Resource response example not found")
        
        with open(response_file) as f:
            data = json.load(f)
        
        # Test that Resource can be created with from_response if we had httpx response
        if "items" in data and data["items"]:
            item = data["items"][0]
            resource = Resource(**item)
            
            # Should have BaseOFSResponse attributes
            assert hasattr(resource, '_raw_response')
            assert hasattr(resource, 'status_code')
            assert hasattr(resource, 'headers')
            
            # These should be None when created directly (not from httpx response)
            assert resource.status_code is None
            assert resource.headers is None
    
    def test_model_extra_fields_handling(self, response_examples_path):
        """Test that models handle extra fields from API responses gracefully."""
        response_file = response_examples_path / "163_get_resources.json"
        
        if not response_file.exists():
            pytest.skip("Resource response example not found")
        
        with open(response_file) as f:
            data = json.load(f)
        
        if "items" in data and data["items"]:
            item = data["items"][0]
            
            # Add some extra fields that aren't in the model
            test_item = item.copy()
            test_item["extraField1"] = "test_value"
            test_item["customProperty"] = {"nested": "data"}
            
            # Should not raise an error due to extra="allow"
            resource = Resource(**test_item)
            assert resource.resourceId is not None
            
            # Extra fields should be accessible
            if hasattr(resource, 'extraField1'):
                assert resource.extraField1 == "test_value"