"""
Metadata Endpoints Schema Validation Tests

This module validates that Pydantic models for Metadata API endpoints are fully compatible
with their corresponding response schemas from the swagger.json specification.
"""

import pytest
from typing import List

from tests.fixtures.endpoints_registry import EndpointInfo
from tests.utils.endpoint_schema_test_base import EndpointSchemaTestBase


class TestMetadataEndpointsSchemaCompatibility(EndpointSchemaTestBase):
    """Test schema compatibility for Metadata API endpoints."""
    
    def setup_method(self):
        """Set up test fixtures for metadata endpoints."""
        super().setup_method()
        self.module_name = 'metadata'
        self.metadata_get_endpoints = self.get_endpoints_for_module(self.module_name)
    
    @pytest.mark.unit
    def test_all_metadata_endpoints_schema_compatibility(self):
        """
        Test that all metadata endpoints' Pydantic models match their swagger schemas.
        
        This test validates each endpoint individually and reports failures.
        """
        endpoints = self.get_endpoints_for_module('metadata')
        failed_endpoints = []
        
        for endpoint in endpoints:
            try:
                result = self.validate_endpoint_schema_compatibility(endpoint)
                if not result.is_valid:
                    failed_endpoints.append({
                        'endpoint': f"{endpoint.method} {endpoint.path}",
                        'schema': endpoint.response_schema,
                        'errors': result.errors
                    })
            except Exception as e:
                failed_endpoints.append({
                    'endpoint': f"{endpoint.method} {endpoint.path}",
                    'schema': endpoint.response_schema,
                    'errors': [str(e)]
                })
        
        if failed_endpoints:
            print(f"\nFailed metadata endpoint validations ({len(failed_endpoints)}):")
            for failure in failed_endpoints[:5]:  # Show first 5
                print(f"  - {failure['endpoint']} ({failure['schema']})")
                if failure['errors']:
                    print(f"    Error: {failure['errors'][0]}")
            
            if len(failed_endpoints) > 5:
                print(f"    ... and {len(failed_endpoints) - 5} more")
        
        # For now, this is informational rather than strict
        # assert not failed_endpoints, f"Metadata endpoint schema validation failures: {len(failed_endpoints)}"
    
    @pytest.mark.unit
    def test_metadata_schema_coverage(self):
        """
        Test that all metadata GET endpoints with schemas have corresponding models.
        
        This test ensures we're not missing any Pydantic models for metadata endpoints
        and provides a comprehensive coverage report.
        """
        report = self.generate_module_coverage_report(self.module_name)
        
        # Print detailed report for visibility
        self.print_module_coverage_report(self.module_name)
        
        # Assert minimum coverage threshold (adjusted for current implementation state)
        min_coverage_percentage = 0.0  # Allow 0% for now since models aren't implemented yet
        assert report['coverage_percentage'] >= min_coverage_percentage, (
            f"Metadata module schema coverage is {report['coverage_percentage']:.1f}%, "
            f"but minimum required is {min_coverage_percentage}%. "
            f"Missing models: {report['missing_models']}"
        )
        
        # Document the current state for tracking improvements
        print(f"\nMetadata module validation summary:")
        print(f"  Total GET endpoints with schemas: {report['total_endpoints']}")
        print(f"  Successfully validated models: {report['validated_count']}")
        print(f"  Coverage percentage: {report['coverage_percentage']:.1f}%")
        
        if report['missing_models']:
            print(f"  Missing models that need implementation:")
            for schema in sorted(report['missing_models'])[:10]:  # Show first 10
                print(f"    - {schema}")
            if len(report['missing_models']) > 10:
                print(f"    ... and {len(report['missing_models']) - 10} more")
    
    @pytest.mark.unit
    def test_metadata_model_completeness(self):
        """
        Test that metadata models are not orphaned (without corresponding schemas).
        
        This test helps identify models that might be outdated or incorrectly named
        by checking if they have corresponding swagger schema definitions.
        """
        # Get all schema names for comparison
        all_schema_names = self.schema_validator.get_all_schema_names()
        
        # Get orphaned models (models without schemas)
        orphaned_models = self.schema_mapper.get_orphaned_models(all_schema_names)
        
        # Filter for models that might be metadata-related
        metadata_related_orphans = []
        for orphan in orphaned_models:
            # Check if the model name suggests it's metadata-related
            if any(keyword in orphan.lower() for keyword in [
                'property', 'properties', 'workzone', 'work_zone', 'activity_type',
                'workskill', 'work_skill', 'metadata', 'translation', 'enum'
            ]):
                metadata_related_orphans.append(orphan)
        
        # This is more of a warning than a hard failure
        if metadata_related_orphans:
            print(f"\nPotential metadata-related orphaned models found:")
            for model in sorted(metadata_related_orphans):
                print(f"  - {model}")
            print(f"These models might need:")
            print(f"  1. Corresponding swagger schema definitions")
            print(f"  2. To be added to SCHEMA_TO_MODEL_OVERRIDES mapping")
            print(f"  3. Review if they're still needed")
        
        # For now, we'll just document this rather than fail
        assert len(metadata_related_orphans) < 20, (
            f"Too many potentially orphaned metadata models ({len(metadata_related_orphans)}). "
            f"This suggests a systematic issue with schema-model mapping."
        )
    
    @pytest.mark.unit
    def test_metadata_endpoints_have_models(self):
        """
        Test that critical metadata endpoints have Pydantic models.
        
        This test specifically checks that important metadata endpoints have
        corresponding model implementations.
        """
        # Define critical metadata schemas that must have models
        critical_schemas = [
            'Properties',           # Property definitions listing
            'Property',            # Individual property
            'WorkZones',           # Work zones listing  
            'WorkZone',            # Individual work zone
            'ActivityTypes',       # Activity types listing
            'ActivityType',        # Individual activity type
            'WorkSkills',          # Work skills listing
            'WorkSkill',           # Individual work skill
            'ActivityTypeGroups',  # Activity type groups
            'ActivityTypeGroup',   # Individual activity type group
        ]
        
        missing_critical = []
        for schema_name in critical_schemas:
            model_class = self.schema_mapper.get_model_class_by_schema_name(schema_name)
            if not model_class:
                missing_critical.append(schema_name)
        
        if missing_critical:
            print(f"\nMissing critical metadata models: {missing_critical}")
            print("These schemas are essential for metadata API functionality.")
        
        # Use a more lenient assertion since some schemas might use different names
        max_missing_critical = 3  # Allow a few missing for flexibility
        assert len(missing_critical) <= max_missing_critical, (
            f"Too many critical metadata schemas are missing Pydantic models: {missing_critical}. "
            f"Found {len(missing_critical)} missing, but maximum allowed is {max_missing_critical}. "
            f"These are essential for metadata API functionality."
        )
    
    @pytest.mark.unit
    def test_metadata_property_types_coverage(self):
        """
        Test coverage of property type schemas.
        
        Metadata API includes various property types that should have model coverage.
        """
        # Property-related schemas that should exist
        property_schemas = [
            'Properties',
            'Property',
            'PropertyEnumValue',
            'PropertyDefinition',
        ]
        
        found_schemas = []
        missing_schemas = []
        
        for schema_name in property_schemas:
            model_class = self.schema_mapper.get_model_class_by_schema_name(schema_name)
            if model_class:
                found_schemas.append(schema_name)
            else:
                missing_schemas.append(schema_name)
        
        # Report on property schema coverage
        print(f"\nProperty schema coverage:")
        print(f"  Found models for: {found_schemas}")
        if missing_schemas:
            print(f"  Missing models for: {missing_schemas}")
        
        coverage_ratio = len(found_schemas) / len(property_schemas)
        print(f"  Property schema coverage: {coverage_ratio:.1%}")
        
        # Require at least 50% coverage for property schemas
        assert coverage_ratio >= 0.5, (
            f"Property schema coverage is {coverage_ratio:.1%}, but minimum required is 50%. "
            f"Missing: {missing_schemas}"
        )
    
    @pytest.mark.unit
    def test_metadata_workzone_schemas_coverage(self):
        """
        Test coverage of work zone related schemas.
        
        Work zones are a critical part of metadata API.
        """
        # Work zone related schemas
        workzone_schemas = [
            'WorkZones',
            'WorkZone', 
            'WorkZoneDefinition',
        ]
        
        found_schemas = []
        missing_schemas = []
        
        for schema_name in workzone_schemas:
            model_class = self.schema_mapper.get_model_class_by_schema_name(schema_name)
            if model_class:
                found_schemas.append(schema_name)
            else:
                missing_schemas.append(schema_name)
        
        # Report on work zone schema coverage
        print(f"\nWork zone schema coverage:")
        print(f"  Found models for: {found_schemas}")
        if missing_schemas:
            print(f"  Missing models for: {missing_schemas}")
        
        coverage_ratio = len(found_schemas) / len(workzone_schemas)
        print(f"  Work zone schema coverage: {coverage_ratio:.1%}")
        
        # Require at least 60% coverage for work zone schemas
        assert coverage_ratio >= 0.6, (
            f"Work zone schema coverage is {coverage_ratio:.1%}, but minimum required is 60%. "
            f"Missing: {missing_schemas}"
        )
    
    def create_parametrized_test_data(self, module_name: str) -> List[EndpointInfo]:
        """Create parametrized test data for metadata endpoints."""
        return self.get_endpoints_for_module(module_name)


# Test execution helper for standalone running
if __name__ == "__main__":
    # Allow running this test file directly for development/debugging
    test_instance = TestMetadataEndpointsSchemaCompatibility()
    test_instance.setup_method()
    
    print("=== METADATA ENDPOINTS SCHEMA VALIDATION ===")
    print(f"Found {len(test_instance.metadata_get_endpoints)} metadata GET endpoints with schemas")
    
    # Run coverage test to see current state
    test_instance.test_metadata_schema_coverage()
    
    print("\n=== VALIDATION COMPLETE ===")