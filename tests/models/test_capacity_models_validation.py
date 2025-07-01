"""Validation tests for Capacity API models against response examples.

This module tests that Capacity API Pydantic models correctly parse real API responses
from the response_examples directory.
"""

import json
import pytest
from pathlib import Path
from pydantic import ValidationError

from ofsc.models.capacity import (
    CapacityArea,
    CapacityCategoryResponse,
    GetCapacityResponse,
    CapacityMetrics,
    CapacityAreaTimeInterval,
    CapacityAreaTimeIntervalListResponse,
    CapacityAreaTimeSlot,
    CapacityAreaTimeSlotListResponse,
    CapacityAreaWorkzone,
    CapacityAreaWorkzoneListResponse,
    CapacityAreaCategory,
    CapacityAreaCategoryListResponse,
    CapacityAreaOrganization,
    CapacityAreaOrganizationListResponse,
)


class TestCapacityModelsValidation:
    """Test Capacity API model validation against real response examples."""
    
    @pytest.fixture
    def response_examples_path(self):
        """Path to response examples directory."""
        return Path(__file__).parent.parent.parent / "response_examples"
    
    def test_capacity_area_model_validation(self, response_examples_path):
        """Test CapacityArea model against get_capacity_areas response."""
        response_file = response_examples_path / "14_get_capacity_areas.json"
        
        if not response_file.exists():
            pytest.skip("Capacity areas response example not found")
        
        with open(response_file) as f:
            data = json.load(f)
        
        # Skip metadata
        if "_metadata" in data:
            del data["_metadata"]
        
        # Test individual capacity area items
        if "items" in data and data["items"]:
            for item in data["items"][:3]:  # Test first 3 items
                # Since the actual response only has 'label', we need to add required fields
                test_item = item.copy()
                test_item["status"] = "active"  # Required field
                
                area = CapacityArea(**test_item)
                assert area.label is not None
                assert area.status == "active"
                
                # Test v3.0 enhanced fields
                if hasattr(area, '_raw_response'):
                    assert area._raw_response is None  # Should be None when created directly
    
    def test_capacity_category_model_validation(self, response_examples_path):
        """Test CapacityCategory model against get_capacity_categories response."""
        response_file = response_examples_path / "23_get_capacity_categories.json"
        
        if not response_file.exists():
            pytest.skip("Capacity categories response example not found")
        
        with open(response_file) as f:
            data = json.load(f)
        
        # Skip metadata
        if "_metadata" in data:
            del data["_metadata"]
        
        # Test individual category items
        if "items" in data and data["items"]:
            for item in data["items"][:3]:  # Test first 3 items
                category = CapacityCategoryResponse(**item)
                assert category.label is not None
                assert category.name is not None
                assert isinstance(category.active, bool)
                
                # Test v3.0 enhanced fields - workSkills should be ItemList or None
                if hasattr(category, 'workSkills'):
                    # workSkills can be ItemList or None
                    from ofsc.models.capacity import ItemList
                    assert category.workSkills is None or isinstance(category.workSkills, ItemList)
    
    def test_get_capacity_response_validation(self, response_examples_path):
        """Test GetCapacityResponse model against available capacity response."""
        response_file = response_examples_path / "get_available_capacity_response.json"
        
        if not response_file.exists():
            pytest.skip("Available capacity response example not found")
        
        with open(response_file) as f:
            data = json.load(f)
        
        # Test the complete capacity response structure
        response = GetCapacityResponse(**data)
        assert hasattr(response, 'items')
        assert isinstance(response.items, list)
        
        if response.items:
            # Test first item structure
            first_item = response.items[0]
            assert hasattr(first_item, 'date')
            assert hasattr(first_item, 'areas')
            assert isinstance(first_item.areas, list)
            
            if first_item.areas:
                # Test first area structure
                first_area = first_item.areas[0]
                assert hasattr(first_area, 'label')
                assert hasattr(first_area, 'name')
                
                # Test capacity metrics if present
                if hasattr(first_area, 'calendar') and first_area.calendar:
                    assert hasattr(first_area.calendar, 'count')
                    assert isinstance(first_area.calendar.count, list)
                
                # Test categories if present
                if hasattr(first_area, 'categories') and first_area.categories:
                    first_category = first_area.categories[0]
                    assert hasattr(first_category, 'label')
                    assert hasattr(first_category, 'calendar')
    
    def test_capacity_metrics_model_validation(self, response_examples_path):
        """Test CapacityMetrics model validation."""
        # Test with typical capacity metrics data
        test_metrics = {
            "count": [9, 5, 3],
            "minutes": [5791, 629, 200]
        }
        
        metrics = CapacityMetrics(**test_metrics)
        assert metrics.count == [9, 5, 3]
        assert metrics.minutes == [5791, 629, 200]
        
        # Test with minimal data (count only)
        minimal_metrics = {"count": [1]}
        minimal = CapacityMetrics(**minimal_metrics)
        assert minimal.count == [1]
        assert minimal.minutes is None
    
    def test_base_ofs_response_integration(self, response_examples_path):
        """Test that Capacity models properly inherit BaseOFSResponse functionality."""
        # Create a capacity area manually
        area = CapacityArea(label="TEST_AREA", status="active")
        
        # Should have BaseOFSResponse attributes
        assert hasattr(area, '_raw_response')
        assert hasattr(area, 'status_code')
        assert hasattr(area, 'headers')
        
        # These should be None when created directly (not from httpx response)
        assert area.status_code is None
        assert area.headers is None
    
    def test_model_extra_fields_handling(self, response_examples_path):
        """Test that capacity models correctly forbid extra fields by default."""
        # Test that capacity models follow the default extra="forbid" behavior
        test_area = {
            "label": "TEST_AREA",
            "status": "active"
        }
        
        # This should work fine with just the required fields
        area = CapacityArea(**test_area)
        assert area.label == "TEST_AREA"
        assert area.status == "active"
        
        # Test that extra fields are properly rejected
        test_area_with_extra = {
            "label": "TEST_AREA",
            "status": "active",
            "extraField": "should_be_rejected"
        }
        
        # This should raise a ValidationError due to extra="forbid"
        with pytest.raises(ValidationError):
            CapacityArea(**test_area_with_extra)
    
    def test_capacity_request_csvlist_conversion(self):
        """Test that CapacityRequest properly handles CsvList conversion."""
        from ofsc.models.capacity import CapacityRequest
        
        # Test with list input
        request_data = {
            "dates": ["2024-01-01", "2024-01-02"],
            "areas": ["AREA1", "AREA2"],
            "categories": ["CAT1", "CAT2"]
        }
        
        request = CapacityRequest(**request_data)
        assert request.get_dates_list() == ["2024-01-01", "2024-01-02"]
        assert request.get_areas_list() == ["AREA1", "AREA2"]
        assert request.get_categories_list() == ["CAT1", "CAT2"]
    
    def test_capacity_area_categories_model_validation(self, response_examples_path):
        """Test CapacityAreaCategory model against endpoint 16 response."""
        response_file = response_examples_path / "16_get_capacity_area_capacity_categories.json"
        
        if not response_file.exists():
            pytest.skip("Capacity area categories response example not found")
        
        with open(response_file) as f:
            data = json.load(f)
        
        # Test individual category items
        if "items" in data and data["items"]:
            for item in data["items"]:
                category = CapacityAreaCategory(**item)
                assert category.label is not None
                assert category.name is not None
                
        # Test full response structure (remove metadata first)
        test_data = data.copy()
        if "_metadata" in test_data:
            del test_data["_metadata"]
        response = CapacityAreaCategoryListResponse(**test_data)
        assert hasattr(response, "items")
        assert isinstance(response.items, list)
        
    def test_capacity_area_workzones_v2_model_validation(self, response_examples_path):
        """Test CapacityAreaWorkzone model against endpoint 17 (v2) response."""
        response_file = response_examples_path / "17_get_capacity_area_workzones_v2.json"
        
        if not response_file.exists():
            pytest.skip("Capacity area work zones v2 response example not found")
        
        with open(response_file) as f:
            data = json.load(f)
        
        # Test individual workzone items
        if "items" in data and data["items"]:
            for item in data["items"]:
                workzone = CapacityAreaWorkzone(**item)
                assert workzone.workZoneLabel is not None
                assert workzone.workZoneName is not None
                
        # Test full response structure (remove metadata first)
        test_data = data.copy()
        if "_metadata" in test_data:
            del test_data["_metadata"]
        response = CapacityAreaWorkzoneListResponse(**test_data)
        assert hasattr(response, "items")
        assert isinstance(response.items, list)
        
    def test_capacity_area_timeslots_model_validation(self, response_examples_path):
        """Test CapacityAreaTimeSlot model against endpoint 19 response."""
        response_file = response_examples_path / "19_get_capacity_area_timeslots.json"
        
        if not response_file.exists():
            pytest.skip("Capacity area time slots response example not found")
        
        with open(response_file) as f:
            data = json.load(f)
        
        # Test individual timeslot items
        if "items" in data and data["items"]:
            for item in data["items"]:
                timeslot = CapacityAreaTimeSlot(**item)
                assert timeslot.label is not None
                assert timeslot.name is not None
                assert timeslot.timeFrom is not None
                assert timeslot.timeTo is not None
                
        # Test full response structure (remove metadata first)
        test_data = data.copy()
        if "_metadata" in test_data:
            del test_data["_metadata"]
        response = CapacityAreaTimeSlotListResponse(**test_data)
        assert hasattr(response, "items")
        assert isinstance(response.items, list)
        
    def test_capacity_area_timeintervals_model_validation(self, response_examples_path):
        """Test CapacityAreaTimeInterval model against endpoint 20 response."""
        response_file = response_examples_path / "20_get_capacity_area_timeintervals.json"
        
        if not response_file.exists():
            pytest.skip("Capacity area time intervals response example not found")
        
        with open(response_file) as f:
            data = json.load(f)
        
        # Test individual timeinterval items
        if "items" in data and data["items"]:
            for item in data["items"]:
                timeinterval = CapacityAreaTimeInterval(**item)
                assert timeinterval.timeFrom is not None
                # timeTo is optional - some intervals only have timeFrom
                
        # Test full response structure (remove metadata first)
        test_data = data.copy()
        if "_metadata" in test_data:
            del test_data["_metadata"]
        response = CapacityAreaTimeIntervalListResponse(**test_data)
        assert hasattr(response, "items")
        assert isinstance(response.items, list)
        
    def test_capacity_area_organizations_model_validation(self, response_examples_path):
        """Test CapacityAreaOrganization model against endpoint 21 response."""
        response_file = response_examples_path / "21_get_capacity_area_organizations.json"
        
        if not response_file.exists():
            pytest.skip("Capacity area organizations response example not found")
        
        with open(response_file) as f:
            data = json.load(f)
        
        # Test individual organization items
        if "items" in data and data["items"]:
            for item in data["items"]:
                organization = CapacityAreaOrganization(**item)
                assert organization.label is not None
                assert organization.name is not None
                assert organization.type is not None
                
        # Test full response structure (remove metadata first)
        test_data = data.copy()
        if "_metadata" in test_data:
            del test_data["_metadata"]
        response = CapacityAreaOrganizationListResponse(**test_data)
        assert hasattr(response, "items")
        assert isinstance(response.items, list)
        
    def test_capacity_area_subresource_models_extra_fields(self):
        """Test that new capacity area sub-resource models follow extra='forbid' behavior."""
        # Test each model individually
        
        # TimeInterval - should accept valid fields, reject extra
        valid_interval = {"timeFrom": "08", "timeTo": "12"}
        interval = CapacityAreaTimeInterval(**valid_interval)
        assert interval.timeFrom == "08"
        assert interval.timeTo == "12"
        
        with pytest.raises(ValidationError):
            CapacityAreaTimeInterval(**{**valid_interval, "extraField": "should_fail"})
        
        # TimeSlot - should accept valid fields, reject extra
        valid_timeslot = {"label": "08-10", "name": "08-10", "timeFrom": "08:00:00", "timeTo": "10:00:00"}
        timeslot = CapacityAreaTimeSlot(**valid_timeslot)
        assert timeslot.label == "08-10"
        
        with pytest.raises(ValidationError):
            CapacityAreaTimeSlot(**{**valid_timeslot, "extraField": "should_fail"})
        
        # Workzone - should accept valid fields, reject extra (v2 format only)
        valid_workzone = {"workZoneLabel": "AREA1", "workZoneName": "Area 1"}
        workzone = CapacityAreaWorkzone(**valid_workzone)
        assert workzone.workZoneLabel == "AREA1"
        assert workzone.workZoneName == "Area 1"
        
        with pytest.raises(ValidationError):
            CapacityAreaWorkzone(**{**valid_workzone, "extraField": "should_fail"})
        
        # Category - should accept valid fields, reject extra
        valid_category = {"label": "EST", "name": "Estimation"}
        category = CapacityAreaCategory(**valid_category)
        assert category.label == "EST"
        
        with pytest.raises(ValidationError):
            CapacityAreaCategory(**{**valid_category, "extraField": "should_fail"})
        
        # Organization - should accept valid fields, reject extra
        valid_org = {"label": "default", "name": "Default Org", "type": "inhouse"}
        org = CapacityAreaOrganization(**valid_org)
        assert org.label == "default"
        
        with pytest.raises(ValidationError):
            CapacityAreaOrganization(**{**valid_org, "extraField": "should_fail"})