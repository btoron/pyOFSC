"""
Swagger Schema Validator Utility

This module provides functionality to validate Pydantic models against their corresponding
Swagger JSON schema definitions using a hybrid validation approach.
"""

import json
import random
import string
from dataclasses import dataclass
from datetime import datetime, date
from pathlib import Path
from typing import Dict, Any, List, Optional, Type, Set
from pydantic import BaseModel, ValidationError

from tests.utils.schema_mapper import SchemaModelMapper


@dataclass
class ValidationResult:
    """Result of schema-model validation."""
    is_valid: bool
    schema_name: str
    model_class_name: str
    errors: List[str]
    warnings: List[str]
    structural_validation_passed: bool
    data_validation_passed: bool
    
    def has_errors(self) -> bool:
        """Check if validation has any errors."""
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        """Check if validation has any warnings.""" 
        return len(self.warnings) > 0


@dataclass 
class FieldCompatibilityResult:
    """Result of individual field compatibility check."""
    field_name: str
    is_compatible: bool
    model_type: str
    schema_type: str
    errors: List[str]
    warnings: List[str]


class SwaggerSchemaValidator:
    """Validates Pydantic models against Swagger JSON schema definitions."""
    
    # Type mapping from JSON Schema to Python types
    JSON_TO_PYTHON_TYPES = {
        'string': str,
        'integer': int,
        'number': (int, float),
        'boolean': bool,
        'array': list,
        'object': dict,
        'null': type(None),
    }
    
    def __init__(self, swagger_file_path: str):
        """
        Initialize the validator with swagger.json file.
        
        Args:
            swagger_file_path: Path to the swagger.json file
        """
        self.swagger_file_path = Path(swagger_file_path)
        self._swagger_data: Optional[Dict[str, Any]] = None
        self._definitions: Optional[Dict[str, Any]] = None
        self.schema_mapper = SchemaModelMapper()
        
    def _load_swagger_data(self) -> Dict[str, Any]:
        """Load and cache swagger.json data."""
        if self._swagger_data is None:
            with open(self.swagger_file_path, 'r') as f:
                self._swagger_data = json.load(f)
            self._definitions = self._swagger_data.get('definitions', {})
        return self._swagger_data
    
    def get_schema_definition(self, schema_name: str) -> Optional[Dict[str, Any]]:
        """
        Get schema definition from swagger.json.
        
        Args:
            schema_name: Name of the schema in the definitions section
            
        Returns:
            Schema definition dictionary or None if not found
        """
        self._load_swagger_data()
        if self._definitions is None:
            return None
        return self._definitions.get(schema_name)
    
    def get_all_schema_names(self) -> List[str]:
        """Get all schema names from swagger definitions."""
        self._load_swagger_data()
        if self._definitions is None:
            return []
        return list(self._definitions.keys())
    
    def validate_model_against_schema(
        self, 
        model_class: Type[BaseModel], 
        schema_name: str
    ) -> ValidationResult:
        """
        Validate a Pydantic model against its corresponding JSON schema.
        
        Args:
            model_class: The Pydantic model class to validate
            schema_name: The name of the JSON schema to validate against
            
        Returns:
            ValidationResult with detailed validation information
        """
        errors = []
        warnings = []
        
        # Get schema definition
        schema_def = self.get_schema_definition(schema_name)
        if not schema_def:
            errors.append(f"Schema '{schema_name}' not found in swagger definitions")
            return ValidationResult(
                is_valid=False,
                schema_name=schema_name,
                model_class_name=model_class.__name__,
                errors=errors,
                warnings=warnings,
                structural_validation_passed=False,
                data_validation_passed=False
            )
        
        # Perform structural validation
        structural_result = self._validate_structure(model_class, schema_def, schema_name)
        errors.extend(structural_result.get('errors', []))
        warnings.extend(structural_result.get('warnings', []))
        structural_passed = len(structural_result.get('errors', [])) == 0
        
        # Perform data validation
        data_result = self._validate_data_compatibility(model_class, schema_def, schema_name)
        errors.extend(data_result.get('errors', []))
        warnings.extend(data_result.get('warnings', []))
        data_passed = len(data_result.get('errors', [])) == 0
        
        return ValidationResult(
            is_valid=structural_passed and data_passed,
            schema_name=schema_name,
            model_class_name=model_class.__name__,
            errors=errors,
            warnings=warnings,
            structural_validation_passed=structural_passed,
            data_validation_passed=data_passed
        )
    
    def _validate_structure(
        self, 
        model_class: Type[BaseModel], 
        schema_def: Dict[str, Any], 
        schema_name: str
    ) -> Dict[str, List[str]]:
        """Validate structural compatibility between model and schema."""
        errors = []
        warnings = []
        
        # Get model fields
        model_fields = model_class.model_fields if hasattr(model_class, 'model_fields') else {}
        
        # Get schema properties
        schema_properties = schema_def.get('properties', {})
        schema_required = set(schema_def.get('required', []))
        
        # Check required fields
        model_required = set()
        for field_name, field_info in model_fields.items():
            if field_info.is_required():
                model_required.add(field_name)
        
        # Find missing required fields in model
        missing_required = schema_required - model_required
        if missing_required:
            errors.append(f"Model missing required fields from schema: {sorted(missing_required)}")
        
        # Find extra required fields in model (might be warnings)
        extra_required = model_required - schema_required
        if extra_required:
            warnings.append(f"Model has required fields not in schema: {sorted(extra_required)}")
        
        # Validate individual fields
        for field_name, schema_property in schema_properties.items():
            if field_name in model_fields:
                field_result = self._validate_field_compatibility(
                    field_name, model_fields[field_name], schema_property
                )
                errors.extend(field_result.errors)
                warnings.extend(field_result.warnings)
            else:
                # Schema field not in model
                if field_name in schema_required:
                    errors.append(f"Required schema field '{field_name}' not found in model")
                else:
                    warnings.append(f"Optional schema field '{field_name}' not found in model")
        
        # Check for model fields not in schema
        extra_model_fields = set(model_fields.keys()) - set(schema_properties.keys())
        if extra_model_fields:
            warnings.append(f"Model has fields not in schema: {sorted(extra_model_fields)}")
        
        return {
            'errors': errors,
            'warnings': warnings
        }
    
    def _validate_field_compatibility(
        self, 
        field_name: str, 
        model_field: Any, 
        schema_property: Dict[str, Any]
    ) -> FieldCompatibilityResult:
        """Validate compatibility of a single field."""
        errors = []
        warnings = []
        
        # Get types
        schema_type = schema_property.get('type', 'unknown')
        model_type = str(model_field.annotation) if hasattr(model_field, 'annotation') else 'unknown'
        
        # Basic type compatibility check
        is_compatible = self._are_types_compatible(model_field, schema_property)
        
        if not is_compatible:
            errors.append(
                f"Field '{field_name}' type mismatch: "
                f"model={model_type}, schema={schema_type}"
            )
        
        # Check format constraints
        schema_format = schema_property.get('format')
        if schema_format:
            # TODO: Validate format constraints (e.g., date-time, email, etc.)
            pass
        
        # Check enum constraints
        schema_enum = schema_property.get('enum')
        if schema_enum:
            # TODO: Validate enum constraints
            pass
        
        # Check array items for array types
        if schema_type == 'array':
            items_schema = schema_property.get('items', {})
            if items_schema:
                # TODO: Recursively validate array item types
                pass
        
        return FieldCompatibilityResult(
            field_name=field_name,
            is_compatible=len(errors) == 0,
            model_type=model_type,
            schema_type=schema_type,
            errors=errors,
            warnings=warnings
        )
    
    def _are_types_compatible(self, model_field: Any, schema_property: Dict[str, Any]) -> bool:
        """Check if model field type is compatible with schema property type."""
        schema_type = schema_property.get('type')
        
        if not schema_type:
            return True  # No type specified in schema
        
        # Get expected Python type from schema
        expected_python_type = self.JSON_TO_PYTHON_TYPES.get(schema_type)
        if not expected_python_type:
            return True  # Unknown schema type
        
        # TODO: Implement more sophisticated type checking
        # This is a simplified version - real implementation would need to handle:
        # - Union types
        # - Optional types  
        # - Generic types (List[T], Dict[K,V])
        # - Custom types and nested models
        
        return True  # Placeholder - assume compatible for now
    
    def _validate_data_compatibility(
        self, 
        model_class: Type[BaseModel], 
        schema_def: Dict[str, Any], 
        schema_name: str
    ) -> Dict[str, List[str]]:
        """Validate data compatibility by generating test data from schema."""
        errors = []
        warnings = []
        
        try:
            # Generate test data from schema
            test_data = self.generate_test_data_from_schema(schema_def, schema_name)
            
            # Try to create model instance with generated data
            try:
                model_class(**test_data)
                # If we get here, the data is compatible
            except ValidationError as e:
                errors.append(f"Generated test data failed model validation: {str(e)}")
            except Exception as e:
                errors.append(f"Unexpected error creating model instance: {str(e)}")
                
        except Exception as e:
            warnings.append(f"Could not generate test data from schema: {str(e)}")
        
        return {
            'errors': errors,
            'warnings': warnings
        }
    
    def generate_test_data_from_schema(
        self, 
        schema_def: Dict[str, Any], 
        schema_name: str,
        _visited_schemas: Optional[Set[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate valid test data from a JSON schema definition.
        
        Args:
            schema_def: The JSON schema definition
            schema_name: Name of the schema (for circular reference detection)
            _visited_schemas: Set of already visited schemas (for recursion detection)
            
        Returns:
            Dictionary with generated test data
        """
        if _visited_schemas is None:
            _visited_schemas = set()
        
        # Prevent infinite recursion
        if schema_name in _visited_schemas:
            return {}
        
        _visited_schemas.add(schema_name)
        
        try:
            return self._generate_data_from_schema_properties(
                schema_def, schema_name, _visited_schemas
            )
        finally:
            _visited_schemas.discard(schema_name)
    
    def _generate_data_from_schema_properties(
        self, 
        schema_def: Dict[str, Any], 
        schema_name: str,
        visited_schemas: Set[str]
    ) -> Dict[str, Any]:
        """Generate test data from schema properties."""
        data = {}
        properties = schema_def.get('properties', {})
        required_fields = set(schema_def.get('required', []))
        
        for prop_name, prop_def in properties.items():
            # Always generate required fields, optionally generate optional fields
            if prop_name in required_fields or random.choice([True, False]):
                try:
                    data[prop_name] = self._generate_value_for_property(
                        prop_def, prop_name, visited_schemas
                    )
                except Exception:
                    # If we can't generate a value, skip it
                    pass
        
        return data
    
    def _generate_value_for_property(
        self, 
        prop_def: Dict[str, Any], 
        prop_name: str,
        visited_schemas: Set[str]
    ) -> Any:
        """Generate a value for a single property based on its schema definition."""
        prop_type = prop_def.get('type', 'string')
        
        # Handle $ref (references to other schemas)
        if '$ref' in prop_def:
            ref_path = prop_def['$ref']
            if ref_path.startswith('#/definitions/'):
                ref_schema_name = ref_path.replace('#/definitions/', '')
                ref_schema_def = self.get_schema_definition(ref_schema_name)
                if ref_schema_def:
                    return self.generate_test_data_from_schema(
                        ref_schema_def, ref_schema_name, visited_schemas
                    )
            return {}
        
        # Handle enum values
        if 'enum' in prop_def:
            return random.choice(prop_def['enum'])
        
        # Generate value based on type
        if prop_type == 'string':
            return self._generate_string_value(prop_def, prop_name)
        elif prop_type == 'integer':
            return self._generate_integer_value(prop_def)
        elif prop_type == 'number':
            return self._generate_number_value(prop_def)
        elif prop_type == 'boolean':
            return random.choice([True, False])
        elif prop_type == 'array':
            return self._generate_array_value(prop_def, visited_schemas)
        elif prop_type == 'object':
            return self._generate_object_value(prop_def, visited_schemas)
        elif prop_type == 'null':
            return None
        else:
            # Unknown type, return a safe default
            return f"unknown_type_{prop_type}"
    
    def _generate_string_value(self, prop_def: Dict[str, Any], prop_name: str) -> str:
        """Generate a string value based on property definition."""
        format_type = prop_def.get('format', '')
        min_length = prop_def.get('minLength', 1)
        max_length = prop_def.get('maxLength', 50)
        
        # Handle special formats
        if format_type == 'date-time':
            return datetime.now().isoformat()
        elif format_type == 'date':
            return date.today().isoformat()
        elif format_type == 'email':
            return f"test_{prop_name}@example.com"
        elif format_type == 'uri':
            return f"https://example.com/{prop_name}"
        
        # Generate random string
        length = min(max_length, max(min_length, random.randint(5, 20)))
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    def _generate_integer_value(self, prop_def: Dict[str, Any]) -> int:
        """Generate an integer value based on property definition."""
        minimum = prop_def.get('minimum', 0)
        maximum = prop_def.get('maximum', 1000)
        return random.randint(minimum, maximum)
    
    def _generate_number_value(self, prop_def: Dict[str, Any]) -> float:
        """Generate a number value based on property definition."""
        minimum = prop_def.get('minimum', 0.0)
        maximum = prop_def.get('maximum', 1000.0)
        return random.uniform(minimum, maximum)
    
    def _generate_array_value(
        self, 
        prop_def: Dict[str, Any], 
        visited_schemas: Set[str]
    ) -> List[Any]:
        """Generate an array value based on property definition."""
        items_def = prop_def.get('items', {})
        min_items = prop_def.get('minItems', 0)
        max_items = prop_def.get('maxItems', 5)
        
        array_length = random.randint(min_items, min(max_items, 3))  # Keep arrays small
        
        array = []
        for _ in range(array_length):
            try:
                item_value = self._generate_value_for_property(
                    items_def, 'item', visited_schemas
                )
                array.append(item_value)
            except Exception:
                # If we can't generate an item, stop here
                break
        
        return array
    
    def _generate_object_value(
        self, 
        prop_def: Dict[str, Any], 
        visited_schemas: Set[str]
    ) -> Dict[str, Any]:
        """Generate an object value based on property definition."""
        # If the object has properties defined, generate them
        if 'properties' in prop_def:
            return self._generate_data_from_schema_properties(
                prop_def, 'inline_object', visited_schemas
            )
        
        # Otherwise, return a simple object
        return {'generated': True, 'type': 'object'}