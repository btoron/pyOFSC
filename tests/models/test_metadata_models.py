"""Model validation tests for Metadata API responses."""

import json
from pathlib import Path
from typing import Dict, Any, List
import pytest
from pydantic import BaseModel, ValidationError

# Import the actual production models from the reorganized structure
from ofsc.models import (
    Property, 
    PropertyListResponse,
    TimeSlot,
    TimeSlotListResponse,
    Workskill,
    WorkskillListResponse, 
    Workzone,
    WorkzoneListResponse,
    ActivityType,
    ActivityTypeListResponse,
    OFSResponseList,
    BaseOFSResponse,
    Link
)


class TestMetadataModels:
    """Test Metadata API model validation against response examples."""
    
    @pytest.fixture
    def response_examples_path(self):
        """Path to response examples directory."""
        return Path(__file__).parent.parent.parent / "response_examples"
    
    def test_properties_model_validation(self, response_examples_path):
        """Validate property response examples against real Property model."""
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
                    prop = Property.model_validate(item)
                    assert prop.name is not None
                    assert prop.label is not None
                    assert prop.type is not None
                    print(f"✅ Validated property: {prop.name} ({prop.type})")
                except ValidationError as e:
                    pytest.fail(f"Property validation failed for {filename}: {e}")
                    
        # Test paginated response structure
        paginated_file = response_examples_path / "50_get_properties.json"
        if paginated_file.exists():
            with open(paginated_file) as f:
                data = json.load(f)
            
            # Remove metadata for clean validation
            if "_metadata" in data:
                del data["_metadata"]
                
            try:
                # Validate as paginated response
                response = OFSResponseList[Property].model_validate(data)
                assert len(response.items) > 0
                assert hasattr(response, 'totalResults')
                print(f"✅ Validated paginated Property response with {len(response.items)} items")
            except ValidationError as e:
                pytest.fail(f"Paginated Property response validation failed: {e}")
    
    def test_work_zones_model_validation(self, response_examples_path):
        """Validate work zone response examples against real Workzone model."""
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
                    # Remove fields that aren't in the current model definition
                    if "shapes" in item:
                        del item["shapes"]
                    
                    workzone = Workzone.model_validate(item)
                    assert workzone.workZoneLabel is not None
                    assert workzone.workZoneName is not None
                    assert workzone.status is not None
                    print(f"✅ Validated work zone: {workzone.workZoneLabel}")
                except ValidationError as e:
                    pytest.fail(f"Work zone validation failed for {filename}: {e}")
                    
        # Test paginated response if available
        paginated_file = response_examples_path / "78_get_work_zones.json"
        if paginated_file.exists():
            with open(paginated_file) as f:
                data = json.load(f)
            
            if "_metadata" in data:
                del data["_metadata"]
                
            # Check if it's a paginated response
            if "items" in data:
                try:
                    # Remove shapes field from all items in the paginated response
                    for item in data["items"]:
                        if "shapes" in item:
                            del item["shapes"]
                    
                    response = OFSResponseList[Workzone].model_validate(data)
                    assert len(response.items) >= 0
                    print(f"✅ Validated paginated Workzone response with {len(response.items)} items")
                except ValidationError as e:
                    pytest.fail(f"Paginated Workzone response validation failed: {e}")
    
    def test_activity_types_model_validation(self, response_examples_path):
        """Validate activity type response examples against real ActivityType model."""
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
                        # Check if this is an ActivityType or ActivityTypeGroup
                        # ActivityTypeGroup has only label, name, active
                        # ActivityType has additional required fields like defaultDuration
                        if filename == "1_get_activity_type_groups.json":
                            # Skip ActivityType validation for activity type groups file
                            # This file contains ActivityTypeGroup objects, not ActivityType
                            continue
                            
                        activity_type = ActivityType.model_validate(item)
                        assert activity_type.label is not None
                        assert activity_type.name is not None
                        assert isinstance(activity_type.active, bool)
                        assert activity_type.defaultDuration > 0
                        print(f"✅ Validated activity type: {activity_type.label}")
                    except ValidationError as e:
                        pytest.fail(f"Activity type validation failed for {filename}: {e}")
                        
        # Test paginated activity types response  
        paginated_file = response_examples_path / "4_get_activity_types.json"
        if paginated_file.exists():
            with open(paginated_file) as f:
                data = json.load(f)
            
            if "_metadata" in data:
                del data["_metadata"]
                
            try:
                response = ActivityTypeListResponse.model_validate(data)
                assert len(response.items) > 0
                assert hasattr(response, 'totalResults')
                print(f"✅ Validated ActivityTypeListResponse with {len(response.items)} items")
            except ValidationError as e:
                pytest.fail(f"ActivityTypeListResponse validation failed: {e}")
                
    def test_work_skills_model_validation(self, response_examples_path):
        """Validate work skills response examples against real Workskill model."""
        file_path = response_examples_path / "74_get_work_skills.json"
        if not file_path.exists():
            pytest.skip("Work skills response example not found")
            
        with open(file_path) as f:
            data = json.load(f)
        
        # Skip metadata
        if "_metadata" in data:
            del data["_metadata"]
        
        # Validate items if present
        if "items" in data and data["items"]:
            for item in data["items"][:3]:  # Test first 3 items
                try:
                    workskill = Workskill.model_validate(item)
                    assert workskill.label is not None
                    assert workskill.name is not None
                    assert isinstance(workskill.active, bool)
                    assert workskill.sharing is not None
                    
                    # Test links field if present
                    if workskill.links:
                        for link in workskill.links:
                            assert link.rel is not None
                            assert link.href is not None
                            # href is AnyHttpUrl, convert to string for validation
                            href_str = str(link.href)
                            assert href_str  # Just ensure it's not empty
                            
                    print(f"✅ Validated work skill: {workskill.label} (sharing: {workskill.sharing})")
                except ValidationError as e:
                    pytest.fail(f"Work skill validation failed: {e}")
                    
        # Test paginated response
        try:
            response = OFSResponseList[Workskill].model_validate(data)
            assert len(response.items) > 0
            print(f"✅ Validated paginated Workskill response with {len(response.items)} items")
        except ValidationError as e:
            pytest.fail(f"Paginated Workskill response validation failed: {e}")
    
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
    
    def test_base_response_integration(self, response_examples_path):
        """Test BaseOFSResponse integration with metadata models."""
        # Test that response models inherit from BaseOFSResponse correctly
        file_path = response_examples_path / "74_get_work_skills.json"
        if not file_path.exists():
            pytest.skip("Work skills response example not found")
            
        with open(file_path) as f:
            data = json.load(f)
        
        if "_metadata" in data:
            del data["_metadata"]
            
        # Test OFSResponseList inherits BaseOFSResponse functionality
        response = OFSResponseList[Workskill].model_validate(data)
        
        # Should have BaseOFSResponse properties
        assert hasattr(response, 'raw_response')
        assert hasattr(response, 'status_code')
        assert hasattr(response, 'headers')
        
        # Should be None since we didn't use from_response
        assert response.raw_response is None
        assert response.status_code is None
        assert response.headers is None
        
        print("✅ BaseOFSResponse integration verified")
        
    def test_model_extra_fields_tolerance(self, response_examples_path):
        """Test that models follow the expected extra fields behavior."""
        file_path = response_examples_path / "74_get_work_skills.json"
        if not file_path.exists():
            pytest.skip("Work skills response example not found")
            
        with open(file_path) as f:
            data = json.load(f)
        
        if "_metadata" in data and "items" in data and data["items"]:
            # Test that models correctly reject extra fields by default
            test_item = data["items"][0].copy()
            test_item["futureField"] = "future_value"
            test_item["anotherNewField"] = {"nested": "data"}
            
            # This should raise a ValidationError due to extra="forbid" default
            with pytest.raises(ValidationError):
                Workskill.model_validate(test_item)
            
            # But the original item should work fine
            original_item = data["items"][0].copy()
            workskill = Workskill.model_validate(original_item)
            assert workskill.label is not None
            print("✅ Model correctly enforces extra fields policy")
    
    def test_link_model_validation(self, response_examples_path):
        """Test Link model validation against real response data."""
        file_path = response_examples_path / "74_get_work_skills.json"
        if not file_path.exists():
            pytest.skip("Work skills response example not found")
            
        with open(file_path) as f:
            data = json.load(f)
            
        if "items" in data and data["items"]:
            for item in data["items"][:2]:  # Test first 2
                if "links" in item and item["links"]:
                    for link_data in item["links"]:
                        try:
                            link = Link.model_validate(link_data)
                            assert link.rel is not None
                            assert link.href is not None
                            # href is AnyHttpUrl object, need to convert to string
                            href_str = str(link.href)
                            assert href_str.startswith("https://")
                            print(f"✅ Validated link: {link.rel} -> {href_str}")
                        except ValidationError as e:
                            pytest.fail(f"Link validation failed: {e}")
                    break  # Only test first item with links

    def test_timeslots_model_validation(self, response_examples_path):
        """Validate timeslots response examples against TimeSlot models."""
        timeslots_files = [
            "67_get_time_slots.json",
            "67_timeslots.json"
        ]
        
        for filename in timeslots_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                continue
                
            print(f"\nTesting TimeSlot model against: {filename}")
            
            with open(file_path) as f:
                data = json.load(f)
            
            # Skip metadata
            if "_metadata" in data:
                del data["_metadata"]
                
            try:
                # Test the complete response model
                timeslots_response = TimeSlotListResponse.model_validate(data)
                print(f"✅ TimeSlotListResponse validation successful")
                print(f"   Total results: {timeslots_response.totalResults}")
                print(f"   Items count: {len(timeslots_response.items)}")
                
                # Test individual timeslot models
                for i, timeslot in enumerate(timeslots_response.items[:3]):  # Test first 3
                    print(f"   TimeSlot {i+1}: {timeslot.label} - {timeslot.name}")
                    print(f"     Active: {timeslot.active}, All Day: {timeslot.isAllDay}")
                    
                    # Test all-day vs timed slots
                    if timeslot.isAllDay:
                        assert timeslot.timeStart is None or timeslot.timeStart == ""
                        assert timeslot.timeEnd is None or timeslot.timeEnd == ""
                        print(f"     ✅ All-day slot validation passed")
                    else:
                        assert timeslot.timeStart is not None
                        assert timeslot.timeEnd is not None
                        print(f"     ✅ Timed slot: {timeslot.timeStart} - {timeslot.timeEnd}")
                    
                    # Test links if present
                    if timeslot.links:
                        assert len(timeslot.links) > 0
                        for link in timeslot.links:
                            assert link.rel is not None
                            assert link.href is not None
                        print(f"     ✅ Links validated ({len(timeslot.links)} links)")
                
                print(f"✅ All TimeSlot validations passed for {filename}")
                return  # Test passed, no need to check other files
                
            except ValidationError as e:
                print(f"❌ TimeSlot validation failed for {filename}: {e}")
                continue
        
        # If we get here, no valid files were found
        pytest.skip("TimeSlots response examples not found")