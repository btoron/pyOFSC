"""
Model validation tests for Capacity API responses.

This file contains comprehensive validation tests for all Capacity API models
against real API response examples.

Generated on: 2025-07-24 22:47:58 UTC
"""

import json
from pathlib import Path
import pytest
from pydantic import ValidationError

# Import the actual models
from ofsc.models.capacity import ActivityBookingOptionsResponse, CapacityArea, CapacityCategoryResponse

class TestCapacityModelsValidation:
    """Test Capacity API model validation against response examples."""
    
    @pytest.fixture
    def response_examples_path(self):
        """Path to response examples directory."""
        # Go up from tests/models/generated/ to project root, then to response_examples
        return Path(__file__).parent.parent.parent.parent / "response_examples"

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
                if "ListResponse" in "CapacityArea":
                    # Validate the entire list response
                    try:
                        model_instance = CapacityArea(**data)
                        self._validate_capacity_area_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"CapacityArea validation failed for {filename}: {e}")
                else:
                    # Validate individual items (for single model types)
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

    def test_activity_booking_options_response_validation(self, response_examples_path):
        """Validate ActivityBookingOptionsResponse model against saved response examples.
        
        Tests against endpoints: #232
        """
        response_files = [
            "232_get_rest_ofscCapacity_v1_activityBookingOptions.json",
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
                if "ListResponse" in "ActivityBookingOptionsResponse":
                    # Validate the entire list response
                    try:
                        model_instance = ActivityBookingOptionsResponse(**data)
                        self._validate_activity_booking_options_response_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"ActivityBookingOptionsResponse validation failed for {filename}: {e}")
                else:
                    # Validate individual items (for single model types)
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = ActivityBookingOptionsResponse(**item)
                            self._validate_activity_booking_options_response_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(f"ActivityBookingOptionsResponse validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = ActivityBookingOptionsResponse(**data)
                    self._validate_activity_booking_options_response_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"ActivityBookingOptionsResponse validation failed for {filename}: {e}")
    
    def _validate_activity_booking_options_response_fields(self, model: ActivityBookingOptionsResponse, original_data: dict):
        """Validate specific fields for ActivityBookingOptionsResponse."""
        # Add model-specific field validations here
        pass  # Add specific field validations as needed

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
                if "ListResponse" in "CapacityCategoryResponse":
                    # Validate the entire list response
                    try:
                        model_instance = CapacityCategoryResponse(**data)
                        self._validate_capacity_category_response_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"CapacityCategoryResponse validation failed for {filename}: {e}")
                else:
                    # Validate individual items (for single model types)
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
