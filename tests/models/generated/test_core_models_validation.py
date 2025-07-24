"""
Model validation tests for Core API responses.

This file contains comprehensive validation tests for all Core API models
against real API response examples.

Generated on: 2025-07-24 22:47:58 UTC
"""

import json
from pathlib import Path
import pytest
from pydantic import ValidationError

# Import the actual models
from ofsc.models.core import Activity, ActivityListResponse, ActivityProperty, AssignedLocationsResponse, DailyExtractFiles, DailyExtractFolders, Inventory, LocationListResponse, Resource, ResourceListResponse, RouteInfo, SubscriptionList, User, UserListResponse

class TestCoreModelsValidation:
    """Test Core API model validation against response examples."""
    
    @pytest.fixture
    def response_examples_path(self):
        """Path to response examples directory."""
        # Go up from tests/models/generated/ to project root, then to response_examples
        return Path(__file__).parent.parent.parent.parent / "response_examples"

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
                if "ListResponse" in "UserListResponse":
                    # Validate the entire list response
                    try:
                        model_instance = UserListResponse(**data)
                        self._validate_user_list_response_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"UserListResponse validation failed for {filename}: {e}")
                else:
                    # Validate individual items (for single model types)
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

    def test_location_list_response_validation(self, response_examples_path):
        """Validate LocationListResponse model against saved response examples.
        
        Tests against endpoints: #191, #192
        """
        response_files = [
            "191_get_resources_33035_locations_33035.json",
            "191_get_resources_33135_locations_33135.json",
            "192_get_resources_33035_locations_25_33035_25.json",
            "192_get_resources_33035_locations_mine_33035_mine.json",
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
                if "ListResponse" in "LocationListResponse":
                    # Validate the entire list response
                    try:
                        model_instance = LocationListResponse(**data)
                        self._validate_location_list_response_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"LocationListResponse validation failed for {filename}: {e}")
                else:
                    # Validate individual items (for single model types)
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
                if "ListResponse" in "Activity":
                    # Validate the entire list response
                    try:
                        model_instance = Activity(**data)
                        self._validate_activity_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"Activity validation failed for {filename}: {e}")
                else:
                    # Validate individual items (for single model types)
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
                if "ListResponse" in "Resource":
                    # Validate the entire list response
                    try:
                        model_instance = Resource(**data)
                        self._validate_resource_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"Resource validation failed for {filename}: {e}")
                else:
                    # Validate individual items (for single model types)
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

    def test_activity_list_response_validation(self, response_examples_path):
        """Validate ActivityListResponse model against saved response examples.
        
        Tests against endpoints: #104
        """
        response_files = [
            "104_get_activities.json",
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
                if "ListResponse" in "ActivityListResponse":
                    # Validate the entire list response
                    try:
                        model_instance = ActivityListResponse(**data)
                        self._validate_activity_list_response_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"ActivityListResponse validation failed for {filename}: {e}")
                else:
                    # Validate individual items (for single model types)
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = ActivityListResponse(**item)
                            self._validate_activity_list_response_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(f"ActivityListResponse validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = ActivityListResponse(**data)
                    self._validate_activity_list_response_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"ActivityListResponse validation failed for {filename}: {e}")
    
    def _validate_activity_list_response_fields(self, model: ActivityListResponse, original_data: dict):
        """Validate specific fields for ActivityListResponse."""
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
                if "ListResponse" in "ResourceListResponse":
                    # Validate the entire list response
                    try:
                        model_instance = ResourceListResponse(**data)
                        self._validate_resource_list_response_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"ResourceListResponse validation failed for {filename}: {e}")
                else:
                    # Validate individual items (for single model types)
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
                if "ListResponse" in "User":
                    # Validate the entire list response
                    try:
                        model_instance = User(**data)
                        self._validate_user_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"User validation failed for {filename}: {e}")
                else:
                    # Validate individual items (for single model types)
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
                if "ListResponse" in "AssignedLocationsResponse":
                    # Validate the entire list response
                    try:
                        model_instance = AssignedLocationsResponse(**data)
                        self._validate_assigned_locations_response_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"AssignedLocationsResponse validation failed for {filename}: {e}")
                else:
                    # Validate individual items (for single model types)
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

    def test_route_info_validation(self, response_examples_path):
        """Validate RouteInfo model against saved response examples.
        
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
                if "ListResponse" in "RouteInfo":
                    # Validate the entire list response
                    try:
                        model_instance = RouteInfo(**data)
                        self._validate_route_info_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"RouteInfo validation failed for {filename}: {e}")
                else:
                    # Validate individual items (for single model types)
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = RouteInfo(**item)
                            self._validate_route_info_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(f"RouteInfo validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = RouteInfo(**data)
                    self._validate_route_info_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"RouteInfo validation failed for {filename}: {e}")
    
    def _validate_route_info_fields(self, model: RouteInfo, original_data: dict):
        """Validate specific fields for RouteInfo."""
        # Add model-specific field validations here
        pass  # Add specific field validations as needed

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
                if "ListResponse" in "Inventory":
                    # Validate the entire list response
                    try:
                        model_instance = Inventory(**data)
                        self._validate_inventory_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"Inventory validation failed for {filename}: {e}")
                else:
                    # Validate individual items (for single model types)
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
                if "ListResponse" in "DailyExtractFiles":
                    # Validate the entire list response
                    try:
                        model_instance = DailyExtractFiles(**data)
                        self._validate_daily_extract_files_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"DailyExtractFiles validation failed for {filename}: {e}")
                else:
                    # Validate individual items (for single model types)
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

    def test_activity_property_validation(self, response_examples_path):
        """Validate ActivityProperty model against saved response examples.
        
        Tests against endpoints: #110
        """
        response_files = [
            "110_get_activities_3951883_csign_3951883_csign.json",
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
                if "ListResponse" in "ActivityProperty":
                    # Validate the entire list response
                    try:
                        model_instance = ActivityProperty(**data)
                        self._validate_activity_property_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"ActivityProperty validation failed for {filename}: {e}")
                else:
                    # Validate individual items (for single model types)
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = ActivityProperty(**item)
                            self._validate_activity_property_fields(model_instance, item)
                            print(f"✅ Validated {filename} item {idx}")
                        except ValidationError as e:
                            pytest.fail(f"ActivityProperty validation failed for {filename} item {idx}: {e}")
            else:
                # Validate single response
                try:
                    model_instance = ActivityProperty(**data)
                    self._validate_activity_property_fields(model_instance, data)
                    print(f"✅ Validated {filename}")
                except ValidationError as e:
                    pytest.fail(f"ActivityProperty validation failed for {filename}: {e}")
    
    def _validate_activity_property_fields(self, model: ActivityProperty, original_data: dict):
        """Validate specific fields for ActivityProperty."""
        # Add model-specific field validations here
        pass  # Add specific field validations as needed

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
                if "ListResponse" in "SubscriptionList":
                    # Validate the entire list response
                    try:
                        model_instance = SubscriptionList(**data)
                        self._validate_subscription_list_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"SubscriptionList validation failed for {filename}: {e}")
                else:
                    # Validate individual items (for single model types)
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
                if "ListResponse" in "DailyExtractFolders":
                    # Validate the entire list response
                    try:
                        model_instance = DailyExtractFolders(**data)
                        self._validate_daily_extract_folders_fields(model_instance, data)
                        print(f"✅ Validated {filename} as list response")
                    except ValidationError as e:
                        pytest.fail(f"DailyExtractFolders validation failed for {filename}: {e}")
                else:
                    # Validate individual items (for single model types)
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
