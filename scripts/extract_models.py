#!/usr/bin/env python3
"""
Script to extract model information from swagger.json and create the models registry.

This script analyzes all schema definitions in swagger.json, maps them to endpoints,
identifies relationships with Pydantic models, and generates a comprehensive models registry.
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import sys

# Add the project root to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.utils.schema_mapper import SchemaModelMapper


@dataclass
class ModelProperty:
    """Represents a property of a model schema."""

    name: str
    type: str
    description: str
    required: bool
    format: Optional[str] = None
    enum: Optional[List[str]] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    minimum: Optional[int] = None
    maximum: Optional[int] = None
    items: Optional[Dict[str, Any]] = None  # For arrays
    ref: Optional[str] = None  # For object references
    default: Optional[Any] = None


@dataclass
class ModelInfo:
    """Represents complete model schema information."""

    name: str
    description: str
    properties: List[ModelProperty]
    required_properties: List[str]
    inheritance: List[str]  # allOf references
    used_in_endpoints: List[str]  # endpoint paths that use this schema
    used_in_request_endpoints: List[str]  # endpoints using this as request body
    used_in_response_endpoints: List[str]  # endpoints using this as response
    mapped_pydantic_class: Optional[str]
    module: str  # core, metadata, capacity, etc.
    schema_type: str  # object, array, etc.
    examples: List[Dict[str, Any]]
    nested_models: List[str]  # Other models referenced by this model
    parent_models: List[str]  # Models that reference this model


def get_module_from_endpoint_usage(used_in_endpoints: List[str]) -> str:
    """Determine the primary module for a model based on its endpoint usage."""
    if not used_in_endpoints:
        return "unknown"

    module_counts = {}
    for endpoint in used_in_endpoints:
        if "/ofscMetadata/" in endpoint:
            module = "metadata"
        elif "/ofscCore/" in endpoint:
            module = "core"
        elif "/ofscCapacity/" in endpoint:
            module = "capacity"
        elif "/ofscStatistics/" in endpoint:
            module = "statistics"
        elif "/ofscPartsCatalog/" in endpoint:
            module = "partscatalog"
        elif "/ofscCollaboration/" in endpoint:
            module = "collaboration"
        elif "/oauthTokenService/" in endpoint:
            module = "auth"
        else:
            module = "unknown"

        module_counts[module] = module_counts.get(module, 0) + 1

    # Return the most common module
    return max(module_counts.items(), key=lambda x: x[1])[0]


def parse_model_property(
    prop_name: str, prop_data: Dict[str, Any], required_props: List[str]
) -> ModelProperty:
    """Parse a single property from a schema definition."""
    prop_type = prop_data.get("type", "unknown")

    # Handle $ref properties
    ref = prop_data.get("$ref")
    if ref:
        ref_name = ref.replace("#/definitions/", "")
        prop_type = f"ref:{ref_name}"

    # Handle array items
    items = None
    if prop_type == "array":
        items_data = prop_data.get("items")
        if items_data:
            items = {
                "type": items_data.get("type", "unknown"),
                "$ref": items_data.get("$ref", "").replace("#/definitions/", "")
                if items_data.get("$ref")
                else None,
            }

    return ModelProperty(
        name=prop_name,
        type=prop_type,
        description=prop_data.get("description", "")
        .replace("<p>", "")
        .replace("</p>", "")
        .strip(),
        required=prop_name in required_props,
        format=prop_data.get("format"),
        enum=prop_data.get("enum"),
        min_length=prop_data.get("minLength"),
        max_length=prop_data.get("maxLength"),
        minimum=prop_data.get("minimum"),
        maximum=prop_data.get("maximum"),
        items=items,
        ref=ref.replace("#/definitions/", "") if ref else None,
        default=prop_data.get("default"),
    )


def extract_inheritance_chain(schema_def: Dict[str, Any]) -> List[str]:
    """Extract inheritance chain from allOf patterns."""
    inheritance = []

    all_of = schema_def.get("allOf", [])
    for item in all_of:
        ref = item.get("$ref")
        if ref:
            inheritance.append(ref.replace("#/definitions/", ""))

    return inheritance


def extract_nested_references(schema_def: Dict[str, Any]) -> List[str]:
    """Extract all model references nested within this schema."""
    nested_models = set()

    def find_refs_recursive(obj: Any):
        if isinstance(obj, dict):
            # Direct $ref
            if "$ref" in obj:
                ref_name = obj["$ref"].replace("#/definitions/", "")
                nested_models.add(ref_name)
            # Recurse into nested objects
            for value in obj.values():
                find_refs_recursive(value)
        elif isinstance(obj, list):
            for item in obj:
                find_refs_recursive(item)

    find_refs_recursive(schema_def)
    return list(nested_models)


def load_swagger_definitions(swagger_file: str) -> Dict[str, Any]:
    """Load schema definitions from swagger.json."""
    with open(swagger_file, "r") as f:
        swagger = json.load(f)

    return swagger.get("definitions", {})


def find_schema_usage_in_endpoints(
    swagger_file: str,
) -> Dict[str, Dict[str, List[str]]]:
    """Find which endpoints use each schema for requests and responses."""
    with open(swagger_file, "r") as f:
        swagger = json.load(f)

    schema_usage = {}  # schema_name -> {"request": [endpoints], "response": [endpoints]}

    paths = swagger.get("paths", {})
    for path, methods in paths.items():
        for method_name, method_data in methods.items():
            if method_name.lower() not in ["get", "post", "put", "patch", "delete"]:
                continue

            endpoint_key = f"{method_name.upper()} {path}"

            # Check request body schemas
            for param in method_data.get("parameters", []):
                if param.get("in") == "body":
                    schema_ref = param.get("schema", {}).get("$ref", "")
                    if schema_ref:
                        schema_name = schema_ref.replace("#/definitions/", "")
                        if schema_name not in schema_usage:
                            schema_usage[schema_name] = {"request": [], "response": []}
                        schema_usage[schema_name]["request"].append(endpoint_key)

            # Check response schemas
            responses = method_data.get("responses", {})
            for status_code, response_data in responses.items():
                if status_code == "200":  # Focus on successful responses
                    schema_ref = response_data.get("schema", {}).get("$ref", "")
                    if schema_ref:
                        schema_name = schema_ref.replace("#/definitions/", "")
                        if schema_name not in schema_usage:
                            schema_usage[schema_name] = {"request": [], "response": []}
                        schema_usage[schema_name]["response"].append(endpoint_key)

    return schema_usage


def extract_models_from_swagger(swagger_file: str) -> List[ModelInfo]:
    """Extract all model information from swagger.json."""
    print("Loading swagger definitions...")
    definitions = load_swagger_definitions(swagger_file)
    print(f"Found {len(definitions)} schema definitions")

    print("Analyzing endpoint-schema relationships...")
    schema_usage = find_schema_usage_in_endpoints(swagger_file)

    print("Initializing Pydantic model mapper...")
    schema_mapper = SchemaModelMapper()

    models = []

    print("Processing schema definitions...")
    for schema_name, schema_def in definitions.items():
        # Extract basic information
        description = schema_def.get("description", "")
        schema_type = schema_def.get("type", "object")

        # Extract properties
        properties = []
        required_props = schema_def.get("required", [])

        # Handle properties from schema definition
        props_data = schema_def.get("properties", {})
        for prop_name, prop_data in props_data.items():
            properties.append(
                parse_model_property(prop_name, prop_data, required_props)
            )

        # Handle properties from allOf inheritance
        all_of = schema_def.get("allOf", [])
        for inherited_schema in all_of:
            if "properties" in inherited_schema:
                inherited_required = inherited_schema.get("required", [])
                for prop_name, prop_data in inherited_schema["properties"].items():
                    properties.append(
                        parse_model_property(prop_name, prop_data, inherited_required)
                    )

        # Extract inheritance chain
        inheritance = extract_inheritance_chain(schema_def)

        # Extract nested model references
        nested_models = extract_nested_references(schema_def)

        # Get endpoint usage
        usage = schema_usage.get(schema_name, {"request": [], "response": []})
        all_endpoints = usage["request"] + usage["response"]

        # Determine module based on endpoint usage
        module = get_module_from_endpoint_usage(all_endpoints)

        # Try to map to Pydantic model
        pydantic_class = schema_mapper.get_model_class_by_schema_name(schema_name)
        mapped_pydantic_class = pydantic_class.__name__ if pydantic_class else None

        # Create model info
        model_info = ModelInfo(
            name=schema_name,
            description=description,
            properties=properties,
            required_properties=required_props,
            inheritance=inheritance,
            used_in_endpoints=all_endpoints,
            used_in_request_endpoints=usage["request"],
            used_in_response_endpoints=usage["response"],
            mapped_pydantic_class=mapped_pydantic_class,
            module=module,
            schema_type=schema_type,
            examples=[],  # Could be extracted from swagger examples if available
            nested_models=nested_models,
            parent_models=[],  # Will be populated in post-processing
        )

        models.append(model_info)

    # Post-process to populate parent_models (reverse references)
    print("Building reverse reference mappings...")
    model_by_name = {model.name: model for model in models}
    for model in models:
        for nested_model_name in model.nested_models:
            if nested_model_name in model_by_name:
                model_by_name[nested_model_name].parent_models.append(model.name)

    print(f"Extracted {len(models)} model definitions")
    return models


def generate_registry_module(models: List[ModelInfo]) -> str:
    """Generate the Python module content for models registry."""

    module_content = '''"""
OFSC API Models Registry

This module provides a comprehensive registry of all Oracle Field Service Cloud (OFSC) API model schemas
parsed from the swagger.json specification. It includes model metadata, properties, relationships,
endpoint usage, and Pydantic model mappings.

Generated automatically from swagger.json - DO NOT EDIT MANUALLY
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class ModelProperty:
    """Represents a property of a model schema."""
    name: str
    type: str
    description: str
    required: bool
    format: Optional[str] = None
    enum: Optional[List[str]] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    minimum: Optional[int] = None
    maximum: Optional[int] = None
    items: Optional[Dict[str, Any]] = None  # For arrays
    ref: Optional[str] = None  # For object references
    default: Optional[Any] = None


@dataclass 
class ModelInfo:
    """Represents complete model schema information."""
    name: str
    description: str
    properties: List[ModelProperty]
    required_properties: List[str]
    inheritance: List[str]  # allOf references
    used_in_endpoints: List[str]  # endpoint paths that use this schema
    used_in_request_endpoints: List[str]  # endpoints using this as request body
    used_in_response_endpoints: List[str]  # endpoints using this as response
    mapped_pydantic_class: Optional[str]
    module: str  # core, metadata, capacity, etc.
    schema_type: str  # object, array, etc.
    examples: List[Dict[str, Any]]
    nested_models: List[str]  # Other models referenced by this model
    parent_models: List[str]  # Models that reference this model


# All models from swagger.json definitions
MODELS: Dict[str, ModelInfo] = {
'''

    # Generate model entries
    for model in models:
        module_content += f'    "{model.name}": ModelInfo(\n'
        module_content += f"        name={repr(model.name)},\n"
        module_content += f"        description={repr(model.description)},\n"

        # Properties
        module_content += "        properties=[\n"
        for prop in model.properties:
            module_content += "            ModelProperty(\n"
            module_content += f"                name={repr(prop.name)},\n"
            module_content += f"                type={repr(prop.type)},\n"
            module_content += f"                description={repr(prop.description)},\n"
            module_content += f"                required={prop.required},\n"
            if prop.format is not None:
                module_content += f"                format={repr(prop.format)},\n"
            if prop.enum is not None:
                module_content += f"                enum={repr(prop.enum)},\n"
            if prop.min_length is not None:
                module_content += f"                min_length={prop.min_length},\n"
            if prop.max_length is not None:
                module_content += f"                max_length={prop.max_length},\n"
            if prop.minimum is not None:
                module_content += f"                minimum={prop.minimum},\n"
            if prop.maximum is not None:
                module_content += f"                maximum={prop.maximum},\n"
            if prop.items is not None:
                module_content += f"                items={repr(prop.items)},\n"
            if prop.ref is not None:
                module_content += f"                ref={repr(prop.ref)},\n"
            if prop.default is not None:
                module_content += f"                default={repr(prop.default)},\n"
            module_content += "            ),\n"
        module_content += "        ],\n"

        # Other fields
        module_content += (
            f"        required_properties={repr(model.required_properties)},\n"
        )
        module_content += f"        inheritance={repr(model.inheritance)},\n"
        module_content += (
            f"        used_in_endpoints={repr(model.used_in_endpoints)},\n"
        )
        module_content += f"        used_in_request_endpoints={repr(model.used_in_request_endpoints)},\n"
        module_content += f"        used_in_response_endpoints={repr(model.used_in_response_endpoints)},\n"
        module_content += (
            f"        mapped_pydantic_class={repr(model.mapped_pydantic_class)},\n"
        )
        module_content += f"        module={repr(model.module)},\n"
        module_content += f"        schema_type={repr(model.schema_type)},\n"
        module_content += f"        examples={repr(model.examples)},\n"
        module_content += f"        nested_models={repr(model.nested_models)},\n"
        module_content += f"        parent_models={repr(model.parent_models)},\n"
        module_content += "    ),\n"

    module_content += "}\n\n"

    # Add utility functions and indexes
    module_content += '''
# Utility functions for model lookup and analysis

def get_model_by_name(name: str) -> Optional[ModelInfo]:
    """Get model by name."""
    return MODELS.get(name)


def get_models_by_module(module: str) -> List[ModelInfo]:
    """Get all models for a specific module."""
    return [model for model in MODELS.values() if model.module == module]


def get_models_for_endpoint(method: str, path: str) -> List[ModelInfo]:
    """Get all models used by a specific endpoint."""
    endpoint_key = f"{method.upper()} {path}"
    return [model for model in MODELS.values() if endpoint_key in model.used_in_endpoints]


def get_endpoints_using_model(model_name: str) -> List[str]:
    """Get all endpoints that use a specific model."""
    model = MODELS.get(model_name)
    return model.used_in_endpoints if model else []


def get_models_with_pydantic_mapping() -> List[ModelInfo]:
    """Get all models that have corresponding Pydantic classes."""
    return [model for model in MODELS.values() if model.mapped_pydantic_class is not None]


def get_models_without_pydantic_mapping() -> List[ModelInfo]:
    """Get all models that don't have corresponding Pydantic classes."""
    return [model for model in MODELS.values() if model.mapped_pydantic_class is None]


def get_model_inheritance_chain(model_name: str) -> List[str]:
    """Get the complete inheritance chain for a model."""
    model = MODELS.get(model_name)
    if not model:
        return []
    
    chain = []
    to_process = [model_name]
    processed = set()
    
    while to_process:
        current_name = to_process.pop(0)
        if current_name in processed:
            continue
        processed.add(current_name)
        
        current_model = MODELS.get(current_name)
        if current_model:
            chain.append(current_name)
            to_process.extend(current_model.inheritance)
    
    return chain


def get_models_by_property_type(property_type: str) -> List[ModelInfo]:
    """Get all models that have properties of a specific type."""
    result = []
    for model in MODELS.values():
        for prop in model.properties:
            if prop.type == property_type or (prop.ref and prop.ref == property_type):
                result.append(model)
                break
    return result


def generate_mapping_coverage_report() -> Dict[str, Any]:
    """Generate a comprehensive report on Pydantic mapping coverage."""
    total_models = len(MODELS)
    mapped_models = len(get_models_with_pydantic_mapping())
    unmapped_models = len(get_models_without_pydantic_mapping())
    
    # Group by module
    by_module = {}
    for module in set(model.module for model in MODELS.values()):
        module_models = get_models_by_module(module)
        module_mapped = [m for m in module_models if m.mapped_pydantic_class]
        by_module[module] = {
            "total": len(module_models),
            "mapped": len(module_mapped),
            "unmapped": len(module_models) - len(module_mapped),
            "coverage_percentage": (len(module_mapped) / len(module_models) * 100) if module_models else 0
        }
    
    return {
        "total_models": total_models,
        "mapped_models": mapped_models,
        "unmapped_models": unmapped_models,
        "overall_coverage_percentage": (mapped_models / total_models * 100) if total_models > 0 else 0,
        "by_module": by_module,
        "unmapped_model_names": [m.name for m in get_models_without_pydantic_mapping()]
    }


# Indexes for efficient lookup
MODELS_BY_MODULE: Dict[str, List[ModelInfo]] = {}
for model in MODELS.values():
    if model.module not in MODELS_BY_MODULE:
        MODELS_BY_MODULE[model.module] = []
    MODELS_BY_MODULE[model.module].append(model)

MODELS_BY_ENDPOINT: Dict[str, List[ModelInfo]] = {}
for model in MODELS.values():
    for endpoint in model.used_in_endpoints:
        if endpoint not in MODELS_BY_ENDPOINT:
            MODELS_BY_ENDPOINT[endpoint] = []
        MODELS_BY_ENDPOINT[endpoint].append(model)

MODELS_WITH_PYDANTIC_MAPPING = {
    model.name: model for model in MODELS.values() 
    if model.mapped_pydantic_class is not None
}

MODELS_WITHOUT_PYDANTIC_MAPPING = {
    model.name: model for model in MODELS.values() 
    if model.mapped_pydantic_class is None
}

# Build inheritance graph
INHERITANCE_GRAPH: Dict[str, List[str]] = {}
for model in MODELS.values():
    INHERITANCE_GRAPH[model.name] = model.inheritance

# Summary statistics
TOTAL_MODELS = len(MODELS)
MODELS_COUNT_BY_MODULE = {module: len(models) for module, models in MODELS_BY_MODULE.items()}
MAPPED_MODELS_COUNT = len(MODELS_WITH_PYDANTIC_MAPPING)
UNMAPPED_MODELS_COUNT = len(MODELS_WITHOUT_PYDANTIC_MAPPING)
OVERALL_MAPPING_COVERAGE = (MAPPED_MODELS_COUNT / TOTAL_MODELS * 100) if TOTAL_MODELS > 0 else 0
'''

    return module_content


def main():
    """Main function to generate the models registry."""
    print("=" * 60)
    print("OFSC API Models Registry Generator")
    print("=" * 60)

    swagger_file = "response_examples/swagger.json"
    if not Path(swagger_file).exists():
        print(f"Error: {swagger_file} not found")
        return 1

    try:
        # Extract models
        models = extract_models_from_swagger(swagger_file)

        # Generate statistics
        by_module = {}
        mapped_count = 0
        for model in models:
            by_module[model.module] = by_module.get(model.module, 0) + 1
            if model.mapped_pydantic_class:
                mapped_count += 1

        print("\nExtraction Summary:")
        print(f"  Total models: {len(models)}")
        print(f"  Models with Pydantic mapping: {mapped_count}")
        print(f"  Models without Pydantic mapping: {len(models) - mapped_count}")
        print(f"  Overall mapping coverage: {mapped_count / len(models) * 100:.1f}%")

        print("\nModels by module:")
        for module, count in sorted(by_module.items()):
            module_models = [m for m in models if m.module == module]
            module_mapped = len([m for m in module_models if m.mapped_pydantic_class])
            coverage = (module_mapped / count * 100) if count > 0 else 0
            print(
                f"  {module}: {count} models ({module_mapped} mapped, {coverage:.1f}% coverage)"
            )

        # Generate the registry module
        print("\nGenerating models registry...")
        module_content = generate_registry_module(models)

        # Ensure tests/fixtures directory exists
        fixtures_dir = Path("tests/fixtures")
        fixtures_dir.mkdir(parents=True, exist_ok=True)

        # Write the module
        registry_file = fixtures_dir / "models_registry.py"
        with open(registry_file, "w") as f:
            f.write(module_content)

        print(f"Generated {registry_file}")
        print(
            f"Registry contains {len(models)} model definitions with comprehensive metadata"
        )

        return 0

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
