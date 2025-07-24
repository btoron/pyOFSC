"""
Base Test Class for Endpoint Schema Validation

This module provides a base test class that handles common functionality for validating
endpoint response schemas against their corresponding Pydantic models.
"""

import pytest
from typing import List, Dict, Any, Type, Optional
from pathlib import Path
from pydantic import BaseModel

from tests.fixtures.endpoints_registry import EndpointInfo, ENDPOINTS_BY_MODULE
from tests.utils.schema_mapper import SchemaModelMapper
from tests.utils.schema_validator import SwaggerSchemaValidator, ValidationResult


class EndpointSchemaTestBase:
    """Base class for endpoint schema validation tests."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Initialize validators
        swagger_file = Path(__file__).parent.parent.parent / "response_examples" / "swagger.json"
        self.schema_validator = SwaggerSchemaValidator(str(swagger_file))
        self.schema_mapper = SchemaModelMapper()
        
        # Cache for validation results
        self._validation_cache: Dict[str, ValidationResult] = {}
    
    def get_endpoints_for_module(self, module_name: str) -> List[EndpointInfo]:
        """
        Get all GET endpoints for a specific module that have response schemas.
        
        Args:
            module_name: The module name (e.g., 'core', 'metadata', 'capacity')
            
        Returns:
            List of endpoints filtered for GET method and having response schemas
        """
        module_endpoints = ENDPOINTS_BY_MODULE.get(module_name, [])
        
        return [
            endpoint for endpoint in module_endpoints
            if (endpoint.method == 'GET' and 
                endpoint.response_schema and 
                endpoint.response_schema.strip())
        ]
    
    def validate_endpoint_schema_compatibility(self, endpoint: EndpointInfo) -> ValidationResult:
        """
        Validate that the endpoint's response schema is compatible with its Pydantic model.
        
        Args:
            endpoint: The endpoint information from the registry
            
        Returns:
            ValidationResult with detailed validation information
            
        Raises:
            AssertionError: If validation fails with detailed error information
        """
        cache_key = f"{endpoint.method}:{endpoint.path}:{endpoint.response_schema}"
        
        # Check cache first
        if cache_key in self._validation_cache:
            result = self._validation_cache[cache_key]
        else:
            # Perform validation
            result = self._perform_endpoint_validation(endpoint)
            self._validation_cache[cache_key] = result
        
        # Generate detailed assertion message
        if not result.is_valid:
            self._assert_validation_success(endpoint, result)
        
        return result
    
    def _perform_endpoint_validation(self, endpoint: EndpointInfo) -> ValidationResult:
        """Perform the actual validation of endpoint schema compatibility."""
        schema_name = endpoint.response_schema
        
        # Get corresponding model class
        model_class = self.schema_mapper.get_model_class_by_schema_name(schema_name)
        
        if not model_class:
            # Create a validation result for missing model
            return ValidationResult(
                is_valid=False,
                schema_name=schema_name,
                model_class_name="<NOT_FOUND>",
                errors=[f"No Pydantic model found for schema '{schema_name}'"],
                warnings=[],
                structural_validation_passed=False,
                data_validation_passed=False
            )
        
        # Validate model against schema
        return self.schema_validator.validate_model_against_schema(model_class, schema_name)
    
    def _assert_validation_success(self, endpoint: EndpointInfo, result: ValidationResult):
        """Generate detailed assertion failure message."""
        error_parts = [
            f"Schema validation failed for endpoint:",
            f"  Endpoint: {endpoint.method} {endpoint.path}",
            f"  Schema: {result.schema_name}",
            f"  Model: {result.model_class_name}",
            f"  Module: {endpoint.module}",
            "",
            f"Validation Summary:",
            f"  Structural validation: {'✓ PASSED' if result.structural_validation_passed else '✗ FAILED'}",
            f"  Data validation: {'✓ PASSED' if result.data_validation_passed else '✗ FAILED'}",
        ]
        
        if result.errors:
            error_parts.extend([
                "",
                "ERRORS:",
            ])
            for i, error in enumerate(result.errors, 1):
                error_parts.append(f"  {i}. {error}")
        
        if result.warnings:
            error_parts.extend([
                "",
                "WARNINGS:",
            ])
            for i, warning in enumerate(result.warnings, 1):
                error_parts.append(f"  {i}. {warning}")
        
        error_parts.extend([
            "",
            "To fix this issue:",
            f"  1. Check the Pydantic model '{result.model_class_name}' in ofsc.models",
            f"  2. Compare with schema definition for '{result.schema_name}' in swagger.json",
            f"  3. Ensure field names, types, and required/optional status match",
            f"  4. If the model name doesn't match schema name, add override to SCHEMA_TO_MODEL_OVERRIDES",
        ])
        
        pytest.fail("\n".join(error_parts))
    
    def assert_field_compatibility(
        self, 
        model_field: Any, 
        schema_property: Dict[str, Any], 
        field_name: str
    ):
        """
        Assert that a model field is compatible with its schema property.
        
        Args:
            model_field: The Pydantic model field
            schema_property: The JSON schema property definition
            field_name: Name of the field for error reporting
        """
        # This is a helper method that could be expanded for specific field validation
        # For now, the main validation is handled in the schema validator
        pass
    
    def assert_required_fields_match(
        self, 
        model_class: Type[BaseModel], 
        schema_def: Dict[str, Any]
    ):
        """
        Assert that required fields match between model and schema.
        
        Args:
            model_class: The Pydantic model class
            schema_def: The JSON schema definition
        """
        # This is a helper method that could be expanded for specific required field validation
        # For now, the main validation is handled in the schema validator
        pass
    
    def generate_module_coverage_report(self, module_name: str) -> Dict[str, Any]:
        """
        Generate a coverage report for a specific module.
        
        Args:
            module_name: The module name to generate report for
            
        Returns:
            Dictionary with coverage statistics and details
        """
        endpoints = self.get_endpoints_for_module(module_name)
        
        total_endpoints = len(endpoints)
        validated_count = 0
        failed_validations = []
        successful_validations = []
        missing_models = []
        
        for endpoint in endpoints:
            try:
                # Use _perform_endpoint_validation directly to avoid assertions
                result = self._perform_endpoint_validation(endpoint)
                if result.is_valid:
                    validated_count += 1
                    successful_validations.append({
                        'endpoint': f"{endpoint.method} {endpoint.path}",
                        'schema': endpoint.response_schema,
                        'model': result.model_class_name
                    })
                else:
                    failed_validations.append({
                        'endpoint': f"{endpoint.method} {endpoint.path}",
                        'schema': endpoint.response_schema,
                        'model': result.model_class_name,
                        'errors': result.errors
                    })
                    if "No Pydantic model found" in str(result.errors):
                        missing_models.append(endpoint.response_schema)
            except Exception as e:
                failed_validations.append({
                    'endpoint': f"{endpoint.method} {endpoint.path}",
                    'schema': endpoint.response_schema,
                    'model': '<ERROR>',
                    'errors': [f"Validation error: {str(e)}"]
                })
        
        return {
            'module': module_name,
            'total_endpoints': total_endpoints,
            'validated_count': validated_count,
            'failed_count': len(failed_validations),
            'success_rate': validated_count / total_endpoints if total_endpoints > 0 else 0,
            'successful_validations': successful_validations,
            'failed_validations': failed_validations,
            'missing_models': list(set(missing_models)),
            'coverage_percentage': (validated_count / total_endpoints * 100) if total_endpoints > 0 else 0
        }
    
    def print_module_coverage_report(self, module_name: str):
        """Print a formatted coverage report for a module."""
        report = self.generate_module_coverage_report(module_name)
        
        print(f"\n=== {module_name.upper()} MODULE SCHEMA VALIDATION REPORT ===")
        print(f"Total GET endpoints with schemas: {report['total_endpoints']}")
        print(f"Successfully validated: {report['validated_count']}")
        print(f"Failed validations: {report['failed_count']}")
        print(f"Success rate: {report['success_rate']:.1%}")
        print(f"Coverage: {report['coverage_percentage']:.1f}%")
        
        if report['missing_models']:
            print(f"\nMissing models ({len(report['missing_models'])}):")
            for schema in sorted(report['missing_models']):
                print(f"  - {schema}")
        
        if report['failed_validations']:
            print(f"\nFailed validations ({len(report['failed_validations'])}):")
            for failure in report['failed_validations'][:5]:  # Show first 5
                print(f"  - {failure['endpoint']} ({failure['schema']})")
                if failure['errors']:
                    print(f"    Error: {failure['errors'][0]}")
            
            if len(report['failed_validations']) > 5:
                print(f"    ... and {len(report['failed_validations']) - 5} more")
        
        print("=" * 60)
    
    def create_parametrized_test_data(self, module_name: str) -> List[EndpointInfo]:
        """
        Create test data for parametrized tests.
        
        Args:
            module_name: The module name to get endpoints for
            
        Returns:
            List of endpoints suitable for parametrized testing
        """
        return self.get_endpoints_for_module(module_name)
    
    def generate_test_id(self, endpoint: EndpointInfo) -> str:
        """
        Generate a test ID for parametrized tests.
        
        Args:
            endpoint: The endpoint information
            
        Returns:
            String identifier for the test
        """
        # Clean up path for use as test ID
        clean_path = (endpoint.path
                     .replace('/rest/ofsc', '')
                     .replace('/v1', '')
                     .replace('/', '_')
                     .replace('{', '')
                     .replace('}', '')
                     .strip('_'))
        
        return f"{endpoint.method}_{clean_path}_{endpoint.response_schema}"