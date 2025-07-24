"""
Model validation tests for Metadata API responses.

This file contains comprehensive validation tests for all Metadata API models
against real API response examples.

Generated on: 2025-07-24 22:47:58 UTC
"""

import json
from pathlib import Path
import pytest
from pydantic import ValidationError

# Import the actual models
from ofsc.models.metadata import ActivityType, ActivityTypeGroup, ActivityTypeGroupListResponse, ActivityTypeListResponse, Application, ApplicationApiAccess, ApplicationApiAccessListResponse, ApplicationListResponse, CapacityAreaCategoryListResponse, CapacityAreaListResponse, Form, FormListResponse, InventoryType, LinkTemplate, Organization, PropertyListResponse, PropertyResponse, ResourceTypeListResponse, RoutingPlanExportResponse, Shift, WorkSkillGroup, WorkZoneKeyResponse, Workskill, Workzone

class TestMetadataModelsValidation:
    """Test Metadata API model validation against response examples."""
    
    @pytest.fixture
    def response_examples_path(self):
        """Path to response examples directory."""
        # Go up from tests/models/generated/ to project root, then to response_examples
        return Path(__file__).parent.parent.parent.parent / "response_examples"

    def test_form_validation(self, response_examples_path):
        """Validate Form model against saved response examples.
        
        Tests against endpoints: #28
        """
        response_files = [
            "28_get_forms_mobile_provider_request%238%23_mobile_provider_request_8_.json",
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
                if "ListResponse" in "Form":
                    # Validate the entire list response
                    try:
                        model_instance = Form(**data)
                        self._validate_form_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"Form validation failed for {filename}: {e}")
                else:
                    # Validate individual items (for single model types)
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
        assert hasattr(model, 'label'), "Missing required field: label"
        assert hasattr(model, 'name'), "Missing required field: name"

    def test_application_list_response_validation(self, response_examples_path):
        """Validate ApplicationListResponse model against saved response examples.
        
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
                if "ListResponse" in "ApplicationListResponse":
                    # Validate the entire list response
                    try:
                        model_instance = ApplicationListResponse(**data)
                        self._validate_application_list_response_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"ApplicationListResponse validation failed for {filename}: {e}")
                else:
                    # Validate individual items (for single model types)
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = ApplicationListResponse(**item)
                            self._validate_application_list_response_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(f"ApplicationListResponse validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = ApplicationListResponse(**data)
                    self._validate_application_list_response_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"ApplicationListResponse validation failed for {filename}: {e}")
    
    def _validate_application_list_response_fields(self, model: ApplicationListResponse, original_data: dict):
        """Validate specific fields for ApplicationListResponse."""
        # Add model-specific field validations here
        # List response validations
        assert hasattr(model, 'items'), "List response should have 'items' field"
        assert hasattr(model, 'totalResults'), "List response should have 'totalResults' field"

    def test_activity_type_list_response_validation(self, response_examples_path):
        """Validate ActivityTypeListResponse model against saved response examples.
        
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
                if "ListResponse" in "ActivityTypeListResponse":
                    # Validate the entire list response
                    try:
                        model_instance = ActivityTypeListResponse(**data)
                        self._validate_activity_type_list_response_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"ActivityTypeListResponse validation failed for {filename}: {e}")
                else:
                    # Validate individual items (for single model types)
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = ActivityTypeListResponse(**item)
                            self._validate_activity_type_list_response_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(f"ActivityTypeListResponse validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = ActivityTypeListResponse(**data)
                    self._validate_activity_type_list_response_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"ActivityTypeListResponse validation failed for {filename}: {e}")
    
    def _validate_activity_type_list_response_fields(self, model: ActivityTypeListResponse, original_data: dict):
        """Validate specific fields for ActivityTypeListResponse."""
        # Add model-specific field validations here
        # List response validations
        assert hasattr(model, 'items'), "List response should have 'items' field"
        assert hasattr(model, 'totalResults'), "List response should have 'totalResults' field"

    def test_application_api_access_list_response_validation(self, response_examples_path):
        """Validate ApplicationApiAccessListResponse model against saved response examples.
        
        Tests against endpoints: #10
        """
        response_files = [
            "10_get_applications_demoauth_apiAccess_demoauth.json",
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
                if "ListResponse" in "ApplicationApiAccessListResponse":
                    # Validate the entire list response
                    try:
                        model_instance = ApplicationApiAccessListResponse(**data)
                        self._validate_application_api_access_list_response_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"ApplicationApiAccessListResponse validation failed for {filename}: {e}")
                else:
                    # Validate individual items (for single model types)
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = ApplicationApiAccessListResponse(**item)
                            self._validate_application_api_access_list_response_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(f"ApplicationApiAccessListResponse validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = ApplicationApiAccessListResponse(**data)
                    self._validate_application_api_access_list_response_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"ApplicationApiAccessListResponse validation failed for {filename}: {e}")
    
    def _validate_application_api_access_list_response_fields(self, model: ApplicationApiAccessListResponse, original_data: dict):
        """Validate specific fields for ApplicationApiAccessListResponse."""
        # Add model-specific field validations here
        # List response validations
        assert hasattr(model, 'items'), "List response should have 'items' field"
        assert hasattr(model, 'totalResults'), "List response should have 'totalResults' field"

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
                if "ListResponse" in "CapacityAreaListResponse":
                    # Validate the entire list response
                    try:
                        model_instance = CapacityAreaListResponse(**data)
                        self._validate_capacity_area_list_response_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"CapacityAreaListResponse validation failed for {filename}: {e}")
                else:
                    # Validate individual items (for single model types)
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
                if "ListResponse" in "Organization":
                    # Validate the entire list response
                    try:
                        model_instance = Organization(**data)
                        self._validate_organization_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"Organization validation failed for {filename}: {e}")
                else:
                    # Validate individual items (for single model types)
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

    def test_resource_type_list_response_validation(self, response_examples_path):
        """Validate ResourceTypeListResponse model against saved response examples.
        
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
                if "ListResponse" in "ResourceTypeListResponse":
                    # Validate the entire list response
                    try:
                        model_instance = ResourceTypeListResponse(**data)
                        self._validate_resource_type_list_response_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"ResourceTypeListResponse validation failed for {filename}: {e}")
                else:
                    # Validate individual items (for single model types)
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = ResourceTypeListResponse(**item)
                            self._validate_resource_type_list_response_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(f"ResourceTypeListResponse validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = ResourceTypeListResponse(**data)
                    self._validate_resource_type_list_response_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"ResourceTypeListResponse validation failed for {filename}: {e}")
    
    def _validate_resource_type_list_response_fields(self, model: ResourceTypeListResponse, original_data: dict):
        """Validate specific fields for ResourceTypeListResponse."""
        # Add model-specific field validations here
        # List response validations
        assert hasattr(model, 'items'), "List response should have 'items' field"
        assert hasattr(model, 'totalResults'), "List response should have 'totalResults' field"

    def test_property_list_response_validation(self, response_examples_path):
        """Validate PropertyListResponse model against saved response examples.
        
        Tests against endpoints: #50
        """
        response_files = [
            "50_get_properties.json",
            "50_properties.json",
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
                if "ListResponse" in "PropertyListResponse":
                    # Validate the entire list response
                    try:
                        model_instance = PropertyListResponse(**data)
                        self._validate_property_list_response_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"PropertyListResponse validation failed for {filename}: {e}")
                else:
                    # Validate individual items (for single model types)
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = PropertyListResponse(**item)
                            self._validate_property_list_response_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(f"PropertyListResponse validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = PropertyListResponse(**data)
                    self._validate_property_list_response_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"PropertyListResponse validation failed for {filename}: {e}")
    
    def _validate_property_list_response_fields(self, model: PropertyListResponse, original_data: dict):
        """Validate specific fields for PropertyListResponse."""
        # Add model-specific field validations here
        # List response validations
        assert hasattr(model, 'items'), "List response should have 'items' field"
        assert hasattr(model, 'totalResults'), "List response should have 'totalResults' field"

    def test_work_zone_key_response_validation(self, response_examples_path):
        """Validate WorkZoneKeyResponse model against saved response examples.
        
        Tests against endpoints: #86
        """
        response_files = [
            "86_get_the_work_zone_key.json",
            "86_get_workZoneKey.json",
            "86_workzone_keys.json",
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
                if "ListResponse" in "WorkZoneKeyResponse":
                    # Validate the entire list response
                    try:
                        model_instance = WorkZoneKeyResponse(**data)
                        self._validate_work_zone_key_response_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"WorkZoneKeyResponse validation failed for {filename}: {e}")
                else:
                    # Validate individual items (for single model types)
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = WorkZoneKeyResponse(**item)
                            self._validate_work_zone_key_response_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(f"WorkZoneKeyResponse validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = WorkZoneKeyResponse(**data)
                    self._validate_work_zone_key_response_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"WorkZoneKeyResponse validation failed for {filename}: {e}")
    
    def _validate_work_zone_key_response_fields(self, model: WorkZoneKeyResponse, original_data: dict):
        """Validate specific fields for WorkZoneKeyResponse."""
        # Add model-specific field validations here
        pass  # Add specific field validations as needed

    def test_activity_type_group_list_response_validation(self, response_examples_path):
        """Validate ActivityTypeGroupListResponse model against saved response examples.
        
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
                if "ListResponse" in "ActivityTypeGroupListResponse":
                    # Validate the entire list response
                    try:
                        model_instance = ActivityTypeGroupListResponse(**data)
                        self._validate_activity_type_group_list_response_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"ActivityTypeGroupListResponse validation failed for {filename}: {e}")
                else:
                    # Validate individual items (for single model types)
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = ActivityTypeGroupListResponse(**item)
                            self._validate_activity_type_group_list_response_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(f"ActivityTypeGroupListResponse validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = ActivityTypeGroupListResponse(**data)
                    self._validate_activity_type_group_list_response_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"ActivityTypeGroupListResponse validation failed for {filename}: {e}")
    
    def _validate_activity_type_group_list_response_fields(self, model: ActivityTypeGroupListResponse, original_data: dict):
        """Validate specific fields for ActivityTypeGroupListResponse."""
        # Add model-specific field validations here
        # List response validations
        assert hasattr(model, 'items'), "List response should have 'items' field"
        assert hasattr(model, 'totalResults'), "List response should have 'totalResults' field"

    def test_application_api_access_validation(self, response_examples_path):
        """Validate ApplicationApiAccess model against saved response examples.
        
        Tests against endpoints: #11
        """
        response_files = [
            "11_get_applications_demoauth_apiAccess_metadataAPI_apiAccess_demoauth_apiAccess_metadataAPI_demoauth_apiAccess_metadataAPI.json",
            "11_get_applications_demoauth_apiAccess_metadataAPI_demoauth_metadataAPI.json",
            "11_get_applications_metadataAPI_apiAccess_metadataAPI_metadataAPI.json",
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
                if "ListResponse" in "ApplicationApiAccess":
                    # Validate the entire list response
                    try:
                        model_instance = ApplicationApiAccess(**data)
                        self._validate_application_api_access_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"ApplicationApiAccess validation failed for {filename}: {e}")
                else:
                    # Validate individual items (for single model types)
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = ApplicationApiAccess(**item)
                            self._validate_application_api_access_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(f"ApplicationApiAccess validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = ApplicationApiAccess(**data)
                    self._validate_application_api_access_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"ApplicationApiAccess validation failed for {filename}: {e}")
    
    def _validate_application_api_access_fields(self, model: ApplicationApiAccess, original_data: dict):
        """Validate specific fields for ApplicationApiAccess."""
        # Add model-specific field validations here
        if hasattr(model, 'status') and getattr(model, 'status') is not None:
            assert getattr(model, 'status') in ['active', 'inactive'], "Invalid enum value for status"

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
                if "ListResponse" in "Application":
                    # Validate the entire list response
                    try:
                        model_instance = Application(**data)
                        self._validate_application_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"Application validation failed for {filename}: {e}")
                else:
                    # Validate individual items (for single model types)
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
                if "ListResponse" in "InventoryType":
                    # Validate the entire list response
                    try:
                        model_instance = InventoryType(**data)
                        self._validate_inventory_type_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"InventoryType validation failed for {filename}: {e}")
                else:
                    # Validate individual items (for single model types)
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
                if "ListResponse" in "ActivityTypeGroup":
                    # Validate the entire list response
                    try:
                        model_instance = ActivityTypeGroup(**data)
                        self._validate_activity_type_group_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"ActivityTypeGroup validation failed for {filename}: {e}")
                else:
                    # Validate individual items (for single model types)
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
                if "ListResponse" in "WorkSkillGroup":
                    # Validate the entire list response
                    try:
                        model_instance = WorkSkillGroup(**data)
                        self._validate_work_skill_group_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"WorkSkillGroup validation failed for {filename}: {e}")
                else:
                    # Validate individual items (for single model types)
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

    def test_routing_plan_export_response_validation(self, response_examples_path):
        """Validate RoutingPlanExportResponse model against saved response examples.
        
        Tests against endpoints: #59
        """
        response_files = [
            "59_get_routingProfiles_MaintenanceRoutingProfile_plans_Optimization_custom-actions_export_MaintenanceRoutingProfile_Optimization.json",
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
                if "ListResponse" in "RoutingPlanExportResponse":
                    # Validate the entire list response
                    try:
                        model_instance = RoutingPlanExportResponse(**data)
                        self._validate_routing_plan_export_response_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"RoutingPlanExportResponse validation failed for {filename}: {e}")
                else:
                    # Validate individual items (for single model types)
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = RoutingPlanExportResponse(**item)
                            self._validate_routing_plan_export_response_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(f"RoutingPlanExportResponse validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = RoutingPlanExportResponse(**data)
                    self._validate_routing_plan_export_response_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"RoutingPlanExportResponse validation failed for {filename}: {e}")
    
    def _validate_routing_plan_export_response_fields(self, model: RoutingPlanExportResponse, original_data: dict):
        """Validate specific fields for RoutingPlanExportResponse."""
        # Add model-specific field validations here
        pass  # Add specific field validations as needed

    def test_form_list_response_validation(self, response_examples_path):
        """Validate FormListResponse model against saved response examples.
        
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
                if "ListResponse" in "FormListResponse":
                    # Validate the entire list response
                    try:
                        model_instance = FormListResponse(**data)
                        self._validate_form_list_response_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"FormListResponse validation failed for {filename}: {e}")
                else:
                    # Validate individual items (for single model types)
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = FormListResponse(**item)
                            self._validate_form_list_response_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(f"FormListResponse validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = FormListResponse(**data)
                    self._validate_form_list_response_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"FormListResponse validation failed for {filename}: {e}")
    
    def _validate_form_list_response_fields(self, model: FormListResponse, original_data: dict):
        """Validate specific fields for FormListResponse."""
        # Add model-specific field validations here
        # List response validations
        assert hasattr(model, 'items'), "List response should have 'items' field"
        assert hasattr(model, 'totalResults'), "List response should have 'totalResults' field"

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
                if "ListResponse" in "Shift":
                    # Validate the entire list response
                    try:
                        model_instance = Shift(**data)
                        self._validate_shift_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"Shift validation failed for {filename}: {e}")
                else:
                    # Validate individual items (for single model types)
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

    def test_workskill_validation(self, response_examples_path):
        """Validate Workskill model against saved response examples.
        
        Tests against endpoints: #75
        """
        response_files = [
            "75_get_workSkills_EST_EST.json",
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
                if "ListResponse" in "Workskill":
                    # Validate the entire list response
                    try:
                        model_instance = Workskill(**data)
                        self._validate_workskill_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"Workskill validation failed for {filename}: {e}")
                else:
                    # Validate individual items (for single model types)
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = Workskill(**item)
                            self._validate_workskill_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(f"Workskill validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = Workskill(**data)
                    self._validate_workskill_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"Workskill validation failed for {filename}: {e}")
    
    def _validate_workskill_fields(self, model: Workskill, original_data: dict):
        """Validate specific fields for Workskill."""
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
                if "ListResponse" in "LinkTemplate":
                    # Validate the entire list response
                    try:
                        model_instance = LinkTemplate(**data)
                        self._validate_link_template_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"LinkTemplate validation failed for {filename}: {e}")
                else:
                    # Validate individual items (for single model types)
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

    def test_workzone_validation(self, response_examples_path):
        """Validate Workzone model against saved response examples.
        
        Tests against endpoints: #82
        """
        response_files = [
            "82_get_workzone.json",
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
                if "ListResponse" in "Workzone":
                    # Validate the entire list response
                    try:
                        model_instance = Workzone(**data)
                        self._validate_workzone_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"Workzone validation failed for {filename}: {e}")
                else:
                    # Validate individual items (for single model types)
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = Workzone(**item)
                            self._validate_workzone_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(f"Workzone validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = Workzone(**data)
                    self._validate_workzone_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"Workzone validation failed for {filename}: {e}")
    
    def _validate_workzone_fields(self, model: Workzone, original_data: dict):
        """Validate specific fields for Workzone."""
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
                if "ListResponse" in "ActivityType":
                    # Validate the entire list response
                    try:
                        model_instance = ActivityType(**data)
                        self._validate_activity_type_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"ActivityType validation failed for {filename}: {e}")
                else:
                    # Validate individual items (for single model types)
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
                if "ListResponse" in "CapacityAreaCategoryListResponse":
                    # Validate the entire list response
                    try:
                        model_instance = CapacityAreaCategoryListResponse(**data)
                        self._validate_capacity_area_category_list_response_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"CapacityAreaCategoryListResponse validation failed for {filename}: {e}")
                else:
                    # Validate individual items (for single model types)
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

    def test_property_response_validation(self, response_examples_path):
        """Validate PropertyResponse model against saved response examples.
        
        Tests against endpoints: #51
        """
        response_files = [
            "51_property.json",
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
                if "ListResponse" in "PropertyResponse":
                    # Validate the entire list response
                    try:
                        model_instance = PropertyResponse(**data)
                        self._validate_property_response_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"PropertyResponse validation failed for {filename}: {e}")
                else:
                    # Validate individual items (for single model types)
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = PropertyResponse(**item)
                            self._validate_property_response_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(f"PropertyResponse validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = PropertyResponse(**data)
                    self._validate_property_response_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"PropertyResponse validation failed for {filename}: {e}")
    
    def _validate_property_response_fields(self, model: PropertyResponse, original_data: dict):
        """Validate specific fields for PropertyResponse."""
        # Add model-specific field validations here
        pass  # Add specific field validations as needed
