"""Model validation tests for Capacity API responses."""

import json
from pathlib import Path
from typing import Dict, Any, List
import pytest
from pydantic import BaseModel, ValidationError


class CapacityAreaModel(BaseModel):
    """Temporary model for capacity area validation."""
    name: str
    status: str
    
    class Config:
        extra = "allow"


class CapacityCategoryModel(BaseModel):
    """Temporary model for capacity category validation."""
    name: str
    status: str
    timeSlotCapacity: bool
    
    class Config:
        extra = "allow"


class AvailableCapacityModel(BaseModel):
    """Temporary model for available capacity validation."""
    
    class Config:
        extra = "allow"


class TestCapacityModels:
    """Test Capacity API model validation against response examples."""
    
    @pytest.fixture
    def response_examples_path(self):
        """Path to response examples directory."""
        return Path(__file__).parent.parent.parent / "response_examples"
    
    def test_capacity_areas_model_validation(self, response_examples_path):
        """Validate capacity area response examples."""
        file_path = response_examples_path / "14_get_capacity_areas.json"
        
        if not file_path.exists():
            pytest.skip("Capacity areas response example not found")
        
        with open(file_path) as f:
            data = json.load(f)
        
        # Skip metadata
        if "_metadata" in data:
            del data["_metadata"]
        
        # Validate items if present
        if "items" in data and data["items"]:
            for item in data["items"][:3]:  # Test first 3 items
                try:
                    capacity_area = CapacityAreaModel(**item)
                    assert capacity_area.name is not None
                    assert capacity_area.status in ["active", "inactive"]
                    print(f"✅ Validated capacity area: {capacity_area.name}")
                except ValidationError as e:
                    pytest.fail(f"Capacity area validation failed: {e}")
    
    def test_capacity_categories_model_validation(self, response_examples_path):
        """Validate capacity category response examples."""
        file_path = response_examples_path / "23_get_capacity_categories.json"
        
        if not file_path.exists():
            pytest.skip("Capacity categories response example not found")
        
        with open(file_path) as f:
            data = json.load(f)
        
        # Skip metadata
        if "_metadata" in data:
            del data["_metadata"]
        
        # Validate items if present
        if "items" in data and data["items"]:
            for item in data["items"][:3]:  # Test first 3 items
                try:
                    capacity_category = CapacityCategoryModel(**item)
                    assert capacity_category.name is not None
                    assert capacity_category.status in ["active", "inactive"]
                    assert isinstance(capacity_category.timeSlotCapacity, bool)
                    print(f"✅ Validated capacity category: {capacity_category.name}")
                except ValidationError as e:
                    pytest.fail(f"Capacity category validation failed: {e}")
    
    def test_available_capacity_model_validation(self, response_examples_path):
        """Validate available capacity response examples."""
        file_path = response_examples_path / "get_available_capacity_response.json"
        
        if not file_path.exists():
            pytest.skip("Available capacity response example not found")
        
        with open(file_path) as f:
            data = json.load(f)
        
        # Skip metadata
        if "_metadata" in data:
            del data["_metadata"]
        
        # This is a complex nested structure, just validate it parses correctly
        try:
            capacity = AvailableCapacityModel(**data)
            print(f"✅ Available capacity model validation passed")
        except ValidationError as e:
            pytest.fail(f"Available capacity validation failed: {e}")
    
    def test_capacity_response_structure(self, response_examples_path):
        """Validate capacity response structure consistency."""
        capacity_files = [
            "14_get_capacity_areas.json",
            "23_get_capacity_categories.json",
            "get_available_capacity_response.json"
        ]
        
        for filename in capacity_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                continue
            
            with open(file_path) as f:
                data = json.load(f)
            
            # Check for metadata structure if present
            if "_metadata" in data:
                metadata = data["_metadata"]
                assert "endpoint_id" in metadata or "path" in metadata
                print(f"✅ Metadata structure valid for {filename}")
            
            # Check data structure
            if "items" in data:
                assert isinstance(data["items"], list)
                print(f"✅ List structure valid for {filename}")
            else:
                # Single object response
                assert isinstance(data, dict)
                print(f"✅ Object structure valid for {filename}")
    
    def test_capacity_examples_completeness(self, response_examples_path):
        """Check that key capacity response examples exist."""
        required_examples = [
            "14_get_capacity_areas.json",         # Capacity areas
            "23_get_capacity_categories.json"     # Capacity categories
        ]
        
        for filename in required_examples:
            file_path = response_examples_path / filename
            assert file_path.exists(), f"Required capacity example missing: {filename}"
            
            # Check file is not empty
            assert file_path.stat().st_size > 0, f"Capacity example is empty: {filename}"
            print(f"✅ Required capacity example exists: {filename}")
    
    def test_capacity_json_structure(self, response_examples_path):
        """Test capacity-specific JSON structure requirements."""
        capacity_files = list(response_examples_path.glob("*capacity*.json"))
        capacity_files.extend(list(response_examples_path.glob("14_*.json")))  # Capacity areas
        capacity_files.extend(list(response_examples_path.glob("23_*.json")))  # Capacity categories
        
        for file_path in capacity_files:
            try:
                with open(file_path) as f:
                    data = json.load(f)
                
                # Capacity responses should have either items array or be single objects
                assert "items" in data or isinstance(data, dict)
                print(f"✅ Capacity structure valid: {file_path.name}")
                
            except json.JSONDecodeError as e:
                pytest.fail(f"Invalid JSON in capacity file {file_path.name}: {e}")
            except AssertionError:
                pytest.fail(f"Invalid capacity structure in {file_path.name}")