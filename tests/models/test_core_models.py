"""Model validation tests for Core API responses."""

import json
from pathlib import Path
import pytest
from pydantic import ValidationError

# Import the actual models
from ofsc.models.core import Resource, User


class TestCoreModels:
    """Test Core API model validation against response examples."""
    
    @pytest.fixture
    def response_examples_path(self):
        """Path to response examples directory."""
        return Path(__file__).parent.parent.parent / "response_examples"
    
    def test_resources_model_validation(self, response_examples_path):
        """Validate resource response examples against ResourceModel."""
        resource_files = [
            "163_get_resources.json",
            "214_get_last_known_positions_of_resources.json"
        ]
        
        for filename in resource_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                continue
                
            with open(file_path) as f:
                data = json.load(f)
            
            # Skip metadata
            if "_metadata" in data:
                del data["_metadata"]
            
            # Validate items if present
            if "items" in data and data["items"]:
                for item in data["items"][:3]:  # Test first 3 items
                    try:
                        # Skip position responses that don't have full resource data
                        if filename == "214_get_last_known_positions_of_resources.json":
                            # This file contains resource positions, not full resources
                            # Just check basic structure
                            assert "resourceId" in item
                            print(f"✅ Validated resource position for: {item.get('resourceId')}")
                            continue
                            
                        resource = Resource(**item)
                        # Resource model might not have resourceId as required field
                        assert resource.name is not None
                        assert resource.resourceType is not None
                        assert resource.status in ["active", "inactive", "suspended"]
                        print(f"✅ Validated resource: {resource.name}")
                    except ValidationError as e:
                        pytest.fail(f"Resource validation failed for {filename}: {e}")
    
    def test_users_model_validation(self, response_examples_path):
        """Validate user response examples against UserModel."""
        user_file = response_examples_path / "219_get_users.json"
        
        if not user_file.exists():
            pytest.skip("User response example not found")
        
        with open(user_file) as f:
            data = json.load(f)
        
        # Skip metadata
        if "_metadata" in data:
            del data["_metadata"]
        
        # Validate items if present
        if "items" in data and data["items"]:
            for item in data["items"][:3]:  # Test first 3 items
                try:
                    user = User(**item)
                    assert user.login is not None
                    # User model has 'status' field, not 'active'
                    if hasattr(user, 'status') and user.status is not None:
                        assert user.status in ["active", "inactive", "suspended"]
                    print(f"✅ Validated user: {user.login}")
                except ValidationError as e:
                    pytest.fail(f"User validation failed: {e}")
    
    def test_response_structure_validation(self, response_examples_path):
        """Validate that all core response examples have expected structure."""
        core_files = [
            "163_get_resources.json",
            "219_get_users.json",
            "214_get_last_known_positions_of_resources.json"
        ]
        
        for filename in core_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                continue
            
            with open(file_path) as f:
                data = json.load(f)
            
            # Validate metadata structure
            if "_metadata" in data:
                metadata = data["_metadata"]
                assert "endpoint_id" in metadata
                assert "path" in metadata
                assert "method" in metadata
                assert "status_code" in metadata
                print(f"✅ Metadata validation passed for {filename}")
            
            # Validate pagination structure if present
            if "items" in data:
                assert "totalResults" in data or "limit" in data
                assert isinstance(data["items"], list)
                print(f"✅ Pagination structure valid for {filename}")
    
    def test_json_parsing(self, response_examples_path):
        """Ensure core response examples are valid JSON."""
        core_files = [
            "163_get_resources.json",
            "219_get_users.json",
            "214_get_last_known_positions_of_resources.json"
        ]
        
        for filename in core_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                continue
                
            try:
                with open(file_path) as f:
                    json.load(f)
                print(f"✅ JSON parsing successful: {filename}")
            except json.JSONDecodeError as e:
                pytest.fail(f"Invalid JSON in {filename}: {e}")
    
    def test_response_examples_completeness(self, response_examples_path):
        """Check that key response examples exist for core endpoints."""
        required_examples = [
            "163_get_resources.json",  # Resources
            "219_get_users.json"       # Users
        ]
        
        for filename in required_examples:
            file_path = response_examples_path / filename
            assert file_path.exists(), f"Required response example missing: {filename}"
            
            # Check file is not empty
            assert file_path.stat().st_size > 0, f"Response example is empty: {filename}"
            print(f"✅ Required example exists: {filename}")