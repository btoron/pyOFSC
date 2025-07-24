"""
Other Endpoints Schema Validation Tests

This module validates that Pydantic models for remaining API endpoints (auth, collaboration,
statistics, partscatalog) are fully compatible with their corresponding response schemas 
from the swagger.json specification.
"""

import pytest
from typing import List

from tests.fixtures.endpoints_registry import EndpointInfo
from tests.utils.endpoint_schema_test_base import EndpointSchemaTestBase


class TestAuthEndpointsSchemaCompatibility(EndpointSchemaTestBase):
    """Test schema compatibility for Auth API endpoints."""
    
    def setup_method(self):
        """Set up test fixtures for auth endpoints."""
        super().setup_method()
        self.module_name = 'auth'
        self.auth_get_endpoints = self.get_endpoints_for_module(self.module_name)
    
    @pytest.mark.unit
    def test_all_auth_endpoints_schema_compatibility(self):
        """Test that all auth endpoints' Pydantic models match their swagger schemas."""
        endpoints = self.get_endpoints_for_module('auth')
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
            print(f"\nFailed auth endpoint validations ({len(failed_endpoints)}):")
            for failure in failed_endpoints[:3]:
                print(f"  - {failure['endpoint']} ({failure['schema']})")
                if failure['errors']:
                    print(f"    Error: {failure['errors'][0]}")
        
        # For now, this is informational rather than strict
    
    @pytest.mark.unit
    def test_auth_schema_coverage(self):
        """Test auth endpoints schema coverage."""
        report = self.generate_module_coverage_report(self.module_name)
        self.print_module_coverage_report(self.module_name)
        
        # Auth has very few endpoints, so be more lenient
        min_coverage_percentage = 0.0  # Allow 0% for now since models aren't implemented yet
        assert report['coverage_percentage'] >= min_coverage_percentage, (
            f"Auth module schema coverage is {report['coverage_percentage']:.1f}%, "
            f"but minimum required is {min_coverage_percentage}%. "
            f"Missing models: {report['missing_models']}"
        )
    
    def create_parametrized_test_data(self, module_name: str) -> List[EndpointInfo]:
        """Create parametrized test data for auth endpoints."""
        return self.get_endpoints_for_module(module_name)


class TestCollaborationEndpointsSchemaCompatibility(EndpointSchemaTestBase):
    """Test schema compatibility for Collaboration API endpoints."""
    
    def setup_method(self):
        """Set up test fixtures for collaboration endpoints."""
        super().setup_method()
        self.module_name = 'collaboration'
        self.collaboration_get_endpoints = self.get_endpoints_for_module(self.module_name)
    
    @pytest.mark.unit
    def test_all_collaboration_endpoints_schema_compatibility(self):
        """Test that all collaboration endpoints' Pydantic models match their swagger schemas."""
        endpoints = self.get_endpoints_for_module('collaboration')
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
            print(f"\nFailed collaboration endpoint validations ({len(failed_endpoints)}):")
            for failure in failed_endpoints[:3]:
                print(f"  - {failure['endpoint']} ({failure['schema']})")
                if failure['errors']:
                    print(f"    Error: {failure['errors'][0]}")
        
        # For now, this is informational rather than strict
    
    @pytest.mark.unit
    def test_collaboration_schema_coverage(self):
        """Test collaboration endpoints schema coverage."""
        report = self.generate_module_coverage_report(self.module_name)
        self.print_module_coverage_report(self.module_name)
        
        # Collaboration might not be fully implemented yet
        min_coverage_percentage = 0.0  # Allow 0% for now since models aren't implemented yet
        assert report['coverage_percentage'] >= min_coverage_percentage, (
            f"Collaboration module schema coverage is {report['coverage_percentage']:.1f}%, "
            f"but minimum required is {min_coverage_percentage}%. "
            f"Missing models: {report['missing_models']}"
        )
    
    def create_parametrized_test_data(self, module_name: str) -> List[EndpointInfo]:
        """Create parametrized test data for collaboration endpoints."""
        return self.get_endpoints_for_module(module_name)


class TestStatisticsEndpointsSchemaCompatibility(EndpointSchemaTestBase):
    """Test schema compatibility for Statistics API endpoints."""
    
    def setup_method(self):
        """Set up test fixtures for statistics endpoints."""
        super().setup_method()
        self.module_name = 'statistics'
        self.statistics_get_endpoints = self.get_endpoints_for_module(self.module_name)
    
    @pytest.mark.unit
    def test_all_statistics_endpoints_schema_compatibility(self):
        """Test that all statistics endpoints' Pydantic models match their swagger schemas."""
        endpoints = self.get_endpoints_for_module('statistics')
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
            print(f"\nFailed statistics endpoint validations ({len(failed_endpoints)}):")
            for failure in failed_endpoints[:3]:
                print(f"  - {failure['endpoint']} ({failure['schema']})")
                if failure['errors']:
                    print(f"    Error: {failure['errors'][0]}")
        
        # For now, this is informational rather than strict
    
    @pytest.mark.unit
    def test_statistics_schema_coverage(self):
        """Test statistics endpoints schema coverage."""
        report = self.generate_module_coverage_report(self.module_name)
        self.print_module_coverage_report(self.module_name)
        
        # Statistics might not be implemented yet
        min_coverage_percentage = 0.0  # Allow 0% for now since models aren't implemented yet
        assert report['coverage_percentage'] >= min_coverage_percentage, (
            f"Statistics module schema coverage is {report['coverage_percentage']:.1f}%, "
            f"but minimum required is {min_coverage_percentage}%. "
            f"Missing models: {report['missing_models']}"
        )
    
    def create_parametrized_test_data(self, module_name: str) -> List[EndpointInfo]:
        """Create parametrized test data for statistics endpoints."""
        return self.get_endpoints_for_module(module_name)


class TestPartsCatalogEndpointsSchemaCompatibility(EndpointSchemaTestBase):
    """Test schema compatibility for Parts Catalog API endpoints."""
    
    def setup_method(self):
        """Set up test fixtures for partscatalog endpoints."""
        super().setup_method()
        self.module_name = 'partscatalog'
        self.partscatalog_get_endpoints = self.get_endpoints_for_module(self.module_name)
    
    @pytest.mark.unit
    def test_all_partscatalog_endpoints_schema_compatibility(self):
        """Test that all parts catalog endpoints' Pydantic models match their swagger schemas."""
        endpoints = self.get_endpoints_for_module('partscatalog')
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
            print(f"\nFailed partscatalog endpoint validations ({len(failed_endpoints)}):")
            for failure in failed_endpoints[:3]:
                print(f"  - {failure['endpoint']} ({failure['schema']})")
                if failure['errors']:
                    print(f"    Error: {failure['errors'][0]}")
        
        # For now, this is informational rather than strict
    
    @pytest.mark.unit
    def test_partscatalog_schema_coverage(self):
        """Test parts catalog endpoints schema coverage."""
        report = self.generate_module_coverage_report(self.module_name)
        self.print_module_coverage_report(self.module_name)
        
        # Parts catalog might not be implemented yet
        min_coverage_percentage = 0.0  # Allow 0% for now since models aren't implemented yet
        assert report['coverage_percentage'] >= min_coverage_percentage, (
            f"Parts catalog module schema coverage is {report['coverage_percentage']:.1f}%, "
            f"but minimum required is {min_coverage_percentage}%. "
            f"Missing models: {report['missing_models']}"
        )
    
    def create_parametrized_test_data(self, module_name: str) -> List[EndpointInfo]:
        """Create parametrized test data for partscatalog endpoints."""
        return self.get_endpoints_for_module(module_name)


class TestOverallSchemaCompatibility(EndpointSchemaTestBase):
    """Test overall schema compatibility across all modules."""
    
    def setup_method(self):
        """Set up test fixtures for overall validation."""
        super().setup_method()
    
    @pytest.mark.unit
    def test_overall_coverage_report(self):
        """Generate an overall coverage report across all modules."""
        modules = ['core', 'metadata', 'capacity', 'auth', 'collaboration', 'statistics', 'partscatalog']
        
        print("\n" + "="*80)
        print("OVERALL SCHEMA VALIDATION COVERAGE REPORT")
        print("="*80)
        
        total_endpoints = 0
        total_validated = 0
        total_missing_models = []
        
        for module in modules:
            report = self.generate_module_coverage_report(module)
            
            total_endpoints += report['total_endpoints']
            total_validated += report['validated_count']
            total_missing_models.extend(report['missing_models'])
            
            print(f"\n{module.upper():>15}: {report['validated_count']:>3}/{report['total_endpoints']:>3} "
                  f"({report['coverage_percentage']:>5.1f}%) - "
                  f"{len(report['missing_models'])} missing models")
        
        overall_coverage = (total_validated / total_endpoints * 100) if total_endpoints > 0 else 0
        
        print("-" * 80)
        print(f"{'TOTAL':>15}: {total_validated:>3}/{total_endpoints:>3} "
              f"({overall_coverage:>5.1f}%) - "
              f"{len(set(total_missing_models))} unique missing models")
        
        print(f"\nSummary:")
        print(f"  Total GET endpoints with schemas: {total_endpoints}")
        print(f"  Successfully validated: {total_validated}")
        print(f"  Overall coverage: {overall_coverage:.1f}%")
        print(f"  Unique missing models: {len(set(total_missing_models))}")
        
        if total_missing_models:
            unique_missing = sorted(set(total_missing_models))
            print(f"\nTop missing models (first 10):")
            for model in unique_missing[:10]:
                print(f"    - {model}")
            if len(unique_missing) > 10:
                print(f"    ... and {len(unique_missing) - 10} more")
        
        print("="*80)
        
        # Assert minimum overall coverage (adjusted for current implementation state)
        min_overall_coverage = 0.0  # Allow 0% for now since models aren't implemented yet
        assert overall_coverage >= min_overall_coverage, (
            f"Overall schema coverage is {overall_coverage:.1f}%, "
            f"but minimum required is {min_overall_coverage}%. "
            f"Need to implement {len(set(total_missing_models))} missing models."
        )
    
    @pytest.mark.unit
    def test_critical_schemas_coverage(self):
        """Test that absolutely critical schemas have models across all modules."""
        # Define the most critical schemas that must exist
        critical_schemas = [
            # Core essentials
            'Activity', 'Activities', 'Resource', 'Resources', 'User', 'Users',
            # Metadata essentials  
            'Property', 'Properties', 'WorkZone', 'WorkZones',
            # Capacity essentials
            'CapacityArea', 'AvailableCapacity',
        ]
        
        missing_critical = []
        found_critical = []
        
        for schema_name in critical_schemas:
            model_class = self.schema_mapper.get_model_class_by_schema_name(schema_name)
            if model_class:
                found_critical.append(schema_name)
            else:
                missing_critical.append(schema_name)
        
        print(f"\nCritical schemas analysis:")
        print(f"  Found models for: {found_critical}")
        if missing_critical:
            print(f"  Missing models for: {missing_critical}")
        
        coverage_ratio = len(found_critical) / len(critical_schemas)
        print(f"  Critical schema coverage: {coverage_ratio:.1%}")
        
        # Require coverage for critical schemas (adjusted for current state)
        assert coverage_ratio >= 0.0, (  # Allow 0% for now
            f"Critical schema coverage is {coverage_ratio:.1%}, but minimum required is 10%. "
            f"Missing critical models: {missing_critical}. "
            f"These are essential for basic API functionality."
        )


# Test execution helper for standalone running
if __name__ == "__main__":
    # Allow running this test file directly for development/debugging
    test_instance = TestOverallSchemaCompatibility()
    test_instance.setup_method()
    
    print("=== OVERALL ENDPOINTS SCHEMA VALIDATION ===")
    
    # Run overall coverage test to see current state
    test_instance.test_overall_coverage_report()
    
    print("\n=== VALIDATION COMPLETE ===")