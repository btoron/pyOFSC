#!/usr/bin/env python3
"""
Endpoint Model Mapping Analyzer

This script analyzes a specific endpoint by ID and provides comprehensive information
about its response model mapping, including schema details, Pydantic mappings,
and model structure analysis.

Usage:
    python scripts/analyze_endpoint_model.py <endpoint_id>
    python scripts/analyze_endpoint_model.py --list-endpoints
    python scripts/analyze_endpoint_model.py --help

Examples:
    python scripts/analyze_endpoint_model.py 1
    python scripts/analyze_endpoint_model.py 25
    python scripts/analyze_endpoint_model.py --list-endpoints | head -10
"""

import argparse
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

# Add the project root to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.fixtures.endpoints_registry import ENDPOINTS, get_endpoint_by_id, EndpointInfo
from tests.fixtures.models_registry import (
    MODELS, get_model_by_name, get_models_for_endpoint, 
    get_model_inheritance_chain, ModelInfo, ModelProperty
)


def format_property_info(prop: ModelProperty, indent: str = "    ") -> str:
    """Format a model property for display."""
    type_info = prop.type
    if prop.ref:
        type_info = f"ref:{prop.ref}"
    elif prop.items and prop.type == "array":
        if prop.items.get('$ref'):
            type_info = f"array[ref:{prop.items['$ref']}]"
        else:
            type_info = f"array[{prop.items.get('type', 'unknown')}]"
    
    required_marker = " *" if prop.required else ""
    
    lines = [f"{indent}{prop.name}: {type_info}{required_marker}"]
    
    if prop.description:
        lines.append(f"{indent}  Description: {prop.description}")
    
    # Add constraints if present
    constraints = []
    if prop.min_length is not None:
        constraints.append(f"minLength: {prop.min_length}")
    if prop.max_length is not None:
        constraints.append(f"maxLength: {prop.max_length}")
    if prop.minimum is not None:
        constraints.append(f"min: {prop.minimum}")
    if prop.maximum is not None:
        constraints.append(f"max: {prop.maximum}")
    if prop.enum:
        constraints.append(f"enum: {prop.enum}")
    if prop.format:
        constraints.append(f"format: {prop.format}")
    
    if constraints:
        lines.append(f"{indent}  Constraints: {', '.join(constraints)}")
    
    return "\n".join(lines)


def analyze_model_structure(model: ModelInfo, max_depth: int = 2, current_depth: int = 0) -> str:
    """Recursively analyze model structure with nested references."""
    if current_depth >= max_depth:
        return f"{'  ' * current_depth}[Max depth reached]"
    
    lines = []
    indent = "  " * current_depth
    
    # Model header
    mapped_info = f" -> {model.mapped_pydantic_class}" if model.mapped_pydantic_class else " (no Pydantic mapping)"
    lines.append(f"{indent}{model.name}{mapped_info}")
    
    if model.description and current_depth == 0:
        lines.append(f"{indent}Description: {model.description}")
    
    # Properties
    if model.properties:
        lines.append(f"{indent}Properties ({len(model.properties)}):")
        for prop in model.properties:
            lines.append(format_property_info(prop, indent + "  "))
            
            # Show nested model structure for references
            if prop.ref and current_depth < max_depth - 1:
                nested_model = get_model_by_name(prop.ref)
                if nested_model:
                    lines.append(f"{indent}    ↳ {prop.ref}:")
                    nested_structure = analyze_model_structure(nested_model, max_depth, current_depth + 2)
                    lines.append(nested_structure)
    else:
        lines.append(f"{indent}No properties defined")
    
    # Inheritance
    if model.inheritance and current_depth == 0:
        lines.append(f"{indent}Inherits from: {', '.join(model.inheritance)}")
        chain = get_model_inheritance_chain(model.name)
        if len(chain) > 1:
            lines.append(f"{indent}Full inheritance chain: {' -> '.join(chain)}")
    
    return "\n".join(lines)


def analyze_endpoint_model_mapping(endpoint_id: int) -> bool:
    """Analyze endpoint model mapping and display comprehensive information."""
    
    # Get endpoint information
    endpoint = get_endpoint_by_id(endpoint_id)
    if not endpoint:
        print(f"❌ Error: Endpoint with ID {endpoint_id} not found")
        return False
    
    print("=" * 80)
    print(f"🔍 ENDPOINT MODEL MAPPING ANALYSIS - ID: {endpoint_id}")
    print("=" * 80)
    
    # Endpoint details
    print(f"📍 Endpoint Information:")
    print(f"   Path: {endpoint.path}")
    print(f"   Method: {endpoint.method}")
    print(f"   Module: {endpoint.module}")
    print(f"   Operation ID: {endpoint.operation_id}")
    
    if endpoint.summary:
        print(f"   Summary: {endpoint.summary}")
    
    if endpoint.description:
        print(f"   Description: {endpoint.description}")
    
    # Implementation information
    print(f"\n💻 Implementation Status:")
    if endpoint.implemented_in:
        print(f"   ✅ Implemented in: {endpoint.implemented_in}")
        if endpoint.signature:
            print(f"   📝 Signature: {endpoint.signature}")
    else:
        print(f"   ❌ Not implemented yet")
        print(f"   💡 Needs implementation in: ofsc/client/{endpoint.module}_api.py")
    
    # Response schema analysis
    print(f"\n📋 Response Schema Analysis:")
    if not endpoint.response_schema:
        print("   ❌ No response schema defined for this endpoint")
        return False
    
    print(f"   Response Schema: {endpoint.response_schema}")
    
    # Find the corresponding model
    response_model = get_model_by_name(endpoint.response_schema)
    if not response_model:
        print(f"   ❌ Model '{endpoint.response_schema}' not found in models registry")
        return False
    
    # Pydantic mapping status
    print(f"\n🔗 Pydantic Mapping Status:")
    if response_model.mapped_pydantic_class:
        print(f"   ✅ Mapped to Pydantic class: {response_model.mapped_pydantic_class}")
        print(f"   📦 Model module: {response_model.module}")
    else:
        print(f"   ❌ No Pydantic mapping found")
        print(f"   💡 Suggestion: Implement Pydantic model for '{endpoint.response_schema}'")
        print(f"   📦 Target module: {response_model.module}")
    
    # Model structure analysis
    print(f"\n🏗️  Model Structure Analysis:")
    structure = analyze_model_structure(response_model, max_depth=3)
    print(structure)
    
    # Usage analysis
    print(f"\n📊 Usage Analysis:")
    print(f"   Used in endpoints: {len(response_model.used_in_endpoints)}")
    if len(response_model.used_in_endpoints) > 1:
        print(f"   Other endpoints using this model:")
        for ep in response_model.used_in_endpoints:
            if ep != f"{endpoint.method} {endpoint.path}":
                print(f"     • {ep}")
    
    # Related models analysis
    print(f"\n🔍 Related Models:")
    if response_model.nested_models:
        print(f"   References {len(response_model.nested_models)} other models:")
        for nested_name in response_model.nested_models:
            nested_model = get_model_by_name(nested_name)
            if nested_model:
                mapped_status = "✅" if nested_model.mapped_pydantic_class else "❌"
                pydantic_info = f" -> {nested_model.mapped_pydantic_class}" if nested_model.mapped_pydantic_class else ""
                print(f"     {mapped_status} {nested_name}{pydantic_info}")
    else:
        print("   No nested model references")
    
    if response_model.parent_models:
        print(f"   Referenced by {len(response_model.parent_models)} other models:")
        for parent_name in response_model.parent_models[:5]:  # Show first 5
            parent_model = get_model_by_name(parent_name)
            if parent_model:
                mapped_status = "✅" if parent_model.mapped_pydantic_class else "❌"
                print(f"     {mapped_status} {parent_name}")
        if len(response_model.parent_models) > 5:
            print(f"     ... and {len(response_model.parent_models) - 5} more")
    
    # Implementation suggestions
    print(f"\n💡 Implementation Suggestions:")
    
    implementation_step = 1
    
    # Implementation suggestions
    if not endpoint.implemented_in:
        print(f"   {implementation_step}. Implement API method")
        print(f"      Location: ofsc/client/{endpoint.module}_api.py")
        print(f"      Method: Add method for {endpoint.method} {endpoint.path}")
        implementation_step += 1
    
    if not response_model.mapped_pydantic_class:
        print(f"   {implementation_step}. Create Pydantic model for '{endpoint.response_schema}'")
        print(f"      Location: ofsc/models/{response_model.module}.py")
        print(f"      Properties: {len(response_model.properties)} fields to implement")
        
        if response_model.inheritance:
            print(f"      Inheritance: Consider extending {', '.join(response_model.inheritance)}")
        implementation_step += 1
    
    unmapped_nested = [name for name in response_model.nested_models 
                      if get_model_by_name(name) and not get_model_by_name(name).mapped_pydantic_class]
    
    if unmapped_nested:
        print(f"   {implementation_step}. Implement nested models:")
        for nested_name in unmapped_nested[:3]:  # Show first 3
            nested_model = get_model_by_name(nested_name)
            print(f"      • {nested_name} (module: {nested_model.module})")
        if len(unmapped_nested) > 3:
            print(f"      • ... and {len(unmapped_nested) - 3} more")
        implementation_step += 1
    
    if response_model.mapped_pydantic_class and endpoint.implemented_in:
        print(f"   {implementation_step}. Validate existing implementation with tests")
        print(f"      Run: pytest tests/models/test_endpoints_{response_model.module}.py -v")
    elif response_model.mapped_pydantic_class or endpoint.implemented_in:
        print(f"   {implementation_step}. Complete the implementation chain")
        if not endpoint.implemented_in:
            print(f"      Missing: API method implementation")
        if not response_model.mapped_pydantic_class:
            print(f"      Missing: Pydantic model mapping")
    
    return True


def list_endpoints_summary():
    """List all endpoints with their response schemas and mapping status."""
    print("📋 All Endpoints Summary:")
    print("=" * 110)
    print(f"{'ID':<4} {'Method':<7} {'Module':<12} {'Response Schema':<25} {'Pydantic':<15} {'Impl':<6} {'Path'}")
    print("-" * 110)
    
    for endpoint in ENDPOINTS:
        # Get model mapping status
        pydantic_status = "❌ None"
        if endpoint.response_schema:
            model = get_model_by_name(endpoint.response_schema)
            if model and model.mapped_pydantic_class:
                pydantic_status = f"✅ {model.mapped_pydantic_class[:12]}"
        
        # Get implementation status
        impl_status = "✅ Yes" if endpoint.implemented_in else "❌ No"
        
        # Truncate long paths
        path = endpoint.path
        if len(path) > 45:
            path = path[:42] + "..."
        
        schema_name = endpoint.response_schema or "None"
        if len(schema_name) > 23:
            schema_name = schema_name[:20] + "..."
        
        print(f"{endpoint.id:<4} {endpoint.method:<7} {endpoint.module:<12} {schema_name:<25} {pydantic_status:<15} {impl_status:<6} {path}")


def main():
    """Main function to handle command line arguments and run analysis."""
    parser = argparse.ArgumentParser(
        description="Analyze endpoint model mapping by endpoint ID",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s 1                    # Analyze endpoint ID 1
  %(prog)s 25                   # Analyze endpoint ID 25
  %(prog)s --list-endpoints     # List all endpoints with mapping status
  %(prog)s --list-endpoints | grep "❌"  # Show only unmapped endpoints
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        'endpoint_id', 
        nargs='?', 
        type=int, 
        help='ID of the endpoint to analyze'
    )
    group.add_argument(
        '--list-endpoints', 
        action='store_true',
        help='List all endpoints with their mapping status'
    )
    
    args = parser.parse_args()
    
    try:
        if args.list_endpoints:
            list_endpoints_summary()
            return 0
        
        if args.endpoint_id is not None:
            success = analyze_endpoint_model_mapping(args.endpoint_id)
            return 0 if success else 1
        
        parser.print_help()
        return 1
        
    except KeyboardInterrupt:
        print("\n❌ Analysis interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())