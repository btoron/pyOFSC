"""
Model validation tests for Core API responses.

This file contains comprehensive validation tests for all Core API models
against real API response examples.

Generated on: 2025-07-24 23:57:35 UTC
"""

import json
from pathlib import Path
import pytest
from pydantic import ValidationError

# Import the actual models
from ofsc.models.core import Activity, ActivityCapacityCategory, ActivityCapacityCategoryListResponse, ActivityCustomerInventory, ActivityCustomerInventoryListResponse, ActivityDeinstalledInventory, ActivityDeinstalledInventoryListResponse, ActivityInstalledInventory, ActivityInstalledInventoryListResponse, ActivityLink, ActivityLinkListResponse, ActivityRequiredInventory, ActivityRequiredInventoryListResponse, ActivityResourcePreference, ActivityResourcePreferenceListResponse, ActivitySubmittedForm, ActivitySubmittedFormListResponse, AssignedLocationsResponse, DailyExtractFiles, DailyExtractFolders, Inventory, LastKnownPosition, LastKnownPositionListResponse, Location, LocationListResponse, NearbyActivity, NearbyActivityListResponse, Resource, ResourceInventory, ResourceInventoryListResponse, ResourceListResponse, ResourceUsersListResponse, ResourceWorkScheduleResponse, ResourceWorkSkill, ResourceWorkSkillListResponse, ResourceWorkZone, ResourceWorkZoneListResponse, RouteInfoListResponse, Subscription, SubscriptionList, User, UserListResponse

class TestCoreModelsValidation:
    """Test Core API model validation against response examples."""
    
    @pytest.fixture
    def response_examples_path(self):
        """Path to response examples directory."""
        # Go up from tests/models/generated/ to project root, then to response_examples
        return Path(__file__).parent.parent.parent.parent / "response_examples"

    def test_activity_installed_inventory_list_response_validation(self, response_examples_path):
        """Validate ActivityInstalledInventoryListResponse model against saved response examples.
        
        Tests against endpoints: #121
        """
        response_files = [
            "121_get_activities_3951883_installedInventories_3951883.json",
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
                        model_instance = ActivityInstalledInventoryListResponse(**data)
                        self._validate_activity_installed_inventory_list_response_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"ActivityInstalledInventoryListResponse validation failed for {filename}: {e}")
                    
                    # Also validate individual items using the item model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = ActivityInstalledInventory(**item)
                            print(f"✅ Validated {filename} item {idx} with ActivityInstalledInventory")
                        except ValidationError as e:
                            pytest.fail(f"ActivityInstalledInventory validation failed for {filename} item {idx}: {e}")
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = ActivityInstalledInventoryListResponse(**item)
                            self._validate_activity_installed_inventory_list_response_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(f"ActivityInstalledInventoryListResponse validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = ActivityInstalledInventoryListResponse(**data)
                    self._validate_activity_installed_inventory_list_response_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"ActivityInstalledInventoryListResponse validation failed for {filename}: {e}")
    
    def _validate_activity_installed_inventory_list_response_fields(self, model: ActivityInstalledInventoryListResponse, original_data: dict):
        """Validate specific fields for ActivityInstalledInventoryListResponse."""
        # Add model-specific field validations here
        # List response validations
        assert hasattr(model, 'items'), "List response should have 'items' field"
        assert hasattr(model, 'totalResults'), "List response should have 'totalResults' field"

    def test_user_list_response_validation(self, response_examples_path):
        """Validate UserListResponse model against saved response examples.
        
        Tests against endpoints: #219
        """
        response_files = [
            "219_get_users.json",
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
                        model_instance = UserListResponse(**data)
                        self._validate_user_list_response_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"UserListResponse validation failed for {filename}: {e}")
                    
                    # Also validate individual items using the item model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = User(**item)
                            print(f"✅ Validated {filename} item {idx} with User")
                        except ValidationError as e:
                            pytest.fail(f"User validation failed for {filename} item {idx}: {e}")
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = UserListResponse(**item)
                            self._validate_user_list_response_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(f"UserListResponse validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = UserListResponse(**data)
                    self._validate_user_list_response_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"UserListResponse validation failed for {filename}: {e}")
    
    def _validate_user_list_response_fields(self, model: UserListResponse, original_data: dict):
        """Validate specific fields for UserListResponse."""
        # Add model-specific field validations here
        # List response validations
        assert hasattr(model, 'items'), "List response should have 'items' field"
        assert hasattr(model, 'totalResults'), "List response should have 'totalResults' field"

    def test_resource_work_schedule_response_validation(self, response_examples_path):
        """Validate ResourceWorkScheduleResponse model against saved response examples.
        
        Tests against endpoints: #182
        """
        response_files = [
            "182_get_resources_33035_workSchedules_33035.json",
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
                        model_instance = ResourceWorkScheduleResponse(**data)
                        self._validate_resource_work_schedule_response_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"ResourceWorkScheduleResponse validation failed for {filename}: {e}")
                    
                    # Also validate individual items using the item model
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = ResourceWorkScheduleResponse(**item)
                            self._validate_resource_work_schedule_response_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(f"ResourceWorkScheduleResponse validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = ResourceWorkScheduleResponse(**data)
                    self._validate_resource_work_schedule_response_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"ResourceWorkScheduleResponse validation failed for {filename}: {e}")
    
    def _validate_resource_work_schedule_response_fields(self, model: ResourceWorkScheduleResponse, original_data: dict):
        """Validate specific fields for ResourceWorkScheduleResponse."""
        # Add model-specific field validations here
        pass  # Add specific field validations as needed

    def test_location_list_response_validation(self, response_examples_path):
        """Validate LocationListResponse model against saved response examples.
        
        Tests against endpoints: #191, #192
        """
        response_files = [
            "191_get_resources_33035_locations_33035.json",
            "192_get_resources_33035_locations_25_33035_25.json",
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
                        model_instance = LocationListResponse(**data)
                        self._validate_location_list_response_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"LocationListResponse validation failed for {filename}: {e}")
                    
                    # Also validate individual items using the item model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = Location(**item)
                            print(f"✅ Validated {filename} item {idx} with Location")
                        except ValidationError as e:
                            pytest.fail(f"Location validation failed for {filename} item {idx}: {e}")
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = LocationListResponse(**item)
                            self._validate_location_list_response_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(f"LocationListResponse validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = LocationListResponse(**data)
                    self._validate_location_list_response_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"LocationListResponse validation failed for {filename}: {e}")
    
    def _validate_location_list_response_fields(self, model: LocationListResponse, original_data: dict):
        """Validate specific fields for LocationListResponse."""
        # Add model-specific field validations here
        # List response validations
        assert hasattr(model, 'items'), "List response should have 'items' field"
        assert hasattr(model, 'totalResults'), "List response should have 'totalResults' field"

    def test_last_known_position_list_response_validation(self, response_examples_path):
        """Validate LastKnownPositionListResponse model against saved response examples.
        
        Tests against endpoints: #214
        """
        response_files = [
            "214_get_last_known_positions_of_resources.json",
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
                        model_instance = LastKnownPositionListResponse(**data)
                        self._validate_last_known_position_list_response_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"LastKnownPositionListResponse validation failed for {filename}: {e}")
                    
                    # Also validate individual items using the item model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = LastKnownPosition(**item)
                            print(f"✅ Validated {filename} item {idx} with LastKnownPosition")
                        except ValidationError as e:
                            pytest.fail(f"LastKnownPosition validation failed for {filename} item {idx}: {e}")
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = LastKnownPositionListResponse(**item)
                            self._validate_last_known_position_list_response_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(f"LastKnownPositionListResponse validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = LastKnownPositionListResponse(**data)
                    self._validate_last_known_position_list_response_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"LastKnownPositionListResponse validation failed for {filename}: {e}")
    
    def _validate_last_known_position_list_response_fields(self, model: LastKnownPositionListResponse, original_data: dict):
        """Validate specific fields for LastKnownPositionListResponse."""
        # Add model-specific field validations here
        # List response validations
        assert hasattr(model, 'items'), "List response should have 'items' field"
        assert hasattr(model, 'totalResults'), "List response should have 'totalResults' field"

    def test_activity_validation(self, response_examples_path):
        """Validate Activity model against saved response examples.
        
        Tests against endpoints: #107
        """
        response_files = [
            "107_get_activities_3951883_3951883.json",
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
                        model_instance = Activity(**data)
                        self._validate_activity_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"Activity validation failed for {filename}: {e}")
                    
                    # Also validate individual items using the item model
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = Activity(**item)
                            self._validate_activity_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(f"Activity validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = Activity(**data)
                    self._validate_activity_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"Activity validation failed for {filename}: {e}")
    
    def _validate_activity_fields(self, model: Activity, original_data: dict):
        """Validate specific fields for Activity."""
        # Add model-specific field validations here
        pass  # Add specific field validations as needed

    def test_resource_validation(self, response_examples_path):
        """Validate Resource model against saved response examples.
        
        Tests against endpoints: #167
        """
        response_files = [
            "167_get_resources_33015_33015.json",
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
                        model_instance = Resource(**data)
                        self._validate_resource_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"Resource validation failed for {filename}: {e}")
                    
                    # Also validate individual items using the item model
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = Resource(**item)
                            self._validate_resource_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(f"Resource validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = Resource(**data)
                    self._validate_resource_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"Resource validation failed for {filename}: {e}")
    
    def _validate_resource_fields(self, model: Resource, original_data: dict):
        """Validate specific fields for Resource."""
        # Add model-specific field validations here
        pass  # Add specific field validations as needed

    def test_resource_inventory_list_response_validation(self, response_examples_path):
        """Validate ResourceInventoryListResponse model against saved response examples.
        
        Tests against endpoints: #174
        """
        response_files = [
            "174_get_resources_33035_inventories_33035.json",
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
                        model_instance = ResourceInventoryListResponse(**data)
                        self._validate_resource_inventory_list_response_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"ResourceInventoryListResponse validation failed for {filename}: {e}")
                    
                    # Also validate individual items using the item model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = ResourceInventory(**item)
                            print(f"✅ Validated {filename} item {idx} with ResourceInventory")
                        except ValidationError as e:
                            pytest.fail(f"ResourceInventory validation failed for {filename} item {idx}: {e}")
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = ResourceInventoryListResponse(**item)
                            self._validate_resource_inventory_list_response_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(f"ResourceInventoryListResponse validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = ResourceInventoryListResponse(**data)
                    self._validate_resource_inventory_list_response_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"ResourceInventoryListResponse validation failed for {filename}: {e}")
    
    def _validate_resource_inventory_list_response_fields(self, model: ResourceInventoryListResponse, original_data: dict):
        """Validate specific fields for ResourceInventoryListResponse."""
        # Add model-specific field validations here
        # List response validations
        assert hasattr(model, 'items'), "List response should have 'items' field"
        assert hasattr(model, 'totalResults'), "List response should have 'totalResults' field"

    def test_resource_list_response_validation(self, response_examples_path):
        """Validate ResourceListResponse model against saved response examples.
        
        Tests against endpoints: #163, #165
        """
        response_files = [
            "163_get_resources.json",
            "165_get_resources_FLUSA_descendants_FLUSA.json",
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
                        model_instance = ResourceListResponse(**data)
                        self._validate_resource_list_response_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"ResourceListResponse validation failed for {filename}: {e}")
                    
                    # Also validate individual items using the item model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = Resource(**item)
                            print(f"✅ Validated {filename} item {idx} with Resource")
                        except ValidationError as e:
                            pytest.fail(f"Resource validation failed for {filename} item {idx}: {e}")
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = ResourceListResponse(**item)
                            self._validate_resource_list_response_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(f"ResourceListResponse validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = ResourceListResponse(**data)
                    self._validate_resource_list_response_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"ResourceListResponse validation failed for {filename}: {e}")
    
    def _validate_resource_list_response_fields(self, model: ResourceListResponse, original_data: dict):
        """Validate specific fields for ResourceListResponse."""
        # Add model-specific field validations here
        # List response validations
        assert hasattr(model, 'items'), "List response should have 'items' field"
        assert hasattr(model, 'totalResults'), "List response should have 'totalResults' field"

    def test_user_validation(self, response_examples_path):
        """Validate User model against saved response examples.
        
        Tests against endpoints: #220
        """
        response_files = [
            "220_get_users_william.arndt_william.arndt.json",
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
                        model_instance = User(**data)
                        self._validate_user_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"User validation failed for {filename}: {e}")
                    
                    # Also validate individual items using the item model
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = User(**item)
                            self._validate_user_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(f"User validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = User(**data)
                    self._validate_user_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"User validation failed for {filename}: {e}")
    
    def _validate_user_fields(self, model: User, original_data: dict):
        """Validate specific fields for User."""
        # Add model-specific field validations here
        pass  # Add specific field validations as needed

    def test_assigned_locations_response_validation(self, response_examples_path):
        """Validate AssignedLocationsResponse model against saved response examples.
        
        Tests against endpoints: #197
        """
        response_files = [
            "197_get_resources_33035_assignedLocations_33035.json",
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
                        model_instance = AssignedLocationsResponse(**data)
                        self._validate_assigned_locations_response_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"AssignedLocationsResponse validation failed for {filename}: {e}")
                    
                    # Also validate individual items using the item model
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = AssignedLocationsResponse(**item)
                            self._validate_assigned_locations_response_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(f"AssignedLocationsResponse validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = AssignedLocationsResponse(**data)
                    self._validate_assigned_locations_response_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"AssignedLocationsResponse validation failed for {filename}: {e}")
    
    def _validate_assigned_locations_response_fields(self, model: AssignedLocationsResponse, original_data: dict):
        """Validate specific fields for AssignedLocationsResponse."""
        # Add model-specific field validations here
        pass  # Add specific field validations as needed

    def test_route_info_list_response_validation(self, response_examples_path):
        """Validate RouteInfoListResponse model against saved response examples.
        
        Tests against endpoints: #203
        """
        response_files = [
            "203_get_resources_33035_routes_2025-07-24_33035_2025-07-24.json",
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
                        model_instance = RouteInfoListResponse(**data)
                        self._validate_route_info_list_response_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"RouteInfoListResponse validation failed for {filename}: {e}")
                    
                    # Also validate individual items using the item model
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = RouteInfoListResponse(**item)
                            self._validate_route_info_list_response_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(f"RouteInfoListResponse validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = RouteInfoListResponse(**data)
                    self._validate_route_info_list_response_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"RouteInfoListResponse validation failed for {filename}: {e}")
    
    def _validate_route_info_list_response_fields(self, model: RouteInfoListResponse, original_data: dict):
        """Validate specific fields for RouteInfoListResponse."""
        # Add model-specific field validations here
        # List response validations
        assert hasattr(model, 'items'), "List response should have 'items' field"
        assert hasattr(model, 'totalResults'), "List response should have 'totalResults' field"

    def test_inventory_validation(self, response_examples_path):
        """Validate Inventory model against saved response examples.
        
        Tests against endpoints: #154
        """
        response_files = [
            "154_get_inventories_21260519_21260519.json",
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
                        model_instance = Inventory(**data)
                        self._validate_inventory_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"Inventory validation failed for {filename}: {e}")
                    
                    # Also validate individual items using the item model
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = Inventory(**item)
                            self._validate_inventory_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(f"Inventory validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = Inventory(**data)
                    self._validate_inventory_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"Inventory validation failed for {filename}: {e}")
    
    def _validate_inventory_fields(self, model: Inventory, original_data: dict):
        """Validate specific fields for Inventory."""
        # Add model-specific field validations here
        pass  # Add specific field validations as needed

    def test_activity_resource_preference_list_response_validation(self, response_examples_path):
        """Validate ActivityResourcePreferenceListResponse model against saved response examples.
        
        Tests against endpoints: #114
        """
        response_files = [
            "114_get_activities_3951883_resourcePreferences_3951883.json",
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
                        model_instance = ActivityResourcePreferenceListResponse(**data)
                        self._validate_activity_resource_preference_list_response_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"ActivityResourcePreferenceListResponse validation failed for {filename}: {e}")
                    
                    # Also validate individual items using the item model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = ActivityResourcePreference(**item)
                            print(f"✅ Validated {filename} item {idx} with ActivityResourcePreference")
                        except ValidationError as e:
                            pytest.fail(f"ActivityResourcePreference validation failed for {filename} item {idx}: {e}")
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = ActivityResourcePreferenceListResponse(**item)
                            self._validate_activity_resource_preference_list_response_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(f"ActivityResourcePreferenceListResponse validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = ActivityResourcePreferenceListResponse(**data)
                    self._validate_activity_resource_preference_list_response_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"ActivityResourcePreferenceListResponse validation failed for {filename}: {e}")
    
    def _validate_activity_resource_preference_list_response_fields(self, model: ActivityResourcePreferenceListResponse, original_data: dict):
        """Validate specific fields for ActivityResourcePreferenceListResponse."""
        # Add model-specific field validations here
        # List response validations
        assert hasattr(model, 'items'), "List response should have 'items' field"
        assert hasattr(model, 'totalResults'), "List response should have 'totalResults' field"

    def test_activity_required_inventory_list_response_validation(self, response_examples_path):
        """Validate ActivityRequiredInventoryListResponse model against saved response examples.
        
        Tests against endpoints: #117
        """
        response_files = [
            "117_get_activities_3951883_requiredInventories_3951883.json",
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
                        model_instance = ActivityRequiredInventoryListResponse(**data)
                        self._validate_activity_required_inventory_list_response_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"ActivityRequiredInventoryListResponse validation failed for {filename}: {e}")
                    
                    # Also validate individual items using the item model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = ActivityRequiredInventory(**item)
                            print(f"✅ Validated {filename} item {idx} with ActivityRequiredInventory")
                        except ValidationError as e:
                            pytest.fail(f"ActivityRequiredInventory validation failed for {filename} item {idx}: {e}")
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = ActivityRequiredInventoryListResponse(**item)
                            self._validate_activity_required_inventory_list_response_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(f"ActivityRequiredInventoryListResponse validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = ActivityRequiredInventoryListResponse(**data)
                    self._validate_activity_required_inventory_list_response_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"ActivityRequiredInventoryListResponse validation failed for {filename}: {e}")
    
    def _validate_activity_required_inventory_list_response_fields(self, model: ActivityRequiredInventoryListResponse, original_data: dict):
        """Validate specific fields for ActivityRequiredInventoryListResponse."""
        # Add model-specific field validations here
        # List response validations
        assert hasattr(model, 'items'), "List response should have 'items' field"
        assert hasattr(model, 'totalResults'), "List response should have 'totalResults' field"

    def test_daily_extract_files_validation(self, response_examples_path):
        """Validate DailyExtractFiles model against saved response examples.
        
        Tests against endpoints: #145
        """
        response_files = [
            "145_get_folders_dailyExtract_folders_2025-07-24_files_2025-07-24.json",
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
                        model_instance = DailyExtractFiles(**data)
                        self._validate_daily_extract_files_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"DailyExtractFiles validation failed for {filename}: {e}")
                    
                    # Also validate individual items using the item model
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = DailyExtractFiles(**item)
                            self._validate_daily_extract_files_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(f"DailyExtractFiles validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = DailyExtractFiles(**data)
                    self._validate_daily_extract_files_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"DailyExtractFiles validation failed for {filename}: {e}")
    
    def _validate_daily_extract_files_fields(self, model: DailyExtractFiles, original_data: dict):
        """Validate specific fields for DailyExtractFiles."""
        # Add model-specific field validations here
        pass  # Add specific field validations as needed

    def test_activity_link_list_response_validation(self, response_examples_path):
        """Validate ActivityLinkListResponse model against saved response examples.
        
        Tests against endpoints: #123
        """
        response_files = [
            "123_get_activities_3951883_linkedActivities_3951883.json",
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
                        model_instance = ActivityLinkListResponse(**data)
                        self._validate_activity_link_list_response_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"ActivityLinkListResponse validation failed for {filename}: {e}")
                    
                    # Also validate individual items using the item model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = ActivityLink(**item)
                            print(f"✅ Validated {filename} item {idx} with ActivityLink")
                        except ValidationError as e:
                            pytest.fail(f"ActivityLink validation failed for {filename} item {idx}: {e}")
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = ActivityLinkListResponse(**item)
                            self._validate_activity_link_list_response_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(f"ActivityLinkListResponse validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = ActivityLinkListResponse(**data)
                    self._validate_activity_link_list_response_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"ActivityLinkListResponse validation failed for {filename}: {e}")
    
    def _validate_activity_link_list_response_fields(self, model: ActivityLinkListResponse, original_data: dict):
        """Validate specific fields for ActivityLinkListResponse."""
        # Add model-specific field validations here
        # List response validations
        assert hasattr(model, 'items'), "List response should have 'items' field"
        assert hasattr(model, 'totalResults'), "List response should have 'totalResults' field"

    def test_activity_capacity_category_list_response_validation(self, response_examples_path):
        """Validate ActivityCapacityCategoryListResponse model against saved response examples.
        
        Tests against endpoints: #126
        """
        response_files = [
            "126_get_activities_3951883_capacityCategories_3951883.json",
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
                        model_instance = ActivityCapacityCategoryListResponse(**data)
                        self._validate_activity_capacity_category_list_response_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"ActivityCapacityCategoryListResponse validation failed for {filename}: {e}")
                    
                    # Also validate individual items using the item model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = ActivityCapacityCategory(**item)
                            print(f"✅ Validated {filename} item {idx} with ActivityCapacityCategory")
                        except ValidationError as e:
                            pytest.fail(f"ActivityCapacityCategory validation failed for {filename} item {idx}: {e}")
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = ActivityCapacityCategoryListResponse(**item)
                            self._validate_activity_capacity_category_list_response_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(f"ActivityCapacityCategoryListResponse validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = ActivityCapacityCategoryListResponse(**data)
                    self._validate_activity_capacity_category_list_response_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"ActivityCapacityCategoryListResponse validation failed for {filename}: {e}")
    
    def _validate_activity_capacity_category_list_response_fields(self, model: ActivityCapacityCategoryListResponse, original_data: dict):
        """Validate specific fields for ActivityCapacityCategoryListResponse."""
        # Add model-specific field validations here
        # List response validations
        assert hasattr(model, 'items'), "List response should have 'items' field"
        assert hasattr(model, 'totalResults'), "List response should have 'totalResults' field"

    def test_resource_users_list_response_validation(self, response_examples_path):
        """Validate ResourceUsersListResponse model against saved response examples.
        
        Tests against endpoints: #170
        """
        response_files = [
            "170_get_resources_33015_users_33015.json",
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
                        model_instance = ResourceUsersListResponse(**data)
                        self._validate_resource_users_list_response_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"ResourceUsersListResponse validation failed for {filename}: {e}")
                    
                    # Also validate individual items using the item model
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = ResourceUsersListResponse(**item)
                            self._validate_resource_users_list_response_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(f"ResourceUsersListResponse validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = ResourceUsersListResponse(**data)
                    self._validate_resource_users_list_response_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"ResourceUsersListResponse validation failed for {filename}: {e}")
    
    def _validate_resource_users_list_response_fields(self, model: ResourceUsersListResponse, original_data: dict):
        """Validate specific fields for ResourceUsersListResponse."""
        # Add model-specific field validations here
        # List response validations
        assert hasattr(model, 'items'), "List response should have 'items' field"
        assert hasattr(model, 'totalResults'), "List response should have 'totalResults' field"

    def test_activity_submitted_form_list_response_validation(self, response_examples_path):
        """Validate ActivitySubmittedFormListResponse model against saved response examples.
        
        Tests against endpoints: #112
        """
        response_files = [
            "112_get_activities_3951883_submittedForms_3951883.json",
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
                        model_instance = ActivitySubmittedFormListResponse(**data)
                        self._validate_activity_submitted_form_list_response_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"ActivitySubmittedFormListResponse validation failed for {filename}: {e}")
                    
                    # Also validate individual items using the item model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = ActivitySubmittedForm(**item)
                            print(f"✅ Validated {filename} item {idx} with ActivitySubmittedForm")
                        except ValidationError as e:
                            pytest.fail(f"ActivitySubmittedForm validation failed for {filename} item {idx}: {e}")
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = ActivitySubmittedFormListResponse(**item)
                            self._validate_activity_submitted_form_list_response_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(f"ActivitySubmittedFormListResponse validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = ActivitySubmittedFormListResponse(**data)
                    self._validate_activity_submitted_form_list_response_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"ActivitySubmittedFormListResponse validation failed for {filename}: {e}")
    
    def _validate_activity_submitted_form_list_response_fields(self, model: ActivitySubmittedFormListResponse, original_data: dict):
        """Validate specific fields for ActivitySubmittedFormListResponse."""
        # Add model-specific field validations here
        # List response validations
        assert hasattr(model, 'items'), "List response should have 'items' field"
        assert hasattr(model, 'totalResults'), "List response should have 'totalResults' field"

    def test_nearby_activity_list_response_validation(self, response_examples_path):
        """Validate NearbyActivityListResponse model against saved response examples.
        
        Tests against endpoints: #206
        """
        response_files = [
            "206_get_resources_33035_findNearbyActivities_33035.json",
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
                        model_instance = NearbyActivityListResponse(**data)
                        self._validate_nearby_activity_list_response_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"NearbyActivityListResponse validation failed for {filename}: {e}")
                    
                    # Also validate individual items using the item model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = NearbyActivity(**item)
                            print(f"✅ Validated {filename} item {idx} with NearbyActivity")
                        except ValidationError as e:
                            pytest.fail(f"NearbyActivity validation failed for {filename} item {idx}: {e}")
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = NearbyActivityListResponse(**item)
                            self._validate_nearby_activity_list_response_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(f"NearbyActivityListResponse validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = NearbyActivityListResponse(**data)
                    self._validate_nearby_activity_list_response_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"NearbyActivityListResponse validation failed for {filename}: {e}")
    
    def _validate_nearby_activity_list_response_fields(self, model: NearbyActivityListResponse, original_data: dict):
        """Validate specific fields for NearbyActivityListResponse."""
        # Add model-specific field validations here
        # List response validations
        assert hasattr(model, 'items'), "List response should have 'items' field"
        assert hasattr(model, 'totalResults'), "List response should have 'totalResults' field"

    def test_activity_deinstalled_inventory_list_response_validation(self, response_examples_path):
        """Validate ActivityDeinstalledInventoryListResponse model against saved response examples.
        
        Tests against endpoints: #122
        """
        response_files = [
            "122_get_activities_3951883_deinstalledInventories_3951883.json",
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
                        model_instance = ActivityDeinstalledInventoryListResponse(**data)
                        self._validate_activity_deinstalled_inventory_list_response_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"ActivityDeinstalledInventoryListResponse validation failed for {filename}: {e}")
                    
                    # Also validate individual items using the item model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = ActivityDeinstalledInventory(**item)
                            print(f"✅ Validated {filename} item {idx} with ActivityDeinstalledInventory")
                        except ValidationError as e:
                            pytest.fail(f"ActivityDeinstalledInventory validation failed for {filename} item {idx}: {e}")
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = ActivityDeinstalledInventoryListResponse(**item)
                            self._validate_activity_deinstalled_inventory_list_response_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(f"ActivityDeinstalledInventoryListResponse validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = ActivityDeinstalledInventoryListResponse(**data)
                    self._validate_activity_deinstalled_inventory_list_response_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"ActivityDeinstalledInventoryListResponse validation failed for {filename}: {e}")
    
    def _validate_activity_deinstalled_inventory_list_response_fields(self, model: ActivityDeinstalledInventoryListResponse, original_data: dict):
        """Validate specific fields for ActivityDeinstalledInventoryListResponse."""
        # Add model-specific field validations here
        # List response validations
        assert hasattr(model, 'items'), "List response should have 'items' field"
        assert hasattr(model, 'totalResults'), "List response should have 'totalResults' field"

    def test_resource_work_skill_list_response_validation(self, response_examples_path):
        """Validate ResourceWorkSkillListResponse model against saved response examples.
        
        Tests against endpoints: #177
        """
        response_files = [
            "177_get_resources_33035_workSkills_33035.json",
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
                        model_instance = ResourceWorkSkillListResponse(**data)
                        self._validate_resource_work_skill_list_response_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"ResourceWorkSkillListResponse validation failed for {filename}: {e}")
                    
                    # Also validate individual items using the item model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = ResourceWorkSkill(**item)
                            print(f"✅ Validated {filename} item {idx} with ResourceWorkSkill")
                        except ValidationError as e:
                            pytest.fail(f"ResourceWorkSkill validation failed for {filename} item {idx}: {e}")
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = ResourceWorkSkillListResponse(**item)
                            self._validate_resource_work_skill_list_response_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(f"ResourceWorkSkillListResponse validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = ResourceWorkSkillListResponse(**data)
                    self._validate_resource_work_skill_list_response_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"ResourceWorkSkillListResponse validation failed for {filename}: {e}")
    
    def _validate_resource_work_skill_list_response_fields(self, model: ResourceWorkSkillListResponse, original_data: dict):
        """Validate specific fields for ResourceWorkSkillListResponse."""
        # Add model-specific field validations here
        # List response validations
        assert hasattr(model, 'items'), "List response should have 'items' field"
        assert hasattr(model, 'totalResults'), "List response should have 'totalResults' field"

    def test_subscription_list_validation(self, response_examples_path):
        """Validate SubscriptionList model against saved response examples.
        
        Tests against endpoints: #149
        """
        response_files = [
            "149_get_subscriptions.json",
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
                        model_instance = SubscriptionList(**data)
                        self._validate_subscription_list_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"SubscriptionList validation failed for {filename}: {e}")
                    
                    # Also validate individual items using the item model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = Subscription(**item)
                            print(f"✅ Validated {filename} item {idx} with Subscription")
                        except ValidationError as e:
                            pytest.fail(f"Subscription validation failed for {filename} item {idx}: {e}")
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = SubscriptionList(**item)
                            self._validate_subscription_list_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(f"SubscriptionList validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = SubscriptionList(**data)
                    self._validate_subscription_list_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"SubscriptionList validation failed for {filename}: {e}")
    
    def _validate_subscription_list_fields(self, model: SubscriptionList, original_data: dict):
        """Validate specific fields for SubscriptionList."""
        # Add model-specific field validations here
        pass  # Add specific field validations as needed

    def test_daily_extract_folders_validation(self, response_examples_path):
        """Validate DailyExtractFolders model against saved response examples.
        
        Tests against endpoints: #144
        """
        response_files = [
            "144_get_daily_extract_dates.json",
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
                        model_instance = DailyExtractFolders(**data)
                        self._validate_daily_extract_folders_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"DailyExtractFolders validation failed for {filename}: {e}")
                    
                    # Also validate individual items using the item model
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = DailyExtractFolders(**item)
                            self._validate_daily_extract_folders_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(f"DailyExtractFolders validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = DailyExtractFolders(**data)
                    self._validate_daily_extract_folders_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"DailyExtractFolders validation failed for {filename}: {e}")
    
    def _validate_daily_extract_folders_fields(self, model: DailyExtractFolders, original_data: dict):
        """Validate specific fields for DailyExtractFolders."""
        # Add model-specific field validations here
        pass  # Add specific field validations as needed

    def test_activity_customer_inventory_list_response_validation(self, response_examples_path):
        """Validate ActivityCustomerInventoryListResponse model against saved response examples.
        
        Tests against endpoints: #120
        """
        response_files = [
            "120_get_activities_3951883_customerInventories_3951883.json",
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
                        model_instance = ActivityCustomerInventoryListResponse(**data)
                        self._validate_activity_customer_inventory_list_response_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"ActivityCustomerInventoryListResponse validation failed for {filename}: {e}")
                    
                    # Also validate individual items using the item model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = ActivityCustomerInventory(**item)
                            print(f"✅ Validated {filename} item {idx} with ActivityCustomerInventory")
                        except ValidationError as e:
                            pytest.fail(f"ActivityCustomerInventory validation failed for {filename} item {idx}: {e}")
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = ActivityCustomerInventoryListResponse(**item)
                            self._validate_activity_customer_inventory_list_response_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(f"ActivityCustomerInventoryListResponse validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = ActivityCustomerInventoryListResponse(**data)
                    self._validate_activity_customer_inventory_list_response_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"ActivityCustomerInventoryListResponse validation failed for {filename}: {e}")
    
    def _validate_activity_customer_inventory_list_response_fields(self, model: ActivityCustomerInventoryListResponse, original_data: dict):
        """Validate specific fields for ActivityCustomerInventoryListResponse."""
        # Add model-specific field validations here
        # List response validations
        assert hasattr(model, 'items'), "List response should have 'items' field"
        assert hasattr(model, 'totalResults'), "List response should have 'totalResults' field"

    def test_resource_work_zone_list_response_validation(self, response_examples_path):
        """Validate ResourceWorkZoneListResponse model against saved response examples.
        
        Tests against endpoints: #180
        """
        response_files = [
            "180_get_resources_33035_workZones_33035.json",
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
                        model_instance = ResourceWorkZoneListResponse(**data)
                        self._validate_resource_work_zone_list_response_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"ResourceWorkZoneListResponse validation failed for {filename}: {e}")
                    
                    # Also validate individual items using the item model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = ResourceWorkZone(**item)
                            print(f"✅ Validated {filename} item {idx} with ResourceWorkZone")
                        except ValidationError as e:
                            pytest.fail(f"ResourceWorkZone validation failed for {filename} item {idx}: {e}")
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = ResourceWorkZoneListResponse(**item)
                            self._validate_resource_work_zone_list_response_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(f"ResourceWorkZoneListResponse validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = ResourceWorkZoneListResponse(**data)
                    self._validate_resource_work_zone_list_response_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"ResourceWorkZoneListResponse validation failed for {filename}: {e}")
    
    def _validate_resource_work_zone_list_response_fields(self, model: ResourceWorkZoneListResponse, original_data: dict):
        """Validate specific fields for ResourceWorkZoneListResponse."""
        # Add model-specific field validations here
        # List response validations
        assert hasattr(model, 'items'), "List response should have 'items' field"
        assert hasattr(model, 'totalResults'), "List response should have 'totalResults' field"
