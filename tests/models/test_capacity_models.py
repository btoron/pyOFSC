"""Model validation tests for Capacity API responses."""

import json
from pathlib import Path
import pytest
from pydantic import ValidationError

# Import the actual models
from ofsc.models.capacity import (
    CapacityArea,
    CapacityAreaListResponse,
    CapacityCategoryResponse,
    CapacityCategoryListResponse,
    GetCapacityResponse,
    CapacityAreaCategoryListResponse,
    CapacityAreaWorkzoneListResponse,
    CapacityAreaTimeSlotListResponse,
    CapacityAreaTimeIntervalListResponse,
    CapacityAreaOrganizationListResponse,
)


class TestCapacityModels:
    """Test Capacity API model validation against response examples."""
    
    @pytest.fixture
    def response_examples_path(self):
        """Path to response examples directory."""
        return Path(__file__).parent.parent.parent / "response_examples"
    
    def test_capacity_area_list_model_validation(self, response_examples_path):
        """Test CapacityAreaListResponse model against real API response."""
        file_path = response_examples_path / "14_get_capacity_areas.json"
        
        if not file_path.exists():
            pytest.skip("Capacity areas response example not found")
        
        with open(file_path) as f:
            data = json.load(f)

        # Remove metadata for model validation
        if "_metadata" in data:
            del data["_metadata"]

        response = CapacityAreaListResponse.model_validate(data)
        
        # Validate structure
        assert response.items is not None
        assert len(response.items) == 8
        
        # Validate first item
        first_area = response.items[0]
        assert first_area.label == "Atlantic"
        
        # All areas should have labels
        for area in response.items:
            assert area.label is not None
            assert isinstance(area.label, str)
            print(f"✅ Validated capacity area: {area.label}")
    
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
                    capacity_category = CapacityCategoryResponse(**item)
                    assert capacity_category.label is not None  # CapacityCategoryResponse uses 'label', not 'name'
                    # CapacityCategoryResponse model has 'active' field instead of 'status'
                    assert isinstance(capacity_category.active, bool)
                    # timeSlotCapacity is not in the actual model, but timeSlots exists
                    if hasattr(capacity_category, 'timeSlots'):
                        # timeSlots can be ItemList or None
                        assert capacity_category.timeSlots is None or hasattr(capacity_category.timeSlots, '__iter__')
                    print(f"✅ Validated capacity category: {capacity_category.label}")
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
            capacity = GetCapacityResponse(**data)
            print("✅ Available capacity model validation passed")
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

    def test_capacity_area_sub_resources_validation(self, response_examples_path):
        """Test all capacity area sub-resource models."""
        test_cases = [
            ("16_get_capacity_area_capacity_categories.json", CapacityAreaCategoryListResponse, "Categories"),
            ("17_get_capacity_area_workzones_v2.json", CapacityAreaWorkzoneListResponse, "Workzones"),
            ("19_get_capacity_area_timeslots.json", CapacityAreaTimeSlotListResponse, "Time Slots"),
            ("20_get_capacity_area_timeintervals.json", CapacityAreaTimeIntervalListResponse, "Time Intervals"),
            ("21_get_capacity_area_organizations.json", CapacityAreaOrganizationListResponse, "Organizations"),
        ]
        
        for filename, model_class, name in test_cases:
            file_path = response_examples_path / filename
            if not file_path.exists():
                pytest.skip(f"{name} response example not found: {filename}")
                continue
                
            with open(file_path) as f:
                data = json.load(f)
            
            # Remove metadata for model validation
            if "_metadata" in data:
                del data["_metadata"]
            
            try:
                response = model_class.model_validate(data)
                assert response.items is not None
                assert len(response.items) > 0
                print(f"✅ {name} validation successful ({len(response.items)} items)")
            except ValidationError as e:
                pytest.fail(f"{name} validation failed: {e}")

    def test_capacity_category_list_comprehensive(self, response_examples_path):
        """Comprehensive test of CapacityCategoryListResponse model."""
        file_path = response_examples_path / "23_get_capacity_categories.json"
        
        if not file_path.exists():
            pytest.skip("Capacity categories response example not found")
        
        with open(file_path) as f:
            data = json.load(f)

        # Remove metadata for model validation
        if "_metadata" in data:
            del data["_metadata"]

        response = CapacityCategoryListResponse.model_validate(data)
        
        # Validate pagination structure
        assert response.totalResults == 3
        assert response.limit == 100
        assert response.offset == 0
        assert response.hasMore is False
        
        # Validate first category in detail
        first_category = response.items[0]
        assert first_category.label == "EST"
        assert first_category.name == "Estimate"
        assert first_category.active is True
        
        # Validate translations
        assert first_category.translations is not None
        assert len(first_category.translations) == 2
        
        # Test translation access
        translation_map = first_category.translations.map()
        assert "en" in translation_map
        assert "fr" in translation_map
        assert translation_map["en"].name == "Estimate"
        assert translation_map["fr"].name == "Estimation"
        
        # Validate workSkills structure
        assert first_category.workSkills is not None
        assert len(first_category.workSkills) == 1
        first_skill = first_category.workSkills[0]
        assert first_skill.label == "EST"
        assert first_skill.ratio == 1
        
        # Validate timeSlots structure
        assert first_category.timeSlots is not None
        assert len(first_category.timeSlots) == 6
        time_slot_labels = {slot.label for slot in first_category.timeSlots}
        expected_slots = {"08-10", "10-12", "13-15", "15-17", "all-day", "17-23"}
        assert time_slot_labels == expected_slots

    def test_capacity_response_comprehensive(self, response_examples_path):
        """Comprehensive test of GetCapacityResponse model."""
        file_path = response_examples_path / "get_available_capacity_response.json"
        
        if not file_path.exists():
            pytest.skip("Available capacity response example not found")
        
        with open(file_path) as f:
            data = json.load(f)

        response = GetCapacityResponse.model_validate(data)
        
        # Validate top-level structure
        assert response.items is not None
        assert len(response.items) == 1
        
        # Validate date item structure
        date_item = response.items[0]
        assert date_item.date == "2025-06-25"
        assert len(date_item.areas) == 47
        
        # Validate first area in detail
        first_area = date_item.areas[0]
        assert first_area.label == "PETERBOROUCOP"
        assert first_area.name == "* Peterborough-IR"
        
        # Validate calendar metrics
        assert first_area.calendar is not None
        assert first_area.calendar.count == [9]
        assert first_area.calendar.minutes == [5791]
        
        # Validate available metrics
        assert first_area.available is not None
        assert first_area.available.count == [7]
        assert first_area.available.minutes == [629]
        
        # Validate categories structure
        assert len(first_area.categories) == 10
        first_category = first_area.categories[0]
        assert first_category.label == "F / RES / Install"
        
        # Validate category metrics
        assert first_category.calendar is not None
        assert first_category.calendar.count == [8]
        assert first_category.calendar.minutes == [5159]
        assert first_category.available is not None
        assert first_category.available.count == [7]
        assert first_category.available.minutes == [738]

    def test_base_response_features(self, response_examples_path):
        """Test that all capacity models inherit BaseOFSResponse features."""
        # Test with capacity area list
        file_path = response_examples_path / "14_get_capacity_areas.json"
        
        if not file_path.exists():
            pytest.skip("Capacity areas response example not found")
        
        with open(file_path) as f:
            data = json.load(f)
        if "_metadata" in data:
            del data["_metadata"]
        
        response = CapacityAreaListResponse.model_validate(data)
        
        # Test BaseOFSResponse features
        assert hasattr(response, 'raw_response')
        assert response.raw_response is None  # Not set in direct validation
        
        # Test links handling if present
        assert hasattr(response, 'links')
        if response.links:
            for link in response.links:
                assert hasattr(link, 'rel')
                assert hasattr(link, 'href')

    def test_model_serialization_roundtrip(self, response_examples_path):
        """Test that capacity models can be serialized and deserialized."""
        file_path = response_examples_path / "23_get_capacity_categories.json"
        
        if not file_path.exists():
            pytest.skip("Capacity categories response example not found")
        
        with open(file_path) as f:
            data = json.load(f)
        
        if "_metadata" in data:
            del data["_metadata"]
        
        # Test round-trip serialization
        response = CapacityCategoryListResponse.model_validate(data)
        serialized = response.model_dump()
        
        # Re-create from serialized data
        response2 = CapacityCategoryListResponse.model_validate(serialized)
        
        # Verify they're equivalent
        assert response.totalResults == response2.totalResults
        assert len(response.items) == len(response2.items)
        assert response.items[0].label == response2.items[0].label
        assert response.items[0].name == response2.items[0].name