"""
Model validation tests for Capacity API responses.

This file contains comprehensive validation tests for all Capacity API models
against real API response examples.

Generated on: 2025-07-25 00:26:01 UTC
"""

import json
from pathlib import Path
import pytest
from pydantic import ValidationError

# Import the actual models
from ofsc.models.capacity import CapacityArea, CapacityAreaCategory, CapacityAreaCategoryListResponse, CapacityAreaListResponse, CapacityAreaOrganization, CapacityAreaOrganizationListResponse, CapacityAreaTimeInterval, CapacityAreaTimeIntervalListResponse, CapacityAreaTimeSlot, CapacityAreaTimeSlotListResponse, CapacityAreaWorkzone, CapacityAreaWorkzoneListResponse, CapacityCategoryListResponse, CapacityCategoryResponse

class TestCapacityModelsValidation:
    """Test Capacity API model validation against response examples."""
    
    @pytest.fixture
    def response_examples_path(self):
        """Path to response examples directory."""
        # Go up from tests/models/generated/ to project root, then to response_examples
        return Path(__file__).parent.parent.parent.parent / "response_examples"

    def test_capacity_area_list_response_validation(self, response_examples_path):
        """Validate CapacityAreaListResponse model against saved response examples.
        
        Tests against endpoints: #14
        """
        response_files = [
            "14_get_capacity_areas.json",
        ]
        
        for filename in response_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                pytest.skip(f"Response file not found: {filename}")
                continue
            
            with open(file_path) as f:
                data = json.load(f)
            
            # Remove metadata field
            if "_metadata" in data:
                del data["_metadata"]
            
            # Handle list responses
            if "items" in data and isinstance(data["items"], list):
                if True:
                    # Validate the entire list response
                    try:
                        model_instance = CapacityAreaListResponse(**data)
                        self._validate_capacity_area_list_response_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"CapacityAreaListResponse validation failed for {filename}: {e}")
                    
                    # Also validate individual items using the item model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = CapacityArea(**item)
                            print(f"✅ Validated {filename} item {idx} with CapacityArea")
                        except ValidationError as e:
                            pytest.fail(f"CapacityArea validation failed for {filename} item {idx}: {e}")
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = CapacityAreaListResponse(**item)
                            self._validate_capacity_area_list_response_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(f"CapacityAreaListResponse validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = CapacityAreaListResponse(**data)
                    self._validate_capacity_area_list_response_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"CapacityAreaListResponse validation failed for {filename}: {e}")
    
    def _validate_capacity_area_list_response_fields(self, model: CapacityAreaListResponse, original_data: dict):
        """Validate specific fields for CapacityAreaListResponse."""
        # Add model-specific field validations here
        # List response validations
        assert hasattr(model, 'items'), "List response should have 'items' field"
        assert hasattr(model, 'totalResults'), "List response should have 'totalResults' field"

    def test_capacity_area_validation(self, response_examples_path):
        """Validate CapacityArea model against saved response examples.
        
        Tests against endpoints: #15
        """
        response_files = [
            "15_get_capacityAreas_FLUSA_FLUSA.json",
        ]
        
        for filename in response_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                pytest.skip(f"Response file not found: {filename}")
                continue
            
            with open(file_path) as f:
                data = json.load(f)
            
            # Remove metadata field
            if "_metadata" in data:
                del data["_metadata"]
            
            # Handle list responses
            if "items" in data and isinstance(data["items"], list):
                if False:
                    # Validate the entire list response
                    try:
                        model_instance = CapacityArea(**data)
                        self._validate_capacity_area_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"CapacityArea validation failed for {filename}: {e}")
                    
                    # Also validate individual items using the item model
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = CapacityArea(**item)
                            self._validate_capacity_area_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(f"CapacityArea validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = CapacityArea(**data)
                    self._validate_capacity_area_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"CapacityArea validation failed for {filename}: {e}")
    
    def _validate_capacity_area_fields(self, model: CapacityArea, original_data: dict):
        """Validate specific fields for CapacityArea."""
        # Add model-specific field validations here
        if hasattr(model, 'type') and getattr(model, 'type') is not None:
            assert getattr(model, 'type') in ['group', 'area'], "Invalid enum value for type"

    def test_capacity_area_time_slot_list_response_validation(self, response_examples_path):
        """Validate CapacityAreaTimeSlotListResponse model against saved response examples.
        
        Tests against endpoints: #19
        """
        response_files = [
            "19_get_capacity_area_timeslots.json",
        ]
        
        for filename in response_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                pytest.skip(f"Response file not found: {filename}")
                continue
            
            with open(file_path) as f:
                data = json.load(f)
            
            # Remove metadata field
            if "_metadata" in data:
                del data["_metadata"]
            
            # Handle list responses
            if "items" in data and isinstance(data["items"], list):
                if True:
                    # Validate the entire list response
                    try:
                        model_instance = CapacityAreaTimeSlotListResponse(**data)
                        self._validate_capacity_area_time_slot_list_response_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"CapacityAreaTimeSlotListResponse validation failed for {filename}: {e}")
                    
                    # Also validate individual items using the item model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = CapacityAreaTimeSlot(**item)
                            print(f"✅ Validated {filename} item {idx} with CapacityAreaTimeSlot")
                        except ValidationError as e:
                            pytest.fail(f"CapacityAreaTimeSlot validation failed for {filename} item {idx}: {e}")
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = CapacityAreaTimeSlotListResponse(**item)
                            self._validate_capacity_area_time_slot_list_response_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(f"CapacityAreaTimeSlotListResponse validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = CapacityAreaTimeSlotListResponse(**data)
                    self._validate_capacity_area_time_slot_list_response_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"CapacityAreaTimeSlotListResponse validation failed for {filename}: {e}")
    
    def _validate_capacity_area_time_slot_list_response_fields(self, model: CapacityAreaTimeSlotListResponse, original_data: dict):
        """Validate specific fields for CapacityAreaTimeSlotListResponse."""
        # Add model-specific field validations here
        # List response validations
        assert hasattr(model, 'items'), "List response should have 'items' field"
        assert hasattr(model, 'totalResults'), "List response should have 'totalResults' field"

    def test_capacity_area_workzone_list_response_validation(self, response_examples_path):
        """Validate CapacityAreaWorkzoneListResponse model against saved response examples.
        
        Tests against endpoints: #17
        """
        response_files = [
            "17_get_capacity_area_workzones_v2.json",
        ]
        
        for filename in response_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                pytest.skip(f"Response file not found: {filename}")
                continue
            
            with open(file_path) as f:
                data = json.load(f)
            
            # Remove metadata field
            if "_metadata" in data:
                del data["_metadata"]
            
            # Handle list responses
            if "items" in data and isinstance(data["items"], list):
                if True:
                    # Validate the entire list response
                    try:
                        model_instance = CapacityAreaWorkzoneListResponse(**data)
                        self._validate_capacity_area_workzone_list_response_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"CapacityAreaWorkzoneListResponse validation failed for {filename}: {e}")
                    
                    # Also validate individual items using the item model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = CapacityAreaWorkzone(**item)
                            print(f"✅ Validated {filename} item {idx} with CapacityAreaWorkzone")
                        except ValidationError as e:
                            pytest.fail(f"CapacityAreaWorkzone validation failed for {filename} item {idx}: {e}")
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = CapacityAreaWorkzoneListResponse(**item)
                            self._validate_capacity_area_workzone_list_response_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(f"CapacityAreaWorkzoneListResponse validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = CapacityAreaWorkzoneListResponse(**data)
                    self._validate_capacity_area_workzone_list_response_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"CapacityAreaWorkzoneListResponse validation failed for {filename}: {e}")
    
    def _validate_capacity_area_workzone_list_response_fields(self, model: CapacityAreaWorkzoneListResponse, original_data: dict):
        """Validate specific fields for CapacityAreaWorkzoneListResponse."""
        # Add model-specific field validations here
        # List response validations
        assert hasattr(model, 'items'), "List response should have 'items' field"
        assert hasattr(model, 'totalResults'), "List response should have 'totalResults' field"

    def test_capacity_area_organization_list_response_validation(self, response_examples_path):
        """Validate CapacityAreaOrganizationListResponse model against saved response examples.
        
        Tests against endpoints: #21
        """
        response_files = [
            "21_get_capacity_area_organizations.json",
        ]
        
        for filename in response_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                pytest.skip(f"Response file not found: {filename}")
                continue
            
            with open(file_path) as f:
                data = json.load(f)
            
            # Remove metadata field
            if "_metadata" in data:
                del data["_metadata"]
            
            # Handle list responses
            if "items" in data and isinstance(data["items"], list):
                if True:
                    # Validate the entire list response
                    try:
                        model_instance = CapacityAreaOrganizationListResponse(**data)
                        self._validate_capacity_area_organization_list_response_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"CapacityAreaOrganizationListResponse validation failed for {filename}: {e}")
                    
                    # Also validate individual items using the item model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = CapacityAreaOrganization(**item)
                            print(f"✅ Validated {filename} item {idx} with CapacityAreaOrganization")
                        except ValidationError as e:
                            pytest.fail(f"CapacityAreaOrganization validation failed for {filename} item {idx}: {e}")
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = CapacityAreaOrganizationListResponse(**item)
                            self._validate_capacity_area_organization_list_response_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(f"CapacityAreaOrganizationListResponse validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = CapacityAreaOrganizationListResponse(**data)
                    self._validate_capacity_area_organization_list_response_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"CapacityAreaOrganizationListResponse validation failed for {filename}: {e}")
    
    def _validate_capacity_area_organization_list_response_fields(self, model: CapacityAreaOrganizationListResponse, original_data: dict):
        """Validate specific fields for CapacityAreaOrganizationListResponse."""
        # Add model-specific field validations here
        # List response validations
        assert hasattr(model, 'items'), "List response should have 'items' field"
        assert hasattr(model, 'totalResults'), "List response should have 'totalResults' field"

    def test_capacity_category_list_response_validation(self, response_examples_path):
        """Validate CapacityCategoryListResponse model against saved response examples.
        
        Tests against endpoints: #23
        """
        response_files = [
            "23_get_capacity_categories.json",
        ]
        
        for filename in response_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                pytest.skip(f"Response file not found: {filename}")
                continue
            
            with open(file_path) as f:
                data = json.load(f)
            
            # Remove metadata field
            if "_metadata" in data:
                del data["_metadata"]
            
            # Handle list responses
            if "items" in data and isinstance(data["items"], list):
                if True:
                    # Validate the entire list response
                    try:
                        model_instance = CapacityCategoryListResponse(**data)
                        self._validate_capacity_category_list_response_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"CapacityCategoryListResponse validation failed for {filename}: {e}")
                    
                    # Also validate individual items using the item model
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = CapacityCategoryListResponse(**item)
                            self._validate_capacity_category_list_response_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(f"CapacityCategoryListResponse validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = CapacityCategoryListResponse(**data)
                    self._validate_capacity_category_list_response_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"CapacityCategoryListResponse validation failed for {filename}: {e}")
    
    def _validate_capacity_category_list_response_fields(self, model: CapacityCategoryListResponse, original_data: dict):
        """Validate specific fields for CapacityCategoryListResponse."""
        # Add model-specific field validations here
        # List response validations
        assert hasattr(model, 'items'), "List response should have 'items' field"
        assert hasattr(model, 'totalResults'), "List response should have 'totalResults' field"

    def test_capacity_category_response_validation(self, response_examples_path):
        """Validate CapacityCategoryResponse model against saved response examples.
        
        Tests against endpoints: #24
        """
        response_files = [
            "24_get_capacityCategories_EST_EST.json",
        ]
        
        for filename in response_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                pytest.skip(f"Response file not found: {filename}")
                continue
            
            with open(file_path) as f:
                data = json.load(f)
            
            # Remove metadata field
            if "_metadata" in data:
                del data["_metadata"]
            
            # Handle list responses
            if "items" in data and isinstance(data["items"], list):
                if False:
                    # Validate the entire list response
                    try:
                        model_instance = CapacityCategoryResponse(**data)
                        self._validate_capacity_category_response_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"CapacityCategoryResponse validation failed for {filename}: {e}")
                    
                    # Also validate individual items using the item model
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = CapacityCategoryResponse(**item)
                            self._validate_capacity_category_response_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(f"CapacityCategoryResponse validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = CapacityCategoryResponse(**data)
                    self._validate_capacity_category_response_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"CapacityCategoryResponse validation failed for {filename}: {e}")
    
    def _validate_capacity_category_response_fields(self, model: CapacityCategoryResponse, original_data: dict):
        """Validate specific fields for CapacityCategoryResponse."""
        # Add model-specific field validations here
        pass  # Add specific field validations as needed

    def test_capacity_area_time_interval_list_response_validation(self, response_examples_path):
        """Validate CapacityAreaTimeIntervalListResponse model against saved response examples.
        
        Tests against endpoints: #20
        """
        response_files = [
            "20_get_capacity_area_timeintervals.json",
        ]
        
        for filename in response_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                pytest.skip(f"Response file not found: {filename}")
                continue
            
            with open(file_path) as f:
                data = json.load(f)
            
            # Remove metadata field
            if "_metadata" in data:
                del data["_metadata"]
            
            # Handle list responses
            if "items" in data and isinstance(data["items"], list):
                if True:
                    # Validate the entire list response
                    try:
                        model_instance = CapacityAreaTimeIntervalListResponse(**data)
                        self._validate_capacity_area_time_interval_list_response_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"CapacityAreaTimeIntervalListResponse validation failed for {filename}: {e}")
                    
                    # Also validate individual items using the item model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = CapacityAreaTimeInterval(**item)
                            print(f"✅ Validated {filename} item {idx} with CapacityAreaTimeInterval")
                        except ValidationError as e:
                            pytest.fail(f"CapacityAreaTimeInterval validation failed for {filename} item {idx}: {e}")
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = CapacityAreaTimeIntervalListResponse(**item)
                            self._validate_capacity_area_time_interval_list_response_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(f"CapacityAreaTimeIntervalListResponse validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = CapacityAreaTimeIntervalListResponse(**data)
                    self._validate_capacity_area_time_interval_list_response_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"CapacityAreaTimeIntervalListResponse validation failed for {filename}: {e}")
    
    def _validate_capacity_area_time_interval_list_response_fields(self, model: CapacityAreaTimeIntervalListResponse, original_data: dict):
        """Validate specific fields for CapacityAreaTimeIntervalListResponse."""
        # Add model-specific field validations here
        # List response validations
        assert hasattr(model, 'items'), "List response should have 'items' field"
        assert hasattr(model, 'totalResults'), "List response should have 'totalResults' field"

    def test_capacity_area_category_list_response_validation(self, response_examples_path):
        """Validate CapacityAreaCategoryListResponse model against saved response examples.
        
        Tests against endpoints: #16
        """
        response_files = [
            "16_get_capacity_area_capacity_categories.json",
        ]
        
        for filename in response_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                pytest.skip(f"Response file not found: {filename}")
                continue
            
            with open(file_path) as f:
                data = json.load(f)
            
            # Remove metadata field
            if "_metadata" in data:
                del data["_metadata"]
            
            # Handle list responses
            if "items" in data and isinstance(data["items"], list):
                if True:
                    # Validate the entire list response
                    try:
                        model_instance = CapacityAreaCategoryListResponse(**data)
                        self._validate_capacity_area_category_list_response_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"CapacityAreaCategoryListResponse validation failed for {filename}: {e}")
                    
                    # Also validate individual items using the item model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = CapacityAreaCategory(**item)
                            print(f"✅ Validated {filename} item {idx} with CapacityAreaCategory")
                        except ValidationError as e:
                            pytest.fail(f"CapacityAreaCategory validation failed for {filename} item {idx}: {e}")
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = CapacityAreaCategoryListResponse(**item)
                            self._validate_capacity_area_category_list_response_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(f"CapacityAreaCategoryListResponse validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = CapacityAreaCategoryListResponse(**data)
                    self._validate_capacity_area_category_list_response_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"CapacityAreaCategoryListResponse validation failed for {filename}: {e}")
    
    def _validate_capacity_area_category_list_response_fields(self, model: CapacityAreaCategoryListResponse, original_data: dict):
        """Validate specific fields for CapacityAreaCategoryListResponse."""
        # Add model-specific field validations here
        # List response validations
        assert hasattr(model, 'items'), "List response should have 'items' field"
        assert hasattr(model, 'totalResults'), "List response should have 'totalResults' field"
