"""Model validation tests for Metadata API responses."""

import json
from pathlib import Path
from typing import Dict, Any, List
import pytest
from pydantic import BaseModel, ValidationError


class PropertyModel(BaseModel):
    """Temporary model for property validation."""
    name: str
    type: str
    entity: str
    
    class Config:
        extra = "allow"


class WorkZoneModel(BaseModel):
    """Temporary model for work zone validation."""
    workZone: str
    workZoneName: str
    status: str
    
    class Config:
        extra = "allow"


class ActivityTypeModel(BaseModel):
    """Temporary model for activity type validation."""
    type: str
    label: str
    active: str
    
    class Config:
        extra = "allow"


class TestMetadataModels:
    """Test Metadata API model validation against response examples."""
    
    @pytest.fixture
    def response_examples_path(self):
        """Path to response examples directory."""
        return Path(__file__).parent.parent.parent / "response_examples"
    
    def test_properties_model_validation(self, response_examples_path):
        """Validate property response examples."""
        property_files = [
            "50_get_properties.json",
            "50_properties.json",
            "51_property.json"
        ]
        
        for filename in property_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                continue
                
            with open(file_path) as f:
                data = json.load(f)
            
            # Skip metadata
            if "_metadata" in data:
                del data["_metadata"]
            
            # Handle different response structures
            items_to_validate = []
            if "items" in data and data["items"]:
                items_to_validate = data["items"][:3]  # Test first 3
            elif isinstance(data, list):
                items_to_validate = data[:3]
            elif isinstance(data, dict) and "name" in data:
                items_to_validate = [data]  # Single property
            
            for item in items_to_validate:
                try:
                    prop = PropertyModel(**item)
                    assert prop.name is not None
                    assert prop.type in ["text", "number", "date", "time", "enum", "boolean"]
                    print(f"✅ Validated property: {prop.name}")
                except ValidationError as e:
                    pytest.fail(f"Property validation failed for {filename}: {e}")
    
    def test_work_zones_model_validation(self, response_examples_path):
        """Validate work zone response examples."""
        workzone_files = [
            "78_get_work_zones.json",
            "78_workzones.json",
            "86_get_the_work_zone_key.json",
            "86_workzone_keys.json"
        ]
        
        for filename in workzone_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                continue
                
            with open(file_path) as f:
                data = json.load(f)
            
            # Skip metadata
            if "_metadata" in data:
                del data["_metadata"]
            
            # Handle different response structures
            items_to_validate = []
            if "items" in data and data["items"]:
                items_to_validate = data["items"][:3]
            elif isinstance(data, list):
                items_to_validate = data[:3]
            
            for item in items_to_validate:
                try:
                    workzone = WorkZoneModel(**item)
                    assert workzone.workZone is not None
                    assert workzone.status in ["active", "inactive"]
                    print(f"✅ Validated work zone: {workzone.workZone}")
                except ValidationError as e:
                    pytest.fail(f"Work zone validation failed for {filename}: {e}")
    
    def test_activity_types_model_validation(self, response_examples_path):
        """Validate activity type response examples."""
        activity_type_files = [
            "4_get_activity_types.json",
            "1_get_activity_type_groups.json"
        ]
        
        for filename in activity_type_files:
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
                        activity_type = ActivityTypeModel(**item)
                        assert activity_type.type is not None
                        assert activity_type.active in ["true", "false", "1", "0"]
                        print(f"✅ Validated activity type: {activity_type.type}")
                    except ValidationError as e:
                        pytest.fail(f"Activity type validation failed for {filename}: {e}")
    
    def test_metadata_response_structure(self, response_examples_path):
        """Validate metadata response structure consistency."""
        metadata_files = [
            "4_get_activity_types.json",
            "50_get_properties.json", 
            "78_get_work_zones.json",
            "7_get_applications.json",
            "34_get_languages.json"
        ]
        
        for filename in metadata_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                continue
            
            with open(file_path) as f:
                data = json.load(f)
            
            # Check for consistent metadata structure
            if "_metadata" in data:
                metadata = data["_metadata"]
                assert "endpoint_id" in metadata
                assert "path" in metadata
                assert metadata["path"].startswith("/rest/ofscMetadata/")
                print(f"✅ Metadata structure valid for {filename}")
            
            # Check pagination if list response
            if "items" in data:
                assert isinstance(data["items"], list)
                print(f"✅ List structure valid for {filename}")
    
    def test_metadata_examples_completeness(self, response_examples_path):
        """Check that key metadata response examples exist."""
        required_examples = [
            "4_get_activity_types.json",   # Activity types
            "50_get_properties.json",      # Properties
            "78_get_work_zones.json",      # Work zones
            "74_get_work_skills.json"      # Work skills
        ]
        
        for filename in required_examples:
            file_path = response_examples_path / filename
            assert file_path.exists(), f"Required metadata example missing: {filename}"
            
            # Check file is not empty
            assert file_path.stat().st_size > 0, f"Metadata example is empty: {filename}"
            print(f"✅ Required metadata example exists: {filename}")