"""Model validation tests for Core API responses."""

import json
from pathlib import Path
from typing import Dict, Any, List
import pytest

# Import existing models from v2 for now (will be replaced with v3 models in Phase 1.4)
try:
    # Try to import v2 models for validation
    import sys
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.insert(0, project_root)
    
    # Import base Pydantic BaseModel for validation
    from pydantic import BaseModel, ValidationError
    
except ImportError:
    pytest.skip("Core models not yet implemented", allow_module_level=True)


class ResourceModel(BaseModel):
    """Temporary model for resource validation."""
    resourceId: str
    organization: str
    email: str
    phone: str
    resourceInternalId: int
    status: str
    resourceType: str
    
    class Config:
        extra = "allow"  # Allow additional fields


class UserModel(BaseModel):
    """Temporary model for user validation."""
    login: str
    name: str
    email: str
    userType: str
    active: str
    
    class Config:
        extra = "allow"


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
                        resource = ResourceModel(**item)
                        assert resource.resourceId is not None
                        assert resource.status in ["active", "inactive", "suspended"]
                        print(f"✅ Validated resource: {resource.resourceId}")
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
                    user = UserModel(**item)
                    assert user.login is not None
                    assert user.active in ["true", "false", "1", "0"]
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
        """Ensure all response examples are valid JSON."""
        json_files = list(response_examples_path.glob("*.json"))
        
        for file_path in json_files:
            try:
                with open(file_path) as f:
                    json.load(f)
                print(f"✅ JSON parsing successful: {file_path.name}")
            except json.JSONDecodeError as e:
                pytest.fail(f"Invalid JSON in {file_path.name}: {e}")
    
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