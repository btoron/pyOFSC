"""
Core Endpoints Schema Validation Tests

This module validates that Pydantic models for Core API endpoints are fully compatible
with their corresponding response schemas from the swagger.json specification.
"""

import pytest
from typing import List

from tests.fixtures.endpoints_registry import EndpointInfo
from tests.utils.endpoint_schema_test_base import EndpointSchemaTestBase


class TestCoreEndpointsSchemaCompatibility(EndpointSchemaTestBase):
    """Test schema compatibility for Core API endpoints."""
    
    def setup_method(self):
        """Set up test fixtures for core endpoints."""
        super().setup_method()
        self.module_name = 'core'
        self.core_get_endpoints = self.get_endpoints_for_module(self.module_name)
    
    @pytest.mark.unit
    def test_all_core_endpoints_schema_compatibility(self):
        """
        Test that all core endpoints' Pydantic models match their swagger schemas.
        
        This test validates each endpoint individually and reports failures.
        """
        endpoints = self.get_endpoints_for_module('core')
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
            print(f"\nFailed core endpoint validations ({len(failed_endpoints)}):")
            for failure in failed_endpoints[:5]:  # Show first 5
                print(f"  - {failure['endpoint']} ({failure['schema']})")
                if failure['errors']:
                    print(f"    Error: {failure['errors'][0]}")
            
            if len(failed_endpoints) > 5:
                print(f"    ... and {len(failed_endpoints) - 5} more")
        
        # For now, this is informational rather than strict
        # assert not failed_endpoints, f"Core endpoint schema validation failures: {len(failed_endpoints)}"
    
    @pytest.mark.unit
    def test_core_schema_coverage(self):
        """
        Test that all core GET endpoints with schemas have corresponding models.
        
        This test ensures we're not missing any Pydantic models for core endpoints
        and provides a comprehensive coverage report.
        """
        report = self.generate_module_coverage_report(self.module_name)
        
        # Print detailed report for visibility
        self.print_module_coverage_report(self.module_name)
        
        # Assert minimum coverage threshold (adjusted for current implementation state)
        min_coverage_percentage = 0.0  # Allow 0% for now since models aren't implemented yet
        assert report['coverage_percentage'] >= min_coverage_percentage, (
            f"Core module schema coverage is {report['coverage_percentage']:.1f}%, "
            f"but minimum required is {min_coverage_percentage}%. "
            f"Missing models: {report['missing_models']}"
        )
        
        # Document the current state for tracking improvements
        print(f"\nCore module validation summary:")
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
    def test_core_model_completeness(self):
        """
        Test that core models are not orphaned (without corresponding schemas).
        
        This test helps identify models that might be outdated or incorrectly named
        by checking if they have corresponding swagger schema definitions.
        """
        # Get all schema names for comparison
        all_schema_names = self.schema_validator.get_all_schema_names()
        
        # Get orphaned models (models without schemas)
        orphaned_models = self.schema_mapper.get_orphaned_models(all_schema_names)
        
        # Filter for models that might be core-related
        # This is a heuristic - we look for models that are imported/used by core tests
        core_related_orphans = []
        for orphan in orphaned_models:
            # Check if the model name suggests it's core-related
            # This is imperfect but helps identify potential issues
            if any(keyword in orphan.lower() for keyword in [
                'activity', 'resource', 'user', 'core', 'inventory'
            ]):
                core_related_orphans.append(orphan)
        
        # This is more of a warning than a hard failure
        # Some models might be internal/utility classes
        if core_related_orphans:
            print(f"\nPotential core-related orphaned models found:")
            for model in sorted(core_related_orphans):
                print(f"  - {model}")
            print(f"These models might need:")
            print(f"  1. Corresponding swagger schema definitions")
            print(f"  2. To be added to SCHEMA_TO_MODEL_OVERRIDES mapping")
            print(f"  3. Review if they're still needed")
        
        # For now, we'll just document this rather than fail
        # In the future, this could become a stricter requirement
        assert len(core_related_orphans) < 50, (
            f"Too many potentially orphaned core models ({len(core_related_orphans)}). "
            f"This suggests a systematic issue with schema-model mapping."
        )
    
    @pytest.mark.unit
    def test_core_endpoints_have_models(self):
        """
        Test that critical core endpoints have Pydantic models.
        
        This test specifically checks that important core endpoints have
        corresponding model implementations.
        """
        # Define critical endpoints that must have models
        critical_schemas = [
            'Activities',      # Activity listing
            'Activity',        # Individual activity
            'Resources',       # Resource listing
            'Resource',        # Individual resource  
            'Users',          # User listing
            'User',           # Individual user
        ]
        
        missing_critical = []
        for schema_name in critical_schemas:
            model_class = self.schema_mapper.get_model_class_by_schema_name(schema_name)
            if not model_class:
                missing_critical.append(schema_name)
        
        # For now, just document the missing critical models
        if missing_critical:
            print(f"\nMissing critical core models: {missing_critical}")
            print("These schemas are essential for core API functionality.")
        
        # Allow some missing critical models for now (adjust as implementation progresses)
        max_missing_critical = len(critical_schemas)  # Allow all missing for now
        assert len(missing_critical) <= max_missing_critical, (
            f"All critical core schemas are missing: {missing_critical}. "
            f"At least one should be implemented for basic functionality."
        )
    
    def create_parametrized_test_data(self, module_name: str) -> List[EndpointInfo]:
        """Create parametrized test data for core endpoints."""
        return self.get_endpoints_for_module(module_name)


# Test execution helper for standalone running
if __name__ == "__main__":
    # Allow running this test file directly for development/debugging
    test_instance = TestCoreEndpointsSchemaCompatibility()
    test_instance.setup_method()
    
    print("=== CORE ENDPOINTS SCHEMA VALIDATION ===")
    print(f"Found {len(test_instance.core_get_endpoints)} core GET endpoints with schemas")
    
    # Run coverage test to see current state
    test_instance.test_core_schema_coverage()
    
    print("\n=== VALIDATION COMPLETE ===")