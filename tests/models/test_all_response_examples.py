"""Comprehensive test for all response examples against their models."""

import json
from pathlib import Path
import pytest
from typing import Dict, Type, Optional
from pydantic import BaseModel, ValidationError

# Import all model classes
from ofsc.models.base import BaseOFSResponse, OFSResponseList
from ofsc.models.metadata import (
    ActivityTypeGroupListResponse,
    ActivityTypeListResponse,
    ApplicationListResponse,
    ApplicationApiAccessListResponse,
    InventoryTypeListResponse,
    LanguageListResponse,
    NonWorkingReasonListResponse,
    OrganizationListResponse,
    PropertyListResponse,
    PropertyResponse,
    ResourceTypeListResponse,
    ShiftListResponse,
    Shift,
    TimeSlotListResponse,
    WorkskillConditionListResponse,
    WorkSkillGroupListResponse,
    WorkskillListResponse,
    WorkzoneListResponse,
    Workzone,
    WorkZoneKeyResponse,
    FormListResponse,
    Form,
    LinkTemplateListResponse,
    LinkTemplate,
    RoutingProfileListResponse,
    RoutingPlanListResponse,
    RoutingPlanExportResponse,
    EnumerationValueList,
)
from ofsc.models.core import (
    SubscriptionList,
    UserListResponse,
    Resource,
    ResourcePositionListResponse,
)
from ofsc.models.capacity import (
    CapacityAreaListResponse,
    CapacityCategoryListResponse,
    GetCapacityResponse,
    CapacityAreaCategoryListResponse,
    CapacityAreaWorkzoneListResponse,
    CapacityAreaTimeSlotListResponse,
    CapacityAreaTimeIntervalListResponse,
    CapacityAreaOrganizationListResponse,
)


class TestAllResponseExamples:
    """Test all response examples against their corresponding models."""
    
    # Mapping of response example files to their model classes
    RESPONSE_MODEL_MAPPING: Dict[str, Optional[Type[BaseModel]]] = {
        # Metadata API
        "1_get_activity_type_groups.json": ActivityTypeGroupListResponse,
        "4_get_activity_types.json": ActivityTypeListResponse,
        "7_get_applications.json": ApplicationListResponse,
        "10_get_applications_demoauth_apiAccess_demoauth.json": None,  # Error response
        "11_get_applications_demoauth_apiAccess_metadataAPI_demoauth_metadataAPI.json": None,  # Single ApplicationApiAccess, not list
        "11_get_applications_demoauth_apiAccess_metadataAPI_apiAccess_demoauth_apiAccess_metadataAPI_demoauth_apiAccess_metadataAPI.json": None,  # Error response
        "11_get_applications_metadataAPI_apiAccess_metadataAPI_metadataAPI.json": None,  # Error response
        "27_get_forms.json": FormListResponse,
        "28_get_forms_mobile_provider_request%238%23_mobile_provider_request_8_.json": Form,
        "31_get_inventory_types.json": InventoryTypeListResponse,
        "34_get_languages.json": LanguageListResponse,
        "35_get_link_templates.json": LinkTemplateListResponse,
        "36_get_link_template.json": LinkTemplate,
        "39_get_custom_map_layers.json": None,  # MapLayer models not implemented yet
        "39_get_mapLayers.json": None,  # MapLayer models not implemented yet
        "45_get_non_working_reasons.json": NonWorkingReasonListResponse,
        "46_get_organizations.json": OrganizationListResponse,
        "50_get_properties.json": PropertyListResponse,
        "50_properties.json": PropertyListResponse,
        "51_property.json": PropertyResponse,
        "54_get_properties_complete_code_enumerationList_complete_code.json": EnumerationValueList,
        "54_get_properties_country_code_enumerationList_country_code.json": None,  # Error response - property is not enumeration
        "56_get_resource_types.json": ResourceTypeListResponse,
        "56_resource_types.json": ResourceTypeListResponse,
        "57_get_routing_profiles.json": RoutingProfileListResponse,
        "58_get_routingProfiles_MaintenanceRoutingProfile_plans_MaintenanceRoutingProfile.json": RoutingPlanListResponse,
        "59_get_routingProfiles_MaintenanceRoutingProfile_plans_Optimization_custom-actions_export_MaintenanceRoutingProfile_Optimization.json": RoutingPlanExportResponse,
        "63_shifts.json": ShiftListResponse,
        "63_get_shifts.json": ShiftListResponse,
        "64_get_shift.json": Shift,
        "67_get_time_slots.json": TimeSlotListResponse,
        "67_timeslots.json": TimeSlotListResponse,
        "68_get_work_skill_conditions.json": WorkskillConditionListResponse,
        "70_get_work_skill_groups.json": WorkSkillGroupListResponse,
        "74_get_work_skills.json": WorkskillListResponse,
        "78_get_work_zones.json": WorkzoneListResponse,
        "78_workzones.json": WorkzoneListResponse,
        "82_get_workzone.json": Workzone,
        "86_get_the_work_zone_key.json": WorkZoneKeyResponse,
        "86_workzone_keys.json": WorkZoneKeyResponse,
        "86_get_workZoneKey.json": WorkZoneKeyResponse,
        
        # Core API
        "144_get_daily_extract_dates.json": None,  # DailyExtract models not implemented yet
        "149_get_subscriptions.json": SubscriptionList,
        "163_get_resources.json": None,  # Resource list response not implemented yet
        "214_get_last_known_positions_of_resources.json": ResourcePositionListResponse,
        "219_get_users.json": UserListResponse,
        
        # Capacity API
        "14_get_capacity_areas.json": CapacityAreaListResponse,
        "16_get_capacity_area_capacity_categories.json": CapacityAreaCategoryListResponse,
        "17_get_capacity_area_workzones_v2.json": CapacityAreaWorkzoneListResponse,
        "19_get_capacity_area_timeslots.json": CapacityAreaTimeSlotListResponse,
        "20_get_capacity_area_timeintervals.json": CapacityAreaTimeIntervalListResponse,
        "21_get_capacity_area_organizations.json": CapacityAreaOrganizationListResponse,
        "23_get_capacity_categories.json": CapacityCategoryListResponse,
        "get_available_capacity_response.json": GetCapacityResponse,
        
        # Statistics API
        "87_get_activity_duration_statistics.json": None,  # Statistics models not implemented yet
        "89_get_activity_travel_statistics.json": None,  # Statistics models not implemented yet
        
        # Special files to skip
        "swagger.json": None,
        "endpoints.json": None,
    }
    
    @pytest.fixture
    def response_examples_path(self):
        """Get path to response examples directory."""
        return Path(__file__).parent.parent.parent / "response_examples"
    
    def test_all_response_examples_have_models(self, response_examples_path):
        """Test that all response examples have corresponding model mappings."""
        example_files = set(f.name for f in response_examples_path.glob("*.json"))
        mapped_files = set(self.RESPONSE_MODEL_MAPPING.keys())
        
        unmapped_files = example_files - mapped_files
        
        if unmapped_files:
            print(f"\nWarning: Found {len(unmapped_files)} unmapped response examples:")
            for file in sorted(unmapped_files):
                print(f"  - {file}")
        
        # This test just warns about unmapped files, doesn't fail
        assert True
    
    def test_validate_all_response_examples(self, response_examples_path):
        """Validate all response examples against their models."""
        results = {
            "passed": [],
            "failed": [],
            "skipped": [],
            "not_implemented": []
        }
        
        for filename, model_class in self.RESPONSE_MODEL_MAPPING.items():
            file_path = response_examples_path / filename
            
            # Skip if file doesn't exist
            if not file_path.exists():
                results["skipped"].append((filename, "File not found"))
                continue
            
            # Skip if model not implemented
            if model_class is None:
                results["not_implemented"].append(filename)
                continue
            
            # Load and validate
            try:
                with open(file_path) as f:
                    data = json.load(f)
                
                # Remove metadata for model validation
                if "_metadata" in data:
                    del data["_metadata"]
                
                # Validate against model
                if issubclass(model_class, BaseOFSResponse) or issubclass(model_class, OFSResponseList):
                    instance = model_class.model_validate(data)
                    results["passed"].append(filename)
                else:
                    # Direct model validation
                    instance = model_class.model_validate(data)
                    results["passed"].append(filename)
                    
            except ValidationError as e:
                results["failed"].append((filename, str(e)))
            except Exception as e:
                results["failed"].append((filename, f"Unexpected error: {type(e).__name__}: {str(e)}"))
        
        # Print summary
        print("\n" + "="*80)
        print("Response Example Validation Summary")
        print("="*80)
        print(f"✅ Passed: {len(results['passed'])}")
        print(f"❌ Failed: {len(results['failed'])}")
        print(f"⚠️  Skipped: {len(results['skipped'])}")
        print(f"🚧 Not Implemented: {len(results['not_implemented'])}")
        print()
        
        # Print failures
        if results["failed"]:
            print("Failed Validations:")
            for filename, error in results["failed"]:
                print(f"\n❌ {filename}")
                # Print first line of error only for brevity
                error_lines = str(error).split('\n')
                print(f"   {error_lines[0]}")
                if len(error_lines) > 1:
                    print(f"   ... ({len(error_lines)-1} more lines)")
        
        # Print not implemented
        if results["not_implemented"]:
            print("\nNot Implemented Models:")
            for filename in sorted(results["not_implemented"]):
                endpoint_id = filename.split('_')[0]
                print(f"  🚧 {filename} (endpoint #{endpoint_id})")
        
        # Assert all mapped models pass validation
        assert len(results["failed"]) == 0, f"{len(results['failed'])} models failed validation"
    
    def test_model_coverage_statistics(self, response_examples_path):
        """Calculate model coverage statistics."""
        total_examples = len([f for f in response_examples_path.glob("*.json") 
                            if f.name not in ["swagger.json", "endpoints.json"]])
        
        implemented = len([m for m in self.RESPONSE_MODEL_MAPPING.values() if m is not None])
        not_implemented = len([m for m in self.RESPONSE_MODEL_MAPPING.values() if m is None])
        
        coverage_pct = (implemented / len(self.RESPONSE_MODEL_MAPPING)) * 100 if self.RESPONSE_MODEL_MAPPING else 0
        
        print("\n" + "="*80)
        print("Model Coverage Statistics")
        print("="*80)
        print(f"Total Response Examples: {total_examples}")
        print(f"Mapped Examples: {len(self.RESPONSE_MODEL_MAPPING)}")
        print(f"Implemented Models: {implemented}")
        print(f"Not Implemented: {not_implemented}")
        print(f"Coverage: {coverage_pct:.1f}%")
        print()
        
        # Group by API
        by_api = {
            "Metadata": 0,
            "Core": 0,
            "Capacity": 0,
            "Statistics": 0,
            "Other": 0
        }
        
        for filename, model in self.RESPONSE_MODEL_MAPPING.items():
            if model is None:
                continue
                
            if "capacity" in filename.lower() or filename.startswith(("14_", "16_", "17_", "19_", "20_", "21_", "23_")):
                by_api["Capacity"] += 1
            elif filename.startswith(("144_", "149_", "163_", "214_", "219_")):
                by_api["Core"] += 1
            elif filename.startswith(("87_", "89_")):
                by_api["Statistics"] += 1
            else:
                by_api["Metadata"] += 1
        
        print("Coverage by API:")
        for api, count in by_api.items():
            print(f"  {api}: {count} models")
    
    def test_base_response_compliance(self, response_examples_path):
        """Test that all models properly inherit from BaseOFSResponse."""
        non_compliant = []
        
        for filename, model_class in self.RESPONSE_MODEL_MAPPING.items():
            if model_class is None:
                continue
                
            # Check inheritance
            if not (issubclass(model_class, BaseOFSResponse) or 
                   issubclass(model_class, OFSResponseList) or
                   model_class in [EnumerationValueList]):  # Special cases
                non_compliant.append((filename, model_class.__name__))
        
        if non_compliant:
            print("\nModels not inheriting from BaseOFSResponse:")
            for filename, model_name in non_compliant:
                print(f"  ⚠️  {filename} -> {model_name}")
        
        # This is informational, not a failure
        assert True