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
import ast
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
        "PropertyListResponse": "ofsc.models.metadata.PropertyListResponse",
        "ResourceType": "ofsc.models.metadata.ResourceType",
        "ResourceTypeListResponse": "ofsc.models.metadata.ResourceTypeListResponse",
        # Capacity models
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

        # Build comprehensive model import map using hybrid approach
        self.model_import_map = self._build_comprehensive_import_map()

        self.endpoint_to_model_map = self._build_endpoint_model_mapping()
        self.model_to_responses_map = self._build_model_response_mapping()
        self.model_name_to_info_map = {m.name: m for m in self.models}

    def _build_comprehensive_import_map(self) -> Dict[str, str]:
        """Build comprehensive model import map using hybrid approach."""
        import_map = {}

        # 1. Dynamic discovery by scanning model files
        discovered_models = self._discover_models_from_files()
        import_map.update(discovered_models)

        # 2. Fallback to static map for any missing models
        for model_name, import_path in self.MODEL_IMPORT_MAP.items():
            if model_name not in import_map:
                import_map[model_name] = import_path

        print(
            f"📊 Model Import Map: {len(discovered_models)} discovered + {len(self.MODEL_IMPORT_MAP)} static = {len(import_map)} total models"
        )

        return import_map

    def _is_error_response(self, response_file: Path) -> bool:
        """Check if a response file contains an error response (status_code >= 400)."""
        try:
            with open(response_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Check metadata for status_code
            if isinstance(data, dict) and "_metadata" in data:
                metadata = data["_metadata"]
                if isinstance(metadata, dict) and "status_code" in metadata:
                    status_code = metadata["status_code"]
                    return isinstance(status_code, int) and status_code >= 400

            # Check for common error response fields
            if isinstance(data, dict):
                error_indicators = ["type", "title", "status", "detail"]
                has_error_fields = (
                    sum(1 for field in error_indicators if field in data) >= 3
                )
                if has_error_fields and "status" in data:
                    try:
                        status = int(str(data["status"]))
                        return status >= 400
                    except (ValueError, TypeError):
                        pass

            return False
        except (json.JSONDecodeError, IOError):
            return False

    def _discover_models_from_files(self) -> Dict[str, str]:
        """Discover Pydantic models by scanning actual model files with recursive inheritance detection."""
        import_map = {}

        # Scan each module including base.py
        modules = ["base", "core", "metadata", "capacity"]
        project_root = Path(__file__).parent.parent

        # First pass: collect all class definitions and their inheritance
        all_classes = {}  # class_name -> (module, node, content)
        inheritance_map = {}  # class_name -> set of base class names

        for module in modules:
            module_path = project_root / "ofsc" / "models" / f"{module}.py"

            if not module_path.exists():
                continue

            try:
                with open(module_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Parse AST to find class definitions
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        class_name = node.name
                        all_classes[class_name] = (module, node, content)

                        # Extract base classes for inheritance analysis
                        base_classes = set()
                        for base in node.bases:
                            base_name = self._extract_base_class_name(base)
                            if base_name:
                                base_classes.add(base_name)
                        inheritance_map[class_name] = base_classes

            except Exception as e:
                print(f"⚠️  Error scanning {module_path}: {e}")
                continue

        # Second pass: identify Pydantic models using recursive inheritance
        pydantic_models = set()

        # Start with known Pydantic base classes
        known_pydantic_bases = {
            "BaseModel",
            "BaseOFSResponse",
            "OFSResponseList",
            "RootModel",
            "BaseOFSCModel",  # In case there are custom base classes
        }

        # Add classes that directly inherit from known Pydantic bases
        for class_name, base_classes in inheritance_map.items():
            if base_classes & known_pydantic_bases:
                pydantic_models.add(class_name)

        # Recursively find classes that inherit from Pydantic models
        changed = True
        while changed:
            changed = False
            for class_name, base_classes in inheritance_map.items():
                if class_name not in pydantic_models and base_classes & pydantic_models:
                    pydantic_models.add(class_name)
                    changed = True

        # Third pass: also check for Pydantic indicators in class body
        for class_name, (module, node, content) in all_classes.items():
            if class_name not in pydantic_models:
                if self._is_pydantic_model_class(node, content):
                    pydantic_models.add(class_name)

        # Build import map for discovered Pydantic models
        module_counts = {}
        for class_name in pydantic_models:
            if class_name in all_classes:
                module, _, _ = all_classes[class_name]
                import_map[class_name] = f"ofsc.models.{module}.{class_name}"
                module_counts[module] = module_counts.get(module, 0) + 1

        # Print discovery results
        for module in modules:
            count = module_counts.get(module, 0)
            print(f"📁 {module}: Found {count} models")

        return import_map

    def _extract_base_class_name(self, base_node: ast.expr) -> Optional[str]:
        """Extract base class name from AST node."""
        if isinstance(base_node, ast.Name):
            return base_node.id
        elif isinstance(base_node, ast.Attribute):
            # Handle cases like pydantic.BaseModel
            return base_node.attr
        elif isinstance(base_node, ast.Subscript):
            # Handle generic types like Generic[T], OFSResponseList[Property]
            return self._extract_base_class_name(base_node.value)
        return None

    def _is_pydantic_model_class(self, node: ast.ClassDef, file_content: str) -> bool:
        """Determine if a class is likely a Pydantic model."""
        # Check if class inherits from BaseModel or BaseOFSCModel
        for base in node.bases:
            if isinstance(base, ast.Name):
                if base.id in ["BaseModel", "BaseOFSCModel", "BaseOFSResponse"]:
                    return True
            elif isinstance(base, ast.Attribute):
                if base.attr in ["BaseModel", "BaseOFSCModel", "BaseOFSResponse"]:
                    return True

        # Additional heuristics: look for Field() usage or model_config
        class_body = ast.get_source_segment(file_content, node) or ""

        # Look for common Pydantic patterns
        pydantic_indicators = [
            "Field(",
            "model_config",
            "ConfigDict",
            "= field(",
            "validator",
            "root_validator",
        ]

        return any(indicator in class_body for indicator in pydantic_indicators)

    def _build_endpoint_model_mapping(self) -> Dict[int, str]:
        """Build mapping from endpoint ID to response model."""
        mapping = {}
        for endpoint in self.endpoints:
            # Extract return type from signature
            if endpoint.signature:
                # Look for return type after "->"
                match = re.search(r"->\s*(\w+)", endpoint.signature)
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
            # Skip error responses (status_code >= 400)
            if self._is_error_response(response_file):
                continue

            # Extract endpoint ID from filename
            match = re.match(r"^(\d+)_", response_file.name)
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
        parts = model_info.mapped_pydantic_class.split(".")
        if len(parts) < 3:
            return None

        module_path = ".".join(parts[:-1])
        class_name = parts[-1]

        return f"from {module_path} import {class_name}"

    def _generate_test_file_for_module(self, module: str) -> str:
        """Generate test file content for a specific module."""
        # Get models that have responses and are in our import map
        models_with_responses = []
        model_names_seen = set()

        for model_name, response_files in self.model_to_responses_map.items():
            if model_name in self.model_import_map and response_files:
                # Check if this model belongs to the requested module
                import_path = self.model_import_map[model_name]
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

Generated on: {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")}
"""'''

    def _get_item_model_name(self, list_model_name: str) -> Optional[str]:
        """Extract individual item model name from list response model name."""
        if list_model_name.endswith("ListResponse"):
            return list_model_name.replace("ListResponse", "")
        elif list_model_name.endswith("List"):
            return list_model_name.replace("List", "")
        return None

    def _is_list_response_model(self, model_name: str) -> bool:
        """Check if a model name represents a list/collection response."""
        return (
            model_name.endswith("ListResponse")
            or model_name.endswith("List")
            or "List" in model_name
        )

    def _generate_imports_for_models(self, model_names: List[str]) -> str:
        """Generate import statements for model names, including item models for lists."""
        imports = [
            "import json",
            "from pathlib import Path",
            "import pytest",
            "from pydantic import ValidationError",
            "",
            "# Import the actual models",
        ]

        # Add individual item models for list responses
        additional_models = set()
        for model_name in model_names:
            if self._is_list_response_model(model_name):
                item_model = self._get_item_model_name(model_name)
                if item_model and item_model in self.model_import_map:
                    additional_models.add(item_model)

        # Include additional models in the final list
        all_models = set(model_names) | additional_models

        # Group imports by module
        imports_by_module = defaultdict(set)
        for model_name in all_models:
            if model_name in self.model_import_map:
                import_path = self.model_import_map[model_name]
                parts = import_path.split(".")
                if len(parts) >= 3:
                    module_path = ".".join(parts[:-1])
                    class_name = parts[-1]
                    imports_by_module[module_path].add(class_name)

        # Generate sorted imports
        for module_path in sorted(imports_by_module.keys()):
            classes = sorted(imports_by_module[module_path])
            imports.append(f"from {module_path} import {', '.join(classes)}")

        return "\n".join(imports)

    def _generate_test_class_for_models(
        self, module: str, model_names: List[str]
    ) -> str:
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
            match = re.match(r"^(\d+)_", response_file.name)
            if match:
                endpoint_ids.append(int(match.group(1)))

        # Generate file list
        file_list = "\n".join(
            [f'            "{f.name}",' for f in sorted(response_files)[:5]]
        )  # Limit to 5 examples

        # Check if this is a list model and get item model
        is_list_model = self._is_list_response_model(model_name)
        item_model_name = None
        if is_list_model:
            item_model_name = self._get_item_model_name(model_name)
            if item_model_name and item_model_name not in self.model_import_map:
                item_model_name = None  # Item model not available

        return f"""
    def {test_method_name}(self, response_examples_path):
        \"\"\"Validate {model_name} model against saved response examples.
        
        Tests against endpoints: {
            ", ".join(f"#{id}" for id in sorted(set(endpoint_ids))[:5])
        }
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
                if {str(is_list_model)}:
                    # Validate the entire list response
                    try:
                        model_instance = {model_name}(**data)
                        self._validate_{
            self._to_snake_case(model_name)
        }_fields(model_instance, data)
                        print(f"✅ Validated {{filename}} as list response")
                    except ValidationError as e:
                        pytest.fail(f"{
            model_name
        } validation failed for {{filename}}: {{e}}")
                    
                    # Also validate individual items using the item model{
            f'''
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = {item_model_name}(**item)
                            print(f"✅ Validated {{filename}} item {{idx}} with {item_model_name}")
                        except ValidationError as e:
                            pytest.fail(f"{item_model_name} validation failed for {{filename}} item {{idx}}: {{e}}")'''
            if item_model_name
            else ""
        }
                else:
                    # For non-list models, validate individual items using the same model
                    for idx, item in enumerate(data["items"][:3]):
                        try:
                            model_instance = {model_name}(**item)
                            self._validate_{
            self._to_snake_case(model_name)
        }_fields(model_instance, item)
                            print(f"✅ Validated {{filename}} item {{idx}}")
                        except ValidationError as e:
                            pytest.fail(f"{
            model_name
        } validation failed for {{filename}} item {{idx}}: {{e}}")
            else:
                # Validate single response
                try:
                    model_instance = {model_name}(**data)
                    self._validate_{
            self._to_snake_case(model_name)
        }_fields(model_instance, data)
                    print(f"✅ Validated {{filename}}")
                except ValidationError as e:
                    pytest.fail(f"{
            model_name
        } validation failed for {{filename}}: {{e}}")
    
    def _validate_{self._to_snake_case(model_name)}_fields(self, model: {
            model_name
        }, original_data: dict):
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
                validations.append(
                    f"assert hasattr(model, '{prop_name}'), \"Missing required field: {prop_name}\""
                )

            # Add type validations for specific fields
            for prop in model_info.properties[:3]:  # Limit to first 3
                if prop.type == "string" and prop.enum:
                    validations.append(
                        f"if hasattr(model, '{prop.name}') and getattr(model, '{prop.name}') is not None:\n"
                        f"            assert getattr(model, '{prop.name}') in {prop.enum}, "
                        f'"Invalid enum value for {prop.name}"'
                    )

        # Add common validations based on model name patterns
        if "ListResponse" in model_name:
            validations.extend(
                [
                    "# List response validations",
                    "assert hasattr(model, 'items'), \"List response should have 'items' field\"",
                    "assert hasattr(model, 'totalResults'), \"List response should have 'totalResults' field\"",
                ]
            )

        if not validations:
            validations.append("pass  # Add specific field validations as needed")

        return "\n        ".join(validations)

    def _to_snake_case(self, name: str) -> str:
        """Convert CamelCase to snake_case."""
        # Insert underscore before uppercase letters
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

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

    def generate_summary_report(self) -> None:
        """Generate a comprehensive summary report using Rich tables."""
        try:
            from rich.console import Console
            from rich.table import Table
            from rich.panel import Panel
            from rich import box
        except ImportError:
            print("Rich library not available. Install with: uv add rich")
            print("Falling back to text-based report...")
            self._generate_text_report()
            return

        console = Console()

        # Calculate comprehensive statistics
        stats = self._calculate_comprehensive_stats()

        # Main Coverage Table
        coverage_table = Table(
            title="📊 pyOFSC API Coverage Summary",
            box=box.ROUNDED,
            header_style="bold magenta",
        )
        coverage_table.add_column("Metric", style="cyan", width=35)
        coverage_table.add_column("All Endpoints", justify="right", style="bold white")
        coverage_table.add_column("GET Endpoints", justify="right", style="bold green")
        coverage_table.add_column("GET Coverage", justify="right", style="bold yellow")

        # Add rows to coverage table
        coverage_table.add_row(
            "🌐 Total Endpoints (Registry)",
            str(stats["total_endpoints"]),
            str(stats["get_endpoints"]),
            f"{(stats['get_endpoints'] / stats['total_endpoints'] * 100):.1f}%",
        )
        coverage_table.add_row(
            "💾 Saved Response Files",
            str(stats["total_responses"]),
            str(stats["get_responses"] + stats["get_error_responses"]),
            f"{((stats['get_responses'] + stats['get_error_responses']) / stats['total_responses'] * 100):.1f}%",
        )
        coverage_table.add_row(
            "❌ Error Responses (>=400)",
            str(stats["error_responses"]),
            str(stats["get_error_responses"]),
            f"{(stats['get_error_responses'] / (stats['get_responses'] + stats['get_error_responses']) * 100 if (stats['get_responses'] + stats['get_error_responses']) > 0 else 0):.1f}%",
        )
        coverage_table.add_row(
            "✅ Success Response Files",
            str(stats["total_responses"] - stats["error_responses"]),
            str(stats["get_responses"]),
            f"{(stats['get_responses'] / (stats['get_responses'] + stats['get_error_responses']) * 100 if (stats['get_responses'] + stats['get_error_responses']) > 0 else 0):.1f}%",
        )
        coverage_table.add_row(
            "🧪 Response Files with Tests",
            str(stats["responses_with_tests"]),
            str(stats["get_responses_with_tests"]),
            f"{(stats['get_responses_with_tests'] / stats['get_responses'] * 100 if stats['get_responses'] > 0 else 0):.1f}%",
        )
        coverage_table.add_row(
            "🎯 Final Test Coverage",
            f"{(stats['responses_with_tests'] / stats['total_endpoints'] * 100):.1f}%",
            f"{(stats['get_responses_with_tests'] / stats['get_endpoints'] * 100):.1f}%",
            f"{stats['get_responses_with_tests']}/{stats['get_endpoints']}",
        )

        # Module Breakdown Table
        module_table = Table(
            title="📁 Coverage by Module", box=box.ROUNDED, header_style="bold blue"
        )
        module_table.add_column("Module", style="cyan")
        module_table.add_column("Endpoints", justify="right")
        module_table.add_column("GET Endpoints", justify="right", style="green")
        module_table.add_column("Responses", justify="right")
        module_table.add_column("Error Responses", justify="right", style="red")
        module_table.add_column("GET Responses", justify="right", style="green")
        module_table.add_column("Tests", justify="right", style="yellow")
        module_table.add_column("GET Tests", justify="right", style="bright_green")
        module_table.add_column("Coverage", justify="right", style="bold magenta")

        for module, module_stats in sorted(stats["by_module"].items()):
            coverage_pct = (
                (module_stats["get_tests"] / module_stats["get_endpoints"] * 100)
                if module_stats["get_endpoints"] > 0
                else 0
            )
            module_table.add_row(
                module,
                str(module_stats["endpoints"]),
                str(module_stats["get_endpoints"]),
                str(module_stats["responses"]),
                str(module_stats["error_responses"]),
                str(module_stats["get_responses"]),
                str(module_stats["tests"]),
                str(module_stats["get_tests"]),
                f"{coverage_pct:.1f}%",
            )

        # Test Generation Summary Table
        test_table = Table(
            title="🧪 Generated Test Files Summary",
            box=box.ROUNDED,
            header_style="bold green",
        )
        test_table.add_column("Module", style="cyan")
        test_table.add_column("Models Tested", justify="right", style="yellow")
        test_table.add_column("Test Methods", justify="right", style="green")
        test_table.add_column("Response Files Used", justify="right", style="blue")

        for module in ["core", "metadata", "capacity"]:
            module_stats = stats["test_generation"].get(
                module, {"models": 0, "methods": 0, "files": 0}
            )
            test_table.add_row(
                module.title(),
                str(module_stats["models"]),
                str(module_stats["methods"]),
                str(module_stats["files"]),
            )

        # Display everything
        console.print()
        console.print(
            Panel.fit(
                "🎯 pyOFSC Model Validation Test Coverage Report", style="bold blue"
            )
        )
        console.print()
        console.print(coverage_table)
        console.print()
        console.print(module_table)
        console.print()
        console.print(test_table)
        console.print()

        # Summary insights
        insights = []
        insights.append(
            f"📈 GET endpoint test coverage: {stats['get_responses_with_tests']}/{stats['get_endpoints']} ({(stats['get_responses_with_tests'] / stats['get_endpoints'] * 100):.1f}%)"
        )
        insights.append(f"💾 Total response files analyzed: {stats['total_responses']}")
        insights.append(
            f"🎯 Models with validation tests: {sum(stats['test_generation'][m]['models'] for m in stats['test_generation'])}"
        )
        insights.append(
            f"🔍 Unique endpoints covered: {len(set(stats['covered_endpoints']))}"
        )

        console.print(
            Panel("\n".join(insights), title="📊 Key Insights", style="bright_blue")
        )
        console.print()

    def _calculate_comprehensive_stats(self) -> dict:
        """Calculate comprehensive statistics for the coverage report."""
        stats = {
            "total_endpoints": len(self.endpoints),
            "get_endpoints": len([e for e in self.endpoints if e.method == "GET"]),
            "total_responses": 0,
            "get_responses": 0,
            "responses_with_tests": 0,
            "get_responses_with_tests": 0,
            "error_responses": 0,
            "get_error_responses": 0,
            "covered_endpoints": set(),
            "by_module": {},
            "test_generation": {},
        }

        # Count response files
        response_files = list(self.response_dir.glob("*.json"))
        stats["total_responses"] = len(response_files)

        # Analyze each response file
        get_response_files = []
        responses_with_tests = []
        get_responses_with_tests = []

        for response_file in response_files:
            # Extract endpoint ID
            match = re.match(r"^(\d+)_", response_file.name)
            if not match:
                continue

            endpoint_id = int(match.group(1))
            endpoint = next((e for e in self.endpoints if e.id == endpoint_id), None)

            if endpoint:
                stats["covered_endpoints"].add(endpoint_id)

                # Check if this is an error response
                is_error_response = self._is_error_response(response_file)
                if is_error_response:
                    stats["error_responses"] += 1
                    if endpoint.method == "GET":
                        stats["get_error_responses"] += 1
                    continue  # Skip error responses for test generation

                # Count GET responses (only successful ones)
                if endpoint.method == "GET":
                    get_response_files.append(response_file)

                # Check if this response has a test (model is mapped)
                if endpoint_id in self.endpoint_to_model_map:
                    model_name = self.endpoint_to_model_map[endpoint_id]
                    if model_name in self.model_import_map:
                        responses_with_tests.append(response_file)
                        if endpoint.method == "GET":
                            get_responses_with_tests.append(response_file)

        stats["get_responses"] = len(get_response_files)
        stats["responses_with_tests"] = len(responses_with_tests)
        stats["get_responses_with_tests"] = len(get_responses_with_tests)

        # Calculate by-module statistics (group by high-level modules)
        for endpoint in self.endpoints:
            detailed_module = endpoint.tags[0] if endpoint.tags else "unknown"

            # Map detailed module tags to high-level modules
            if detailed_module.startswith("Core/") or detailed_module == "Core":
                module = "core"
            elif (
                detailed_module.startswith("Metadata/") or detailed_module == "Metadata"
            ):
                module = "metadata"
            elif (
                detailed_module.startswith("Capacity/") or detailed_module == "Capacity"
            ):
                module = "capacity"
            else:
                module = "other"

            if module not in stats["by_module"]:
                stats["by_module"][module] = {
                    "endpoints": 0,
                    "get_endpoints": 0,
                    "responses": 0,
                    "error_responses": 0,
                    "get_responses": 0,
                    "tests": 0,
                    "get_tests": 0,
                }

            stats["by_module"][module]["endpoints"] += 1
            if endpoint.method == "GET":
                stats["by_module"][module]["get_endpoints"] += 1

            # Check if endpoint has response
            endpoint_responses = [
                f for f in response_files if f.name.startswith(f"{endpoint.id}_")
            ]
            if endpoint_responses:
                # Count all responses
                stats["by_module"][module]["responses"] += len(endpoint_responses)

                # Separate error responses from success responses
                error_count = sum(
                    1 for f in endpoint_responses if self._is_error_response(f)
                )
                success_count = len(endpoint_responses) - error_count

                stats["by_module"][module]["error_responses"] += error_count

                if endpoint.method == "GET":
                    stats["by_module"][module]["get_responses"] += success_count

                # Check if has test (only for success responses)
                if success_count > 0 and endpoint.id in self.endpoint_to_model_map:
                    model_name = self.endpoint_to_model_map[endpoint.id]
                    if model_name in self.model_import_map:
                        stats["by_module"][module]["tests"] += success_count
                        if endpoint.method == "GET":
                            stats["by_module"][module]["get_tests"] += success_count

        # Calculate test generation statistics
        for module in ["core", "metadata", "capacity"]:
            stats["test_generation"][module] = {"models": 0, "methods": 0, "files": 0}

            # Count models tested in this module
            models_tested = set()
            methods_count = 0
            files_used = set()

            for model_name, response_files in self.model_to_responses_map.items():
                if model_name in self.model_import_map:
                    import_path = self.model_import_map[model_name]
                    if f".models.{module}." in import_path:
                        models_tested.add(model_name)
                        methods_count += 1
                        files_used.update(f.name for f in response_files)

            stats["test_generation"][module]["models"] = len(models_tested)
            stats["test_generation"][module]["methods"] = methods_count
            stats["test_generation"][module]["files"] = len(files_used)

        return stats

    def analyze_pipeline_and_generate_log(self) -> str:
        """Analyze the test generation pipeline and create detailed log report."""
        from datetime import datetime

        # Create timestamp for log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = (
            Path(__file__).parent.parent
            / "logs"
            / f"test_generation_pipeline_analysis_{timestamp}.md"
        )

        # Perform detailed pipeline analysis
        analysis = self._perform_pipeline_analysis()

        # Generate comprehensive log report
        log_content = self._generate_pipeline_log_content(analysis, timestamp)

        # Write log file
        log_file.write_text(log_content)

        return str(log_file)

    def _perform_pipeline_analysis(self) -> dict:
        """Perform detailed analysis of the test generation pipeline."""
        analysis = {
            "total_files": 0,
            "step_results": {
                "valid_pattern": {"passed": [], "failed": []},
                "endpoint_found": {"passed": [], "failed": []},
                "has_signature": {"passed": [], "failed": []},
                "model_extracted": {"passed": [], "failed": []},
                "model_mapped": {"passed": [], "failed": []},
            },
            "failure_categories": {
                "invalid_filename": [],
                "missing_endpoint": [],
                "no_signature": [],
                "no_model_name": [],
                "unmapped_model": [],
            },
            "endpoint_analysis": {},
            "model_analysis": {},
            "summary_stats": {},
        }

        # Get all response files
        response_files = list(self.response_dir.glob("*.json"))
        analysis["total_files"] = len(response_files)

        # Track error responses separately
        error_response_files = []

        for response_file in response_files:
            # Check if this is an error response first
            is_error = self._is_error_response(response_file)
            if is_error:
                error_response_files.append(response_file.name)
                continue  # Skip error responses from pipeline analysis

            file_analysis = {
                "filename": response_file.name,
                "endpoint_id": None,
                "endpoint": None,
                "model_name": None,
                "has_test": False,
                "failure_reason": None,
                "failure_step": None,
            }

            # Step 1: Extract endpoint ID from filename
            match = re.match(r"^(\d+)_", response_file.name)
            if not match:
                file_analysis["failure_reason"] = "Invalid filename pattern"
                file_analysis["failure_step"] = "valid_pattern"
                analysis["step_results"]["valid_pattern"]["failed"].append(
                    file_analysis
                )
                analysis["failure_categories"]["invalid_filename"].append(file_analysis)
                continue

            endpoint_id = int(match.group(1))
            file_analysis["endpoint_id"] = endpoint_id
            analysis["step_results"]["valid_pattern"]["passed"].append(file_analysis)

            # Step 2: Find endpoint in registry
            endpoint = next((e for e in self.endpoints if e.id == endpoint_id), None)
            if not endpoint:
                file_analysis["failure_reason"] = (
                    f"Endpoint #{endpoint_id} not found in registry"
                )
                file_analysis["failure_step"] = "endpoint_found"
                analysis["step_results"]["endpoint_found"]["failed"].append(
                    file_analysis
                )
                analysis["failure_categories"]["missing_endpoint"].append(file_analysis)
                continue

            file_analysis["endpoint"] = {
                "id": endpoint.id,
                "method": endpoint.method,
                "path": endpoint.path,
                "tags": endpoint.tags,
            }
            analysis["step_results"]["endpoint_found"]["passed"].append(file_analysis)

            # Step 3: Check for signature or response schema
            has_signature = bool(endpoint.signature or endpoint.response_schema)
            if not has_signature:
                file_analysis["failure_reason"] = "No signature or response_schema"
                file_analysis["failure_step"] = "has_signature"
                analysis["step_results"]["has_signature"]["failed"].append(
                    file_analysis
                )
                analysis["failure_categories"]["no_signature"].append(file_analysis)
                continue

            analysis["step_results"]["has_signature"]["passed"].append(file_analysis)

            # Step 4: Extract model name
            model_name = None
            if endpoint.signature:
                match = re.search(r"->\s*(\w+)", endpoint.signature)
                if match:
                    model_name = match.group(1)
            elif endpoint.response_schema:
                model_name = endpoint.response_schema

            if not model_name:
                file_analysis["failure_reason"] = (
                    "Could not extract model name from signature/schema"
                )
                file_analysis["failure_step"] = "model_extracted"
                analysis["step_results"]["model_extracted"]["failed"].append(
                    file_analysis
                )
                analysis["failure_categories"]["no_model_name"].append(file_analysis)
                continue

            file_analysis["model_name"] = model_name
            analysis["step_results"]["model_extracted"]["passed"].append(file_analysis)

            # Step 5: Check if model is in import map
            if model_name not in self.model_import_map:
                file_analysis["failure_reason"] = (
                    f'Model "{model_name}" not in import map'
                )
                file_analysis["failure_step"] = "model_mapped"
                analysis["step_results"]["model_mapped"]["failed"].append(file_analysis)
                analysis["failure_categories"]["unmapped_model"].append(file_analysis)
                continue

            # Success - this file should have a test
            file_analysis["has_test"] = True
            analysis["step_results"]["model_mapped"]["passed"].append(file_analysis)

        # Calculate summary statistics
        analysis["summary_stats"] = {
            "total_files": len(response_files),
            "error_responses": len(error_response_files),
            "success_responses": len(response_files) - len(error_response_files),
            "valid_pattern": len(analysis["step_results"]["valid_pattern"]["passed"]),
            "endpoint_found": len(analysis["step_results"]["endpoint_found"]["passed"]),
            "has_signature": len(analysis["step_results"]["has_signature"]["passed"]),
            "model_extracted": len(
                analysis["step_results"]["model_extracted"]["passed"]
            ),
            "model_mapped": len(analysis["step_results"]["model_mapped"]["passed"]),
            "final_tests": len(analysis["step_results"]["model_mapped"]["passed"]),
        }

        # Add error response list to analysis
        analysis["error_response_files"] = error_response_files

        return analysis

    def _generate_pipeline_log_content(self, analysis: dict, timestamp: str) -> str:
        """Generate comprehensive log report content."""
        stats = analysis["summary_stats"]

        content = f"""# Test Generation Pipeline Analysis Report

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}  
**Script:** generate_model_validation_tests.py  
**Analysis ID:** {timestamp}

## Executive Summary

📊 **Pipeline Performance:**
- **Total Response Files:** {stats["total_files"]}
- **Error Responses (>=400):** {stats["error_responses"]} ({(stats["error_responses"] / stats["total_files"] * 100):.1f}%)
- **Success Response Files:** {stats["success_responses"]}
- **Files with Generated Tests:** {stats["final_tests"]}
- **Test Coverage (of Success Files):** {(stats["final_tests"] / stats["success_responses"] * 100 if stats["success_responses"] > 0 else 0):.1f}%
- **Files Lost in Pipeline:** {stats["success_responses"] - stats["final_tests"]}

🚨 **Primary Bottlenecks:**
1. **Unmapped Models:** {len(analysis["failure_categories"]["unmapped_model"])} files ({(len(analysis["failure_categories"]["unmapped_model"]) / stats["total_files"] * 100):.1f}%)
2. **Missing Signatures:** {len(analysis["failure_categories"]["no_signature"])} files ({(len(analysis["failure_categories"]["no_signature"]) / stats["total_files"] * 100):.1f}%)
3. **Missing Endpoints:** {len(analysis["failure_categories"]["missing_endpoint"])} files ({(len(analysis["failure_categories"]["missing_endpoint"]) / stats["total_files"] * 100):.1f}%)

## Pipeline Flow Analysis

```
Response Files → Error Filter → Valid Pattern → Endpoint Found → Has Signature → Model Extracted → Model Mapped → Tests Generated
     {stats["total_files"]}       →   {stats["success_responses"]}   →      {stats["valid_pattern"]}      →      {stats["endpoint_found"]}       →      {stats["has_signature"]}      →       {stats["model_extracted"]}       →      {stats["model_mapped"]}      →       {stats["final_tests"]}
                  ↓              ↓              ↓             ↓               ↓              ↓
    Error Responses: {stats["error_responses"]}       Lost: {stats["success_responses"] - stats["valid_pattern"]}        Lost: {stats["valid_pattern"] - stats["endpoint_found"]}       Lost: {stats["endpoint_found"] - stats["has_signature"]}        Lost: {stats["has_signature"] - stats["model_extracted"]}        Lost: {stats["model_extracted"] - stats["model_mapped"]}        → SUCCESS
```

### Step-by-Step Breakdown

| Pipeline Step | Passed | Failed | Success Rate |
|---------------|--------|--------|-------------|
| 0. Success Response Filter | {stats["success_responses"]} | {stats["error_responses"]} | {(stats["success_responses"] / stats["total_files"] * 100):.1f}% |
| 1. Valid Filename Pattern | {stats["valid_pattern"]} | {stats["success_responses"] - stats["valid_pattern"]} | {(stats["valid_pattern"] / stats["success_responses"] * 100 if stats["success_responses"] > 0 else 0):.1f}% |
| 2. Endpoint Found in Registry | {stats["endpoint_found"]} | {stats["valid_pattern"] - stats["endpoint_found"]} | {(stats["endpoint_found"] / stats["valid_pattern"] * 100 if stats["valid_pattern"] > 0 else 0):.1f}% |
| 3. Has Signature/Schema | {stats["has_signature"]} | {stats["endpoint_found"] - stats["has_signature"]} | {(stats["has_signature"] / stats["endpoint_found"] * 100 if stats["endpoint_found"] > 0 else 0):.1f}% |
| 4. Model Name Extracted | {stats["model_extracted"]} | {stats["has_signature"] - stats["model_extracted"]} | {(stats["model_extracted"] / stats["has_signature"] * 100 if stats["has_signature"] > 0 else 0):.1f}% |
| 5. Model Import Mapped | {stats["model_mapped"]} | {stats["model_extracted"] - stats["model_mapped"]} | {(stats["model_mapped"] / stats["model_extracted"] * 100 if stats["model_extracted"] > 0 else 0):.1f}% |

## Detailed Failure Analysis

"""

        # Add detailed failure categories
        for category, failures in analysis["failure_categories"].items():
            if not failures:
                continue

            content += f"\n### {category.replace('_', ' ').title()} ({len(failures)} files)\n\n"

            if category == "invalid_filename":
                content += "**Files with invalid naming patterns:**\n"
                for failure in failures[:10]:  # Limit to first 10
                    content += f"- `{failure['filename']}` - Expected pattern: `{{endpoint_id}}_{{description}}.json`\n"
                if len(failures) > 10:
                    content += f"- ... and {len(failures) - 10} more files\n"

            elif category == "missing_endpoint":
                content += "**Endpoint IDs not found in registry:**\n"
                endpoint_ids = [f["endpoint_id"] for f in failures if f["endpoint_id"]]
                unique_ids = sorted(set(endpoint_ids))
                for endpoint_id in unique_ids[:15]:  # Limit to first 15
                    files = [
                        f["filename"]
                        for f in failures
                        if f["endpoint_id"] == endpoint_id
                    ]
                    content += f"- **Endpoint #{endpoint_id}:** {', '.join(files[:3])}"
                    if len(files) > 3:
                        content += f" (and {len(files) - 3} more)"
                    content += "\n"
                if len(unique_ids) > 15:
                    content += f"- ... and {len(unique_ids) - 15} more endpoint IDs\n"

            elif category == "no_signature":
                content += "**Endpoints without signatures or response schemas:**\n"
                for failure in failures[:10]:
                    endpoint = failure["endpoint"]
                    content += f"- **#{endpoint['id']}** `{endpoint['method']} {endpoint['path']}` - File: `{failure['filename']}`\n"
                if len(failures) > 10:
                    content += f"- ... and {len(failures) - 10} more endpoints\n"

            elif category == "unmapped_model":
                content += "**Model names not in import map:**\n"
                model_files = {}
                for failure in failures:
                    model_name = failure["model_name"]
                    if model_name not in model_files:
                        model_files[model_name] = []
                    model_files[model_name].append(failure["filename"])

                for model_name, files in sorted(model_files.items())[:15]:
                    content += f"- **`{model_name}`:** {', '.join(files[:3])}"
                    if len(files) > 3:
                        content += f" (and {len(files) - 3} more files)"
                    content += "\n"

                if len(model_files) > 15:
                    content += f"- ... and {len(model_files) - 15} more models\n"

        # Add recommendations
        content += f"""

## Recommendations for Improvement

### 1. High-Impact Actions (Target: +{len(analysis["failure_categories"]["unmapped_model"])} tests)

**Add Missing Model Mappings:**
The biggest bottleneck is unmapped models. Add these to MODEL_IMPORT_MAP:

```python
# Add to MODEL_IMPORT_MAP in generate_model_validation_tests.py
"""

        # Get unique unmapped models
        unmapped_models = {}
        for failure in analysis["failure_categories"]["unmapped_model"]:
            model_name = failure["model_name"]
            if model_name not in unmapped_models:
                unmapped_models[model_name] = len(
                    [
                        f
                        for f in analysis["failure_categories"]["unmapped_model"]
                        if f["model_name"] == model_name
                    ]
                )

        for model_name, count in sorted(
            unmapped_models.items(), key=lambda x: x[1], reverse=True
        )[:10]:
            content += f'"{model_name}": "ofsc.models.{model_name.lower().replace("response", "").replace("list", "")}.{model_name}",  # +{count} tests\n'

        content += f"""```

### 2. Medium-Impact Actions (Target: +{len(analysis["failure_categories"]["no_signature"])} tests)

**Add Missing Signatures:**
Update endpoint registry with return type signatures for:

"""

        for failure in analysis["failure_categories"]["no_signature"][:5]:
            endpoint = failure["endpoint"]
            content += f"- Endpoint #{endpoint['id']}: `{endpoint['method']} {endpoint['path']}`\n"

        content += f"""

### 3. Registry Maintenance (Target: +{len(analysis["failure_categories"]["missing_endpoint"])} tests)

**Add Missing Endpoints:**
Update endpoint registry to include these endpoint IDs:

"""

        missing_ids = sorted(
            set(
                f["endpoint_id"]
                for f in analysis["failure_categories"]["missing_endpoint"]
                if f["endpoint_id"]
            )
        )
        content += f"{', '.join(f'#{id}' for id in missing_ids[:20])}\n"
        if len(missing_ids) > 20:
            content += f"... and {len(missing_ids) - 20} more\n"

        content += f"""

## Implementation Priority

| Priority | Action | Impact | Effort | Files Affected |
|----------|--------|--------|--------|---------------|
| 🔥 HIGH | Add unmapped model imports | +{len(analysis["failure_categories"]["unmapped_model"])} tests | Low | MODEL_IMPORT_MAP |
| 🟡 MEDIUM | Add missing signatures | +{len(analysis["failure_categories"]["no_signature"])} tests | Medium | Endpoint registry |
| 🔵 LOW | Add missing endpoints | +{len(analysis["failure_categories"]["missing_endpoint"])} tests | High | Swagger/Registry |

**Potential Maximum Coverage:** {stats["final_tests"] + len(analysis["failure_categories"]["unmapped_model"]) + len(analysis["failure_categories"]["no_signature"])}/{stats["success_responses"]} ({((stats["final_tests"] + len(analysis["failure_categories"]["unmapped_model"]) + len(analysis["failure_categories"]["no_signature"])) / stats["success_responses"] * 100 if stats["success_responses"] > 0 else 0):.1f}%)

## Error Response Files (Excluded from Test Generation)

**Error Responses ({stats["error_responses"]} files):**

These files contain HTTP error responses (status_code >= 400) and are automatically excluded from test generation as they don't represent valid data models.

"""

        for error_file in analysis["error_response_files"][:10]:
            content += (
                f"- `{error_file}` → Status >= 400 → ❌ Skipped (Error Response)\n"
            )
        if len(analysis["error_response_files"]) > 10:
            content += f"- ... and {len(analysis['error_response_files']) - 10} more error responses\n"

        content += f"""

## Files Successfully Generating Tests

**Current Success Cases ({stats["final_tests"]} files):**
"""

        successful_files = analysis["step_results"]["model_mapped"]["passed"]
        for success in successful_files[:10]:
            content += f"- `{success['filename']}` → {success['model_name']} → ✅ Test Generated\n"
        if len(successful_files) > 10:
            content += f"- ... and {len(successful_files) - 10} more successful cases\n"

        content += """

---
*Generated by pyOFSC Model Validation Test Generator*  
*For questions or improvements, check scripts/generate_model_validation_tests.py*
"""

        return content

    def _generate_text_report(self) -> None:
        """Fallback text-based report when Rich is not available."""
        stats = self._calculate_comprehensive_stats()

        print("=" * 80)
        print("MODEL VALIDATION TEST COVERAGE REPORT")
        print("=" * 80)
        print()
        print(f"Total endpoints: {stats['total_endpoints']}")
        print(f"GET endpoints: {stats['get_endpoints']}")
        print(f"Total saved responses: {stats['total_responses']}")
        print(f"GET saved responses: {stats['get_responses']}")
        print(f"Responses with tests: {stats['responses_with_tests']}")
        print(f"GET responses with tests: {stats['get_responses_with_tests']}")
        print(
            f"GET endpoint test coverage: {(stats['get_responses_with_tests'] / stats['get_endpoints'] * 100):.1f}%"
        )
        print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate model validation tests from saved API responses"
    )
    parser.add_argument(
        "--module",
        choices=["core", "metadata", "capacity"],
        help="Generate tests for specific module only",
    )
    parser.add_argument(
        "--output-dir", type=Path, help="Output directory for generated tests"
    )
    parser.add_argument(
        "--summary", action="store_true", help="Show coverage summary report"
    )
    parser.add_argument(
        "--analyze-pipeline",
        action="store_true",
        help="Analyze test generation pipeline and create detailed log report",
    )

    args = parser.parse_args()

    generator = ModelValidationTestGenerator()

    if args.summary:
        generator.generate_summary_report()
        return

    if args.analyze_pipeline:
        log_file = generator.analyze_pipeline_and_generate_log()
        print("📊 Pipeline analysis complete!")
        print(f"📄 Detailed report generated: {log_file}")
        print("\nTo view the report:")
        print(f"  cat {log_file}")
        return

    # Generate tests
    if args.module:
        output_dir = (
            args.output_dir
            or Path(__file__).parent.parent / "tests" / "models" / "generated"
        )
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
