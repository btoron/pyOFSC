#!/usr/bin/env python3
"""
Generate Model Validation Tests for pyOFSC

This script generates comprehensive validation tests for all Pydantic models
by analyzing saved API responses and creating tests that validate each model
against real response data.

Usage:
    python scripts/generate_model_validation_tests.py
    python scripts/generate_model_validation_tests.py --module core
    python scripts/generate_model_validation_tests.py --output-dir tests/models/generated
"""

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.fixtures.endpoints_registry import ENDPOINTS
from tests.fixtures.models_registry import MODELS, ModelInfo


class ModelValidationTestGenerator:
    """Generates validation tests for models based on saved responses."""
    
    # Known model to import mappings based on common patterns
    MODEL_IMPORT_MAP = {
        # Core models
        "Resource": "ofsc.models.core.Resource",
        "ResourceListResponse": "ofsc.models.core.ResourceListResponse",
        "ResourcePosition": "ofsc.models.core.ResourcePosition",
        "Activity": "ofsc.models.core.Activity",
        "ActivityListResponse": "ofsc.models.core.ActivityListResponse",
        "User": "ofsc.models.core.User",
        "UserListResponse": "ofsc.models.core.UserListResponse",
        "Inventory": "ofsc.models.core.Inventory",
        "InventoryListResponse": "ofsc.models.core.InventoryListResponse",
        "ResourceInventory": "ofsc.models.core.ResourceInventory",
        "Location": "ofsc.models.core.Location",
        "LocationListResponse": "ofsc.models.core.LocationListResponse",
        "ResourceWorkSkill": "ofsc.models.core.ResourceWorkSkill",
        "ResourceWorkZone": "ofsc.models.core.ResourceWorkZone",
        "ResourceWorkSchedule": "ofsc.models.core.ResourceWorkSchedule",
        "DailyExtractItem": "ofsc.models.core.DailyExtractItem",
        "DailyExtractFolders": "ofsc.models.core.DailyExtractFolders",
        "Subscription": "ofsc.models.core.Subscription",
        "SubscriptionList": "ofsc.models.core.SubscriptionList",
        "BulkUpdateRequest": "ofsc.models.core.BulkUpdateRequest",
        "BulkUpdateResponse": "ofsc.models.core.BulkUpdateResponse",
        
        # Metadata models
        "ActivityTypeGroup": "ofsc.models.metadata.ActivityTypeGroup",
        "ActivityTypeGroupListResponse": "ofsc.models.metadata.ActivityTypeGroupListResponse",
        "ActivityType": "ofsc.models.metadata.ActivityType",
        "ActivityTypeListResponse": "ofsc.models.metadata.ActivityTypeListResponse",
        "Application": "ofsc.models.metadata.Application",
        "ApplicationListResponse": "ofsc.models.metadata.ApplicationListResponse",
        "ApplicationApiAccess": "ofsc.models.metadata.ApplicationApiAccess",
        "ApplicationApiAccessListResponse": "ofsc.models.metadata.ApplicationApiAccessListResponse",
        "CapacityArea": "ofsc.models.metadata.CapacityArea",
        "CapacityAreaListResponse": "ofsc.models.metadata.CapacityAreaListResponse",
        "CapacityAreaCategory": "ofsc.models.metadata.CapacityAreaCategory",
        "CapacityAreaCategoryListResponse": "ofsc.models.metadata.CapacityAreaCategoryListResponse",
        "Form": "ofsc.models.metadata.Form",
        "FormListResponse": "ofsc.models.metadata.FormListResponse",
        "Property": "ofsc.models.metadata.Property",
        "PropertyListResponse": "ofsc.models.metadata.PropertyListResponse",
        "ResourceType": "ofsc.models.metadata.ResourceType",
        "ResourceTypeListResponse": "ofsc.models.metadata.ResourceTypeListResponse",
        
        # Capacity models
        "CapacityCategory": "ofsc.models.capacity.CapacityCategory",
        "CapacityInterval": "ofsc.models.capacity.CapacityInterval",
        "CapacityResponse": "ofsc.models.capacity.CapacityResponse",
        "BookingStatus": "ofsc.models.capacity.BookingStatus",
        "BookingStatusResponse": "ofsc.models.capacity.BookingStatusResponse",
        "Quota": "ofsc.models.capacity.Quota",
        "QuotaResponse": "ofsc.models.capacity.QuotaResponse",
    }
    
    def __init__(self):
        self.endpoints = ENDPOINTS
        self.models = list(MODELS.values())  # Convert dict to list
        self.response_dir = Path(__file__).parent.parent / "response_examples"
        self.endpoint_to_model_map = self._build_endpoint_model_mapping()
        self.model_to_responses_map = self._build_model_response_mapping()
        self.model_name_to_info_map = {m.name: m for m in self.models}
    
    def _build_endpoint_model_mapping(self) -> Dict[int, str]:
        """Build mapping from endpoint ID to response model."""
        mapping = {}
        for endpoint in self.endpoints:
            # Extract return type from signature
            if endpoint.signature:
                # Look for return type after "->"
                match = re.search(r'->\s*(\w+)', endpoint.signature)
                if match:
                    mapping[endpoint.id] = match.group(1)
            elif endpoint.response_schema:
                mapping[endpoint.id] = endpoint.response_schema
        return mapping
    
    def _build_model_response_mapping(self) -> Dict[str, List[Path]]:
        """Build mapping from model name to response files."""
        mapping = defaultdict(list)
        
        # Iterate through saved responses
        for response_file in self.response_dir.glob("*.json"):
            # Extract endpoint ID from filename
            match = re.match(r'^(\d+)_', response_file.name)
            if not match:
                continue
                
            endpoint_id = int(match.group(1))
            
            # Find model for this endpoint
            if endpoint_id in self.endpoint_to_model_map:
                model_name = self.endpoint_to_model_map[endpoint_id]
                mapping[model_name].append(response_file)
        
        return dict(mapping)
    
    def _get_pydantic_model_import(self, model_info: ModelInfo) -> Optional[str]:
        """Get the Pydantic model import path."""
        if not model_info.mapped_pydantic_class:
            return None
            
        # Extract module and class name
        # Format: "ofsc.models.core.Resource"
        parts = model_info.mapped_pydantic_class.split('.')
        if len(parts) < 3:
            return None
            
        module_path = '.'.join(parts[:-1])
        class_name = parts[-1]
        
        return f"from {module_path} import {class_name}"
    
    def _generate_test_file_for_module(self, module: str) -> str:
        """Generate test file content for a specific module."""
        # Get models that have responses and are in our import map
        models_with_responses = []
        model_names_seen = set()
        
        for model_name, response_files in self.model_to_responses_map.items():
            if model_name in self.MODEL_IMPORT_MAP and response_files:
                # Check if this model belongs to the requested module
                import_path = self.MODEL_IMPORT_MAP[model_name]
                if f".models.{module}." in import_path:
                    if model_name not in model_names_seen:
                        models_with_responses.append(model_name)
                        model_names_seen.add(model_name)
        
        if not models_with_responses:
            return f"# No models with saved responses found for module: {module}"
        
        # Generate imports
        imports = self._generate_imports_for_models(models_with_responses)
        
        # Generate test class
        test_class = self._generate_test_class_for_models(module, models_with_responses)
        
        return f"""{self._generate_header(module)}

{imports}

{test_class}
"""
    
    def _generate_header(self, module: str) -> str:
        """Generate file header."""
        return f'''"""
Model validation tests for {module.title()} API responses.

This file contains comprehensive validation tests for all {module.title()} API models
against real API response examples.

Generated on: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
"""'''
    
    def _generate_imports_for_models(self, model_names: List[str]) -> str:
        """Generate import statements for model names."""
        imports = [
            "import json",
            "from pathlib import Path",
            "import pytest",
            "from pydantic import ValidationError",
            "",
            "# Import the actual models"
        ]
        
        # Group imports by module
        imports_by_module = defaultdict(set)
        for model_name in model_names:
            if model_name in self.MODEL_IMPORT_MAP:
                import_path = self.MODEL_IMPORT_MAP[model_name]
                parts = import_path.split('.')
                if len(parts) >= 3:
                    module_path = '.'.join(parts[:-1])
                    class_name = parts[-1]
                    imports_by_module[module_path].add(class_name)
        
        # Generate sorted imports
        for module_path in sorted(imports_by_module.keys()):
            classes = sorted(imports_by_module[module_path])
            imports.append(f"from {module_path} import {', '.join(classes)}")
        
        return '\n'.join(imports)
    
    def _generate_test_class_for_models(self, module: str, model_names: List[str]) -> str:
        """Generate the test class with all model validation tests."""
        class_name = f"Test{module.title()}ModelsValidation"
        
        test_methods = []
        
        # Add fixture
        test_methods.append("""    @pytest.fixture
    def response_examples_path(self):
        \"\"\"Path to response examples directory.\"\"\"
        # Go up from tests/models/generated/ to project root, then to response_examples
        return Path(__file__).parent.parent.parent.parent / "response_examples\"""")
        
        # Generate test method for each model
        for model_name in model_names:
            test_method = self._generate_model_test_by_name(model_name)
            if test_method:
                test_methods.append(test_method)
        
        return f"""class {class_name}:
    \"\"\"Test {module.title()} API model validation against response examples.\"\"\"
    
{chr(10).join(test_methods)}"""
    
    def _generate_model_test_by_name(self, model_name: str) -> Optional[str]:
        """Generate test method for a model by name."""
        if model_name not in self.model_to_responses_map:
            return None
            
        response_files = self.model_to_responses_map[model_name]
        
        # Generate safe test method name
        test_method_name = f"test_{self._to_snake_case(model_name)}_validation"
        
        # Get endpoint info for these responses
        endpoint_ids = []
        for response_file in response_files:
            match = re.match(r'^(\d+)_', response_file.name)
            if match:
                endpoint_ids.append(int(match.group(1)))
        
        # Generate file list
        file_list = '\n'.join([f'            "{f.name}",' for f in sorted(response_files)[:5]])  # Limit to 5 examples
        
        return f"""
    def {test_method_name}(self, response_examples_path):
        \"\"\"Validate {model_name} model against saved response examples.
        
        Tests against endpoints: {', '.join(f'#{id}' for id in sorted(set(endpoint_ids))[:5])}
        \"\"\"
        response_files = [
{file_list}
        ]
        
        for filename in response_files:
            file_path = response_examples_path / filename
            if not file_path.exists():
                pytest.skip(f"Response file not found: {{filename}}")
                continue
            
            with open(file_path) as f:
                data = json.load(f)
            
            # Remove metadata field
            if "_metadata" in data:
                del data["_metadata"]
            
            # Handle list responses
            if "items" in data and isinstance(data["items"], list):
                if "ListResponse" in "{model_name}":
                    # Validate the entire list response
                    try:
                        model_instance = {model_name}(**data)
                        self._validate_{self._to_snake_case(model_name)}_fields(model_instance, data)
                        print(f"✅ Validated {{filename}} as list response")
                    except ValidationError as e:
                        pytest.fail(f"{model_name} validation failed for {{filename}}: {{e}}")
                else:
                    # Validate individual items (for single model types)
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = {model_name}(**item)
                            self._validate_{self._to_snake_case(model_name)}_fields(model_instance, item)
                            print(f"✅ Validated {{filename}} item {{idx}}")
                        except ValidationError as e:
                            pytest.fail(f"{model_name} validation failed for {{filename}} item {{idx}}: {{e}}")
            else:
                # Validate single response
                try:
                    model_instance = {model_name}(**data)
                    self._validate_{self._to_snake_case(model_name)}_fields(model_instance, data)
                    print(f"✅ Validated {{filename}}")
                except ValidationError as e:
                    pytest.fail(f"{model_name} validation failed for {{filename}}: {{e}}")
    
    def _validate_{self._to_snake_case(model_name)}_fields(self, model: {model_name}, original_data: dict):
        \"\"\"Validate specific fields for {model_name}.\"\"\"
        # Add model-specific field validations here
        {self._generate_field_validations_by_name(model_name)}"""
    
    def _generate_field_validations_by_name(self, model_name: str) -> str:
        """Generate field validation assertions based on model name."""
        validations = []
        
        # Get model info if available
        model_info = self.model_name_to_info_map.get(model_name)
        if model_info:
            # Add validations for required fields
            for prop_name in model_info.required_properties[:3]:  # Limit to first 3
                validations.append(f"assert hasattr(model, '{prop_name}'), \"Missing required field: {prop_name}\"")
            
            # Add type validations for specific fields
            for prop in model_info.properties[:3]:  # Limit to first 3
                if prop.type == "string" and prop.enum:
                    validations.append(
                        f"if hasattr(model, '{prop.name}') and getattr(model, '{prop.name}') is not None:\n"
                        f"            assert getattr(model, '{prop.name}') in {prop.enum}, "
                        f"\"Invalid enum value for {prop.name}\""
                    )
        
        # Add common validations based on model name patterns
        if "ListResponse" in model_name:
            validations.extend([
                "# List response validations",
                "assert hasattr(model, 'items'), \"List response should have 'items' field\"",
                "assert hasattr(model, 'totalResults'), \"List response should have 'totalResults' field\""
            ])
        
        if not validations:
            validations.append("pass  # Add specific field validations as needed")
        
        return '\n        '.join(validations)
    
    def _to_snake_case(self, name: str) -> str:
        """Convert CamelCase to snake_case."""
        # Insert underscore before uppercase letters
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    def generate_all_tests(self, output_dir: Optional[Path] = None) -> List[Path]:
        """Generate test files for all modules."""
        if output_dir is None:
            output_dir = Path(__file__).parent.parent / "tests" / "models" / "generated"
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        generated_files = []
        
        # Get unique modules
        modules = set(m.module for m in self.models)
        
        for module in sorted(modules):
            content = self._generate_test_file_for_module(module)
            
            # Skip if no content
            if content.startswith("#"):
                continue
            
            # Write test file
            output_file = output_dir / f"test_{module}_models_validation.py"
            output_file.write_text(content)
            generated_files.append(output_file)
            
            print(f"✅ Generated: {output_file}")
        
        return generated_files
    
    def generate_summary_report(self) -> str:
        """Generate a summary report of model coverage."""
        report = []
        report.append("=" * 80)
        report.append("MODEL VALIDATION TEST COVERAGE REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Overall statistics
        total_models = len(self.models)
        models_with_responses = len(self.model_to_responses_map)
        coverage_percentage = (models_with_responses / total_models * 100) if total_models > 0 else 0
        
        report.append(f"Total models in registry: {total_models}")
        report.append(f"Models with saved responses: {models_with_responses} ({coverage_percentage:.1f}%)")
        report.append("")
        
        # By module breakdown
        modules = defaultdict(lambda: {"total": 0, "with_responses": 0})
        
        for model in self.models:
            modules[model.module]["total"] += 1
            if model.name in self.model_to_responses_map:
                modules[model.module]["with_responses"] += 1
        
        report.append("Coverage by module:")
        for module, stats in sorted(modules.items()):
            coverage = (stats["with_responses"] / stats["total"] * 100) if stats["total"] > 0 else 0
            report.append(f"  {module}: {stats['with_responses']}/{stats['total']} ({coverage:.1f}%)")
        
        report.append("")
        report.append("Models without saved responses:")
        for model in self.models:
            if model.name not in self.model_to_responses_map and model.mapped_pydantic_class:
                report.append(f"  - {model.name} ({model.module})")
        
        return '\n'.join(report)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate model validation tests from saved API responses"
    )
    parser.add_argument(
        "--module",
        choices=["core", "metadata", "capacity"],
        help="Generate tests for specific module only"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Output directory for generated tests"
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Show coverage summary report"
    )
    
    args = parser.parse_args()
    
    generator = ModelValidationTestGenerator()
    
    if args.summary:
        print(generator.generate_summary_report())
        return
    
    # Generate tests
    if args.module:
        output_dir = args.output_dir or Path(__file__).parent.parent / "tests" / "models" / "generated"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        content = generator._generate_test_file_for_module(args.module)
        output_file = output_dir / f"test_{args.module}_models_validation.py"
        output_file.write_text(content)
        
        print(f"✅ Generated: {output_file}")
    else:
        generated_files = generator.generate_all_tests(args.output_dir)
        print(f"\n✅ Generated {len(generated_files)} test files")
        print("\nRun tests with:")
        print("  uv run pytest tests/models/generated/ -v")


if __name__ == "__main__":
    main()