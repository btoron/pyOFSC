"""
Model validation tests for Metadata API responses.

This file contains comprehensive validation tests for all Metadata API models
against real API response examples.

Generated on: 2025-07-24 22:29:49 UTC
"""

import json
from pathlib import Path
import pytest
from pydantic import ValidationError

# Import the actual models

class TestMetadataModelsValidation:
    """Test Metadata API model validation against response examples."""
    
    @pytest.fixture
    def response_examples_path(self):
        """Path to response examples directory."""
        return Path(__file__).parent.parent.parent / "response_examples"

    def test_activity_type_group_validation(self, response_examples_path):
        """Validate ActivityTypeGroup model against saved response examples.
        
        Tests against endpoints: #1
        """
        response_files = [
            "1_get_activity_type_groups.json",
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
                # Validate first few items
                for idx, item in enumerate(data["items"][:3]):
                    try:
                        model_instance = ActivityTypeGroup(**item)
                        self._validate_activity_type_group_fields(model_instance, item)
                        print(f"✅ Validated {filename} item {idx}")
                    except ValidationError as e:
                        pytest.fail(f"ActivityTypeGroup validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = ActivityTypeGroup(**data)
                    self._validate_activity_type_group_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"ActivityTypeGroup validation failed for {filename}: {e}")
    
    def _validate_activity_type_group_fields(self, model: ActivityTypeGroup, original_data: dict):
        """Validate specific fields for ActivityTypeGroup."""
        # Add model-specific field validations here
        pass  # Add specific field validations as needed

    def test_activity_type_group_validation(self, response_examples_path):
        """Validate ActivityTypeGroup model against saved response examples.
        
        Tests against endpoints: #2
        """
        response_files = [
            "2_get_activityTypeGroups_customer_customer.json",
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
                # Validate first few items
                for idx, item in enumerate(data["items"][:3]):
                    try:
                        model_instance = ActivityTypeGroup(**item)
                        self._validate_activity_type_group_fields(model_instance, item)
                        print(f"✅ Validated {filename} item {idx}")
                    except ValidationError as e:
                        pytest.fail(f"ActivityTypeGroup validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = ActivityTypeGroup(**data)
                    self._validate_activity_type_group_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"ActivityTypeGroup validation failed for {filename}: {e}")
    
    def _validate_activity_type_group_fields(self, model: ActivityTypeGroup, original_data: dict):
        """Validate specific fields for ActivityTypeGroup."""
        # Add model-specific field validations here
        pass  # Add specific field validations as needed

    def test_activity_type_validation(self, response_examples_path):
        """Validate ActivityType model against saved response examples.
        
        Tests against endpoints: #4
        """
        response_files = [
            "4_get_activity_types.json",
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
                # Validate first few items
                for idx, item in enumerate(data["items"][:3]):
                    try:
                        model_instance = ActivityType(**item)
                        self._validate_activity_type_fields(model_instance, item)
                        print(f"✅ Validated {filename} item {idx}")
                    except ValidationError as e:
                        pytest.fail(f"ActivityType validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = ActivityType(**data)
                    self._validate_activity_type_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"ActivityType validation failed for {filename}: {e}")
    
    def _validate_activity_type_fields(self, model: ActivityType, original_data: dict):
        """Validate specific fields for ActivityType."""
        # Add model-specific field validations here
        pass  # Add specific field validations as needed

    def test_activity_type_validation(self, response_examples_path):
        """Validate ActivityType model against saved response examples.
        
        Tests against endpoints: #5
        """
        response_files = [
            "5_get_activityTypes_11_11.json",
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
                # Validate first few items
                for idx, item in enumerate(data["items"][:3]):
                    try:
                        model_instance = ActivityType(**item)
                        self._validate_activity_type_fields(model_instance, item)
                        print(f"✅ Validated {filename} item {idx}")
                    except ValidationError as e:
                        pytest.fail(f"ActivityType validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = ActivityType(**data)
                    self._validate_activity_type_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"ActivityType validation failed for {filename}: {e}")
    
    def _validate_activity_type_fields(self, model: ActivityType, original_data: dict):
        """Validate specific fields for ActivityType."""
        # Add model-specific field validations here
        assert hasattr(model, 'label'), "Missing required field: label"
        assert hasattr(model, 'name'), "Missing required field: name"
        assert hasattr(model, 'active'), "Missing required field: active"
        assert hasattr(model, 'translations'), "Missing required field: translations"
        assert hasattr(model, 'defaultDuration'), "Missing required field: defaultDuration"

    def test_application_validation(self, response_examples_path):
        """Validate Application model against saved response examples.
        
        Tests against endpoints: #7
        """
        response_files = [
            "7_get_applications.json",
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
                # Validate first few items
                for idx, item in enumerate(data["items"][:3]):
                    try:
                        model_instance = Application(**item)
                        self._validate_application_fields(model_instance, item)
                        print(f"✅ Validated {filename} item {idx}")
                    except ValidationError as e:
                        pytest.fail(f"Application validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = Application(**data)
                    self._validate_application_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"Application validation failed for {filename}: {e}")
    
    def _validate_application_fields(self, model: Application, original_data: dict):
        """Validate specific fields for Application."""
        # Add model-specific field validations here
        pass  # Add specific field validations as needed

    def test_application_validation(self, response_examples_path):
        """Validate Application model against saved response examples.
        
        Tests against endpoints: #8
        """
        response_files = [
            "8_get_applications_demoauth_demoauth.json",
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
                # Validate first few items
                for idx, item in enumerate(data["items"][:3]):
                    try:
                        model_instance = Application(**item)
                        self._validate_application_fields(model_instance, item)
                        print(f"✅ Validated {filename} item {idx}")
                    except ValidationError as e:
                        pytest.fail(f"Application validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = Application(**data)
                    self._validate_application_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"Application validation failed for {filename}: {e}")
    
    def _validate_application_fields(self, model: Application, original_data: dict):
        """Validate specific fields for Application."""
        # Add model-specific field validations here
        if hasattr(model, 'status') and getattr(model, 'status') is not None:
            assert getattr(model, 'status') in ['active', 'inactive'], "Invalid enum value for status"
        if hasattr(model, 'tokenService') and getattr(model, 'tokenService') is not None:
            assert getattr(model, 'tokenService') in ['ofsc', 'external', 'idcs'], "Invalid enum value for tokenService"

    def test_capacity_area_validation(self, response_examples_path):
        """Validate CapacityArea model against saved response examples.
        
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
                # Validate first few items
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
        pass  # Add specific field validations as needed

    def test_capacity_area_configuration_validation(self, response_examples_path):
        """Validate CapacityAreaConfiguration model against saved response examples.
        
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
                # Validate first few items
                for idx, item in enumerate(data["items"][:3]):
                    try:
                        model_instance = CapacityAreaConfiguration(**item)
                        self._validate_capacity_area_configuration_fields(model_instance, item)
                        print(f"✅ Validated {filename} item {idx}")
                    except ValidationError as e:
                        pytest.fail(f"CapacityAreaConfiguration validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = CapacityAreaConfiguration(**data)
                    self._validate_capacity_area_configuration_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"CapacityAreaConfiguration validation failed for {filename}: {e}")
    
    def _validate_capacity_area_configuration_fields(self, model: CapacityAreaConfiguration, original_data: dict):
        """Validate specific fields for CapacityAreaConfiguration."""
        # Add model-specific field validations here
        if hasattr(model, 'status') and getattr(model, 'status') is not None:
            assert getattr(model, 'status') in ['active', 'inactive'], "Invalid enum value for status"
        if hasattr(model, 'type') and getattr(model, 'type') is not None:
            assert getattr(model, 'type') in ['group', 'area'], "Invalid enum value for type"

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
                # Validate first few items
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
        assert hasattr(model, 'active'), "Missing required field: active"

    def test_form_validation(self, response_examples_path):
        """Validate Form model against saved response examples.
        
        Tests against endpoints: #27
        """
        response_files = [
            "27_get_forms.json",
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
                # Validate first few items
                for idx, item in enumerate(data["items"][:3]):
                    try:
                        model_instance = Form(**item)
                        self._validate_form_fields(model_instance, item)
                        print(f"✅ Validated {filename} item {idx}")
                    except ValidationError as e:
                        pytest.fail(f"Form validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = Form(**data)
                    self._validate_form_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"Form validation failed for {filename}: {e}")
    
    def _validate_form_fields(self, model: Form, original_data: dict):
        """Validate specific fields for Form."""
        # Add model-specific field validations here
        pass  # Add specific field validations as needed

    def test_inventory_type_validation(self, response_examples_path):
        """Validate InventoryType model against saved response examples.
        
        Tests against endpoints: #31
        """
        response_files = [
            "31_get_inventory_types.json",
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
                # Validate first few items
                for idx, item in enumerate(data["items"][:3]):
                    try:
                        model_instance = InventoryType(**item)
                        self._validate_inventory_type_fields(model_instance, item)
                        print(f"✅ Validated {filename} item {idx}")
                    except ValidationError as e:
                        pytest.fail(f"InventoryType validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = InventoryType(**data)
                    self._validate_inventory_type_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"InventoryType validation failed for {filename}: {e}")
    
    def _validate_inventory_type_fields(self, model: InventoryType, original_data: dict):
        """Validate specific fields for InventoryType."""
        # Add model-specific field validations here
        pass  # Add specific field validations as needed

    def test_inventory_type_validation(self, response_examples_path):
        """Validate InventoryType model against saved response examples.
        
        Tests against endpoints: #32
        """
        response_files = [
            "32_get_inventoryTypes_FIT5000_FIT5000.json",
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
                # Validate first few items
                for idx, item in enumerate(data["items"][:3]):
                    try:
                        model_instance = InventoryType(**item)
                        self._validate_inventory_type_fields(model_instance, item)
                        print(f"✅ Validated {filename} item {idx}")
                    except ValidationError as e:
                        pytest.fail(f"InventoryType validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = InventoryType(**data)
                    self._validate_inventory_type_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"InventoryType validation failed for {filename}: {e}")
    
    def _validate_inventory_type_fields(self, model: InventoryType, original_data: dict):
        """Validate specific fields for InventoryType."""
        # Add model-specific field validations here
        assert hasattr(model, 'label'), "Missing required field: label"
        assert hasattr(model, 'name'), "Missing required field: name"
        assert hasattr(model, 'active'), "Missing required field: active"
        assert hasattr(model, 'nonSerialized'), "Missing required field: nonSerialized"
        assert hasattr(model, 'translations'), "Missing required field: translations"

    def test_language_validation(self, response_examples_path):
        """Validate Language model against saved response examples.
        
        Tests against endpoints: #34
        """
        response_files = [
            "34_get_languages.json",
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
                # Validate first few items
                for idx, item in enumerate(data["items"][:3]):
                    try:
                        model_instance = Language(**item)
                        self._validate_language_fields(model_instance, item)
                        print(f"✅ Validated {filename} item {idx}")
                    except ValidationError as e:
                        pytest.fail(f"Language validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = Language(**data)
                    self._validate_language_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"Language validation failed for {filename}: {e}")
    
    def _validate_language_fields(self, model: Language, original_data: dict):
        """Validate specific fields for Language."""
        # Add model-specific field validations here
        pass  # Add specific field validations as needed

    def test_link_template_validation(self, response_examples_path):
        """Validate LinkTemplate model against saved response examples.
        
        Tests against endpoints: #35
        """
        response_files = [
            "35_get_link_templates.json",
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
                # Validate first few items
                for idx, item in enumerate(data["items"][:3]):
                    try:
                        model_instance = LinkTemplate(**item)
                        self._validate_link_template_fields(model_instance, item)
                        print(f"✅ Validated {filename} item {idx}")
                    except ValidationError as e:
                        pytest.fail(f"LinkTemplate validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = LinkTemplate(**data)
                    self._validate_link_template_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"LinkTemplate validation failed for {filename}: {e}")
    
    def _validate_link_template_fields(self, model: LinkTemplate, original_data: dict):
        """Validate specific fields for LinkTemplate."""
        # Add model-specific field validations here
        pass  # Add specific field validations as needed

    def test_link_template_validation(self, response_examples_path):
        """Validate LinkTemplate model against saved response examples.
        
        Tests against endpoints: #36
        """
        response_files = [
            "36_get_link_template.json",
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
                # Validate first few items
                for idx, item in enumerate(data["items"][:3]):
                    try:
                        model_instance = LinkTemplate(**item)
                        self._validate_link_template_fields(model_instance, item)
                        print(f"✅ Validated {filename} item {idx}")
                    except ValidationError as e:
                        pytest.fail(f"LinkTemplate validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = LinkTemplate(**data)
                    self._validate_link_template_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"LinkTemplate validation failed for {filename}: {e}")
    
    def _validate_link_template_fields(self, model: LinkTemplate, original_data: dict):
        """Validate specific fields for LinkTemplate."""
        # Add model-specific field validations here
        assert hasattr(model, 'label'), "Missing required field: label"
        assert hasattr(model, 'linkType'), "Missing required field: linkType"
        assert hasattr(model, 'active'), "Missing required field: active"
        assert hasattr(model, 'translations'), "Missing required field: translations"

    def test_non_working_reason_validation(self, response_examples_path):
        """Validate NonWorkingReason model against saved response examples.
        
        Tests against endpoints: #45
        """
        response_files = [
            "45_get_non_working_reasons.json",
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
                # Validate first few items
                for idx, item in enumerate(data["items"][:3]):
                    try:
                        model_instance = NonWorkingReason(**item)
                        self._validate_non_working_reason_fields(model_instance, item)
                        print(f"✅ Validated {filename} item {idx}")
                    except ValidationError as e:
                        pytest.fail(f"NonWorkingReason validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = NonWorkingReason(**data)
                    self._validate_non_working_reason_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"NonWorkingReason validation failed for {filename}: {e}")
    
    def _validate_non_working_reason_fields(self, model: NonWorkingReason, original_data: dict):
        """Validate specific fields for NonWorkingReason."""
        # Add model-specific field validations here
        pass  # Add specific field validations as needed

    def test_organization_validation(self, response_examples_path):
        """Validate Organization model against saved response examples.
        
        Tests against endpoints: #46
        """
        response_files = [
            "46_get_organizations.json",
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
                # Validate first few items
                for idx, item in enumerate(data["items"][:3]):
                    try:
                        model_instance = Organization(**item)
                        self._validate_organization_fields(model_instance, item)
                        print(f"✅ Validated {filename} item {idx}")
                    except ValidationError as e:
                        pytest.fail(f"Organization validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = Organization(**data)
                    self._validate_organization_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"Organization validation failed for {filename}: {e}")
    
    def _validate_organization_fields(self, model: Organization, original_data: dict):
        """Validate specific fields for Organization."""
        # Add model-specific field validations here
        pass  # Add specific field validations as needed

    def test_organization_validation(self, response_examples_path):
        """Validate Organization model against saved response examples.
        
        Tests against endpoints: #47
        """
        response_files = [
            "47_get_organizations_default_default.json",
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
                # Validate first few items
                for idx, item in enumerate(data["items"][:3]):
                    try:
                        model_instance = Organization(**item)
                        self._validate_organization_fields(model_instance, item)
                        print(f"✅ Validated {filename} item {idx}")
                    except ValidationError as e:
                        pytest.fail(f"Organization validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = Organization(**data)
                    self._validate_organization_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"Organization validation failed for {filename}: {e}")
    
    def _validate_organization_fields(self, model: Organization, original_data: dict):
        """Validate specific fields for Organization."""
        # Add model-specific field validations here
        assert hasattr(model, 'label'), "Missing required field: label"
        assert hasattr(model, 'type'), "Missing required field: type"
        assert hasattr(model, 'translations'), "Missing required field: translations"
        if hasattr(model, 'type') and getattr(model, 'type') is not None:
            assert getattr(model, 'type') in ['contractor', 'inhouse'], "Invalid enum value for type"

    def test_resource_type_validation(self, response_examples_path):
        """Validate ResourceType model against saved response examples.
        
        Tests against endpoints: #56
        """
        response_files = [
            "56_get_resource_types.json",
            "56_resource_types.json",
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
                # Validate first few items
                for idx, item in enumerate(data["items"][:3]):
                    try:
                        model_instance = ResourceType(**item)
                        self._validate_resource_type_fields(model_instance, item)
                        print(f"✅ Validated {filename} item {idx}")
                    except ValidationError as e:
                        pytest.fail(f"ResourceType validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = ResourceType(**data)
                    self._validate_resource_type_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"ResourceType validation failed for {filename}: {e}")
    
    def _validate_resource_type_fields(self, model: ResourceType, original_data: dict):
        """Validate specific fields for ResourceType."""
        # Add model-specific field validations here
        pass  # Add specific field validations as needed

    def test_shift_validation(self, response_examples_path):
        """Validate Shift model against saved response examples.
        
        Tests against endpoints: #63
        """
        response_files = [
            "63_get_shifts.json",
            "63_shifts.json",
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
                # Validate first few items
                for idx, item in enumerate(data["items"][:3]):
                    try:
                        model_instance = Shift(**item)
                        self._validate_shift_fields(model_instance, item)
                        print(f"✅ Validated {filename} item {idx}")
                    except ValidationError as e:
                        pytest.fail(f"Shift validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = Shift(**data)
                    self._validate_shift_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"Shift validation failed for {filename}: {e}")
    
    def _validate_shift_fields(self, model: Shift, original_data: dict):
        """Validate specific fields for Shift."""
        # Add model-specific field validations here
        pass  # Add specific field validations as needed

    def test_shift_validation(self, response_examples_path):
        """Validate Shift model against saved response examples.
        
        Tests against endpoints: #64
        """
        response_files = [
            "64_get_shift.json",
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
                # Validate first few items
                for idx, item in enumerate(data["items"][:3]):
                    try:
                        model_instance = Shift(**item)
                        self._validate_shift_fields(model_instance, item)
                        print(f"✅ Validated {filename} item {idx}")
                    except ValidationError as e:
                        pytest.fail(f"Shift validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = Shift(**data)
                    self._validate_shift_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"Shift validation failed for {filename}: {e}")
    
    def _validate_shift_fields(self, model: Shift, original_data: dict):
        """Validate specific fields for Shift."""
        # Add model-specific field validations here
        assert hasattr(model, 'name'), "Missing required field: name"
        assert hasattr(model, 'active'), "Missing required field: active"
        assert hasattr(model, 'type'), "Missing required field: type"
        assert hasattr(model, 'workTimeEnd'), "Missing required field: workTimeEnd"
        assert hasattr(model, 'workTimeStart'), "Missing required field: workTimeStart"

    def test_time_slot_validation(self, response_examples_path):
        """Validate TimeSlot model against saved response examples.
        
        Tests against endpoints: #67
        """
        response_files = [
            "67_get_time_slots.json",
            "67_timeslots.json",
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
                # Validate first few items
                for idx, item in enumerate(data["items"][:3]):
                    try:
                        model_instance = TimeSlot(**item)
                        self._validate_time_slot_fields(model_instance, item)
                        print(f"✅ Validated {filename} item {idx}")
                    except ValidationError as e:
                        pytest.fail(f"TimeSlot validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = TimeSlot(**data)
                    self._validate_time_slot_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"TimeSlot validation failed for {filename}: {e}")
    
    def _validate_time_slot_fields(self, model: TimeSlot, original_data: dict):
        """Validate specific fields for TimeSlot."""
        # Add model-specific field validations here
        pass  # Add specific field validations as needed

    def test_work_skill_group_validation(self, response_examples_path):
        """Validate WorkSkillGroup model against saved response examples.
        
        Tests against endpoints: #70
        """
        response_files = [
            "70_get_work_skill_groups.json",
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
                # Validate first few items
                for idx, item in enumerate(data["items"][:3]):
                    try:
                        model_instance = WorkSkillGroup(**item)
                        self._validate_work_skill_group_fields(model_instance, item)
                        print(f"✅ Validated {filename} item {idx}")
                    except ValidationError as e:
                        pytest.fail(f"WorkSkillGroup validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = WorkSkillGroup(**data)
                    self._validate_work_skill_group_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"WorkSkillGroup validation failed for {filename}: {e}")
    
    def _validate_work_skill_group_fields(self, model: WorkSkillGroup, original_data: dict):
        """Validate specific fields for WorkSkillGroup."""
        # Add model-specific field validations here
        pass  # Add specific field validations as needed

    def test_work_skill_group_validation(self, response_examples_path):
        """Validate WorkSkillGroup model against saved response examples.
        
        Tests against endpoints: #71
        """
        response_files = [
            "71_get_workSkillGroups_TEST_TEST.json",
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
                # Validate first few items
                for idx, item in enumerate(data["items"][:3]):
                    try:
                        model_instance = WorkSkillGroup(**item)
                        self._validate_work_skill_group_fields(model_instance, item)
                        print(f"✅ Validated {filename} item {idx}")
                    except ValidationError as e:
                        pytest.fail(f"WorkSkillGroup validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = WorkSkillGroup(**data)
                    self._validate_work_skill_group_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"WorkSkillGroup validation failed for {filename}: {e}")
    
    def _validate_work_skill_group_fields(self, model: WorkSkillGroup, original_data: dict):
        """Validate specific fields for WorkSkillGroup."""
        # Add model-specific field validations here
        assert hasattr(model, 'assignToResource'), "Missing required field: assignToResource"
        assert hasattr(model, 'addToCapacityCategory'), "Missing required field: addToCapacityCategory"
        assert hasattr(model, 'active'), "Missing required field: active"
        assert hasattr(model, 'translations'), "Missing required field: translations"
