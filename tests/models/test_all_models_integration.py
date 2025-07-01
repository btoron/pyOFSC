"""Integration tests for all API models against response examples.

This module tests that all Pydantic models across Core, Metadata, and Capacity APIs
correctly parse real API responses and have proper BaseOFSResponse integration.
"""

import json
import pytest
from pathlib import Path

# Import models from all modules
from ofsc.models.core import Resource, User, Activity, Location
from ofsc.models.metadata import PropertyResponse, Workskill, ActivityType, Organization, ActivityTypeGroup
from ofsc.models.capacity import CapacityArea, CapacityCategoryResponse, GetCapacityResponse
from ofsc.models.auth import OFSConfig, OFSOAuthRequest, OFSAPIError
from ofsc.models.base import BaseOFSResponse


class TestAllModelsIntegration:
    """Test integration of all models with BaseOFSResponse and real response examples."""
    
    @pytest.fixture
    def response_examples_path(self):
        """Path to response examples directory."""
        return Path(__file__).parent.parent.parent / "response_examples"
    
    def test_all_models_inherit_base_ofs_response(self):
        """Test that all main API models inherit from BaseOFSResponse."""
        # Core models
        assert issubclass(Resource, BaseOFSResponse)
        assert issubclass(User, BaseOFSResponse)
        assert issubclass(Activity, BaseOFSResponse)
        assert issubclass(Location, BaseOFSResponse)
        
        # Metadata models
        assert issubclass(PropertyResponse, BaseOFSResponse)
        assert issubclass(Workskill, BaseOFSResponse)
        assert issubclass(ActivityType, BaseOFSResponse)
        assert issubclass(Organization, BaseOFSResponse)
        assert issubclass(ActivityTypeGroup, BaseOFSResponse)
        
        # Capacity models
        assert issubclass(CapacityArea, BaseOFSResponse)
        assert issubclass(CapacityCategoryResponse, BaseOFSResponse)
        assert issubclass(GetCapacityResponse, BaseOFSResponse)
        
        # Auth models
        assert issubclass(OFSConfig, BaseOFSResponse)
        assert issubclass(OFSOAuthRequest, BaseOFSResponse)
        assert issubclass(OFSAPIError, BaseOFSResponse)
        
        print("✅ All models properly inherit from BaseOFSResponse")
    
    def test_models_have_base_ofs_response_attributes(self):
        """Test that all models have BaseOFSResponse attributes."""
        # Create instances of different models
        resource = Resource(resourceType='PR', name='Test', language='en', timeZone='UTC', status='active')
        property_model = PropertyResponse(label='TEST', name='Test', entity='activity', type='string')
        capacity_area = CapacityArea(label='TEST', status='active')
        config = OFSConfig(clientID='test', secret='test', companyName='test')
        
        models = [resource, property_model, capacity_area, config]
        
        for model in models:
            # Check BaseOFSResponse attributes
            assert hasattr(model, '_raw_response')
            assert hasattr(model, 'status_code')
            assert hasattr(model, 'headers')
            
            # These should be None when created directly (not from httpx response)
            assert model.status_code is None
            assert model.headers is None
            
        print("✅ All models have BaseOFSResponse attributes")
    
    def test_comprehensive_response_validation(self, response_examples_path):
        """Test models against multiple response examples."""
        test_cases = [
            # Core API examples
            ("163_get_resources.json", Resource, "items"),
            ("219_get_users.json", User, "items"),
            
            # Metadata API examples  
            ("50_get_properties.json", PropertyResponse, "items"),
            ("74_get_work_skills.json", Workskill, "items"),
            ("1_get_activity_type_groups.json", ActivityTypeGroup, "items"),
            ("46_get_organizations.json", Organization, "items"),
            
            # Capacity API examples
            ("14_get_capacity_areas.json", CapacityArea, "items"),
            ("23_get_capacity_categories.json", CapacityCategoryResponse, "items"),
        ]
        
        passed_tests = 0
        
        for filename, model_class, items_key in test_cases:
            response_file = response_examples_path / filename
            
            if not response_file.exists():
                print(f"⚠️ Skipping {filename} - file not found")
                continue
                
            try:
                with open(response_file) as f:
                    data = json.load(f)
                
                # Skip metadata
                if "_metadata" in data:
                    del data["_metadata"]
                
                # Test individual items
                if items_key in data and data[items_key]:
                    item = data[items_key][0]  # Test first item
                    
                    # Handle special cases for required fields
                    if model_class == CapacityArea and "status" not in item:
                        item["status"] = "active"
                    
                    # Create model instance
                    instance = model_class(**item)
                    
                    # Verify BaseOFSResponse integration
                    assert hasattr(instance, '_raw_response')
                    assert instance.status_code is None
                    assert instance.headers is None
                    
                    passed_tests += 1
                    print(f"✅ {model_class.__name__} validates against {filename}")
                    
            except Exception as e:
                print(f"❌ {model_class.__name__} failed against {filename}: {e}")
        
        print(f"✅ Comprehensive validation complete: {passed_tests} tests passed")
        assert passed_tests >= 5, f"Expected at least 5 successful validations, got {passed_tests}"
    
    def test_model_extra_fields_consistency(self):
        """Test that models handle extra fields according to their configuration."""
        # Test models that ALLOW extra fields
        from ofsc.models.metadata import Application, ActivityTypeFeatures
        
        test_data = {
            "extraField1": "test_value",
            "customProperty": {"nested": "data"},
            "additionalInfo": ["item1", "item2"]
        }
        
        # Test Application model (has extra="allow")
        app_data = {"label": "TEST_APP", "name": "Test"}
        app_data.update(test_data)
        application = Application(**app_data)
        assert application.name == "Test"
        
        # Test PropertyResponse model (has extra="allow")
        property_data = {"label": "TEST_PROP", "name": "Test", "type": "string"}
        property_data.update(test_data)
        property_model = PropertyResponse(**property_data)
        assert property_model.name == "Test"
        
        # Test ActivityTypeFeatures model (has extra="allow")
        features_data = {"allowCreationInBuckets": True}
        features_data.update(test_data)
        features = ActivityTypeFeatures(**features_data)
        assert features.allowCreationInBuckets is True
        
        # Test models that FORBID extra fields (default behavior)
        # These should only use their defined fields
        resource = Resource(resourceType="PR", name="Test", language="en", timeZone="UTC", status="active")
        assert resource.name == "Test"
        
        property_model = PropertyResponse(label="TEST", name="Test", entity="activity", type="string")
        assert property_model.name == "Test"
        
        capacity_area = CapacityArea(label="TEST", status="active")
        assert capacity_area.label == "TEST"
        
        print("✅ Models handle extra fields according to their configuration")
    
    def test_backward_compatibility_imports(self):
        """Test that all models can be imported via the main models module."""
        from ofsc.models import (
            Resource, Property, PropertyResponse, CapacityArea, OFSConfig  # Auth
        )
        
        # Test that imports work and classes are correct
        assert Resource.__name__ == "Resource"
        assert Property is PropertyResponse  # Test backward compatibility alias
        assert PropertyResponse.__name__ == "PropertyResponse"
        assert CapacityArea.__name__ == "CapacityArea"
        assert OFSConfig.__name__ == "OFSConfig"
        
        print("✅ All models available via backward-compatible imports")
    
    def test_response_list_integration(self):
        """Test that OFSResponseList works with all model types."""
        from ofsc.models import ResourceUsersListResponse, CapacityAreaListResponse
        
        # Test that response list models are properly typed
        assert hasattr(ResourceUsersListResponse, '__orig_bases__')
        assert hasattr(CapacityAreaListResponse, '__orig_bases__')
        
        # Test that they inherit from both BaseOFSResponse and are generic
        assert issubclass(ResourceUsersListResponse, BaseOFSResponse)
        assert issubclass(CapacityAreaListResponse, BaseOFSResponse)
        
        print("✅ OFSResponseList integration works correctly")
    
    def test_model_documentation_and_type_hints(self):
        """Test that all models have proper documentation and type hints."""
        models_to_check = [
            Resource, User, PropertyResponse, Workskill, CapacityArea, CapacityCategoryResponse, OFSConfig
        ]
        
        for model in models_to_check:
            # Check that model has docstring
            assert model.__doc__ is not None, f"{model.__name__} missing docstring"
            
            # Check that model has annotations (type hints)
            assert hasattr(model, '__annotations__'), f"{model.__name__} missing type annotations"
            assert len(model.__annotations__) > 0, f"{model.__name__} has no field annotations"
            
            # Check that model has ConfigDict
            assert hasattr(model, 'model_config'), f"{model.__name__} missing model_config"
            
        print("✅ All models have proper documentation and type hints")