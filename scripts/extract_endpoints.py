#!/usr/bin/env python3
"""
Script to extract endpoint information from swagger.json and create the endpoints registry.
"""

import json
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class EndpointParameter:
    """Represents a parameter for an endpoint."""
    name: str
    location: str  # query, path, body, header
    type: str
    required: bool
    description: str = ""
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    minimum: Optional[int] = None
    maximum: Optional[int] = None
    enum: Optional[List[str]] = None


@dataclass
class EndpointInfo:
    """Represents complete endpoint information."""
    id: int
    path: str
    method: str
    module: str
    summary: str
    description: str
    operation_id: str
    tags: List[str]
    required_parameters: List[EndpointParameter]
    optional_parameters: List[EndpointParameter]
    request_body_schema: Optional[str]
    response_schema: str
    implemented_in: str = ""
    signature: str = ""
    rate_limits: Optional[Dict[str, Any]] = None


def parse_parameter(param_data: Dict[str, Any]) -> EndpointParameter:
    """Parse a parameter from swagger JSON."""
    return EndpointParameter(
        name=param_data.get("name", ""),
        location=param_data.get("in", ""),
        type=param_data.get("type", param_data.get("schema", {}).get("type", "unknown")),
        required=param_data.get("required", False),
        description=param_data.get("description", "").replace("<p>", "").replace("</p>", "").strip(),
        min_length=param_data.get("minLength"),
        max_length=param_data.get("maxLength"),
        minimum=param_data.get("minimum"),
        maximum=param_data.get("maximum"),
        enum=param_data.get("enum")
    )


def get_module_from_path(path: str) -> str:
    """Extract module name from path."""
    if "/ofscMetadata/" in path:
        return "metadata"
    elif "/ofscCore/" in path:
        return "core"
    elif "/ofscCapacity/" in path:
        return "capacity"
    elif "/ofscStatistics/" in path:
        return "statistics"
    elif "/ofscPartsCatalog/" in path:
        return "partscatalog"
    elif "/ofscCollaboration/" in path:
        return "collaboration"
    elif "/oauthTokenService/" in path:
        return "auth"
    else:
        return "unknown"


def load_endpoints_mapping() -> Dict[str, int]:
    """Load endpoint mapping from ENDPOINTS.md."""
    endpoints_file = Path("docs/ENDPOINTS.md")
    if not endpoints_file.exists():
        print(f"Warning: {endpoints_file} not found, using sequential IDs")
        return {}
    
    mapping = {}
    with open(endpoints_file, 'r') as f:
        for line in f:
            # Parse table rows like: | 1 | `/rest/ofscMetadata/v1/activityTypeGroups` | GET | metadata | v3.0.0-dev |...
            if re.match(r'^\|\s*\d+\s*\|', line):
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 4:
                    try:
                        endpoint_id = int(parts[1])
                        path = parts[2].strip('`')
                        method = parts[3].upper()
                        key = f"{method} {path}"
                        mapping[key] = endpoint_id
                    except (ValueError, IndexError):
                        continue
    
    print(f"Loaded {len(mapping)} endpoint mappings from ENDPOINTS.md")
    return mapping


def extract_endpoints_from_swagger(swagger_file: str) -> List[EndpointInfo]:
    """Extract all endpoint information from swagger.json."""
    
    with open(swagger_file, 'r') as f:
        swagger = json.load(f)
    
    endpoints = []
    paths = swagger.get("paths", {})
    endpoint_mapping = load_endpoints_mapping()
    
    endpoint_id = 1
    
    for path, methods in paths.items():
        for method_name, method_data in methods.items():
            if method_name.lower() not in ['get', 'post', 'put', 'patch', 'delete']:
                continue
            
            method = method_name.upper()
            key = f"{method} {path}"
            
            # Get ID from mapping or use sequential
            mapped_id = endpoint_mapping.get(key, endpoint_id)
            if key not in endpoint_mapping:
                endpoint_id += 1
            
            # Parse parameters
            required_params = []
            optional_params = []
            request_body_schema = None
            
            for param in method_data.get("parameters", []):
                param_obj = parse_parameter(param)
                
                if param.get("in") == "body":
                    schema_ref = param.get("schema", {}).get("$ref", "")
                    request_body_schema = schema_ref.replace("#/definitions/", "") if schema_ref else None
                elif param_obj.required:
                    required_params.append(param_obj)
                else:
                    optional_params.append(param_obj)
            
            # Get response schema
            responses = method_data.get("responses", {})
            response_schema = ""
            if "200" in responses:
                schema_ref = responses["200"].get("schema", {}).get("$ref", "")
                response_schema = schema_ref.replace("#/definitions/", "") if schema_ref else ""
            
            endpoint = EndpointInfo(
                id=mapped_id,
                path=path,
                method=method,
                module=get_module_from_path(path),
                summary=method_data.get("summary", ""),
                description=method_data.get("description", "").replace("<p>", "").replace("</p>", "").strip(),
                operation_id=method_data.get("operationId", ""),
                tags=method_data.get("tags", []),
                required_parameters=required_params,
                optional_parameters=optional_params,
                request_body_schema=request_body_schema,
                response_schema=response_schema,
                rate_limits=None  # No rate limits found in swagger
            )
            
            endpoints.append(endpoint)
    
    # Sort by ID to match ENDPOINTS.md order
    endpoints.sort(key=lambda x: x.id)
    return endpoints


def generate_registry_module(endpoints: List[EndpointInfo]) -> str:
    """Generate the Python module content."""
    
    module_content = '''"""
OFSC API Endpoints Registry

This module provides a comprehensive registry of all Oracle Field Service Cloud (OFSC) API endpoints
parsed from the swagger.json specification. It includes endpoint metadata, parameters, schemas, and
other relevant information for testing and validation.

Generated automatically from swagger.json - DO NOT EDIT MANUALLY
"""

from typing import Dict, List, Any, Optional, NamedTuple
from dataclasses import dataclass


@dataclass
class EndpointParameter:
    """Represents a parameter for an endpoint."""
    name: str
    location: str  # query, path, body, header
    type: str
    required: bool
    description: str = ""
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    minimum: Optional[int] = None
    maximum: Optional[int] = None
    enum: Optional[List[str]] = None


@dataclass
class EndpointInfo:
    """Represents complete endpoint information."""
    id: int
    path: str
    method: str
    module: str
    summary: str
    description: str
    operation_id: str
    tags: List[str]
    required_parameters: List[EndpointParameter]
    optional_parameters: List[EndpointParameter]
    request_body_schema: Optional[str]
    response_schema: str
    implemented_in: str = ""
    signature: str = ""
    rate_limits: Optional[Dict[str, Any]] = None


# All endpoints from swagger.json
ENDPOINTS: List[EndpointInfo] = [
'''
    
    for endpoint in endpoints:
        # Convert to string representation
        module_content += f"    EndpointInfo(\n"
        module_content += f"        id={endpoint.id},\n"
        module_content += f"        path={repr(endpoint.path)},\n"
        module_content += f"        method={repr(endpoint.method)},\n"
        module_content += f"        module={repr(endpoint.module)},\n"
        module_content += f"        summary={repr(endpoint.summary)},\n"
        module_content += f"        description={repr(endpoint.description)},\n"
        module_content += f"        operation_id={repr(endpoint.operation_id)},\n"
        module_content += f"        tags={repr(endpoint.tags)},\n"
        
        # Parameters
        module_content += f"        required_parameters=[\n"
        for param in endpoint.required_parameters:
            module_content += f"            EndpointParameter(\n"
            module_content += f"                name={repr(param.name)},\n"
            module_content += f"                location={repr(param.location)},\n"
            module_content += f"                type={repr(param.type)},\n"
            module_content += f"                required={param.required},\n"
            module_content += f"                description={repr(param.description)},\n"
            if param.min_length is not None:
                module_content += f"                min_length={param.min_length},\n"
            if param.max_length is not None:
                module_content += f"                max_length={param.max_length},\n"
            if param.minimum is not None:
                module_content += f"                minimum={param.minimum},\n"
            if param.maximum is not None:
                module_content += f"                maximum={param.maximum},\n"
            if param.enum is not None:
                module_content += f"                enum={repr(param.enum)},\n"
            module_content += f"            ),\n"
        module_content += f"        ],\n"
        
        module_content += f"        optional_parameters=[\n"
        for param in endpoint.optional_parameters:
            module_content += f"            EndpointParameter(\n"
            module_content += f"                name={repr(param.name)},\n"
            module_content += f"                location={repr(param.location)},\n"
            module_content += f"                type={repr(param.type)},\n"
            module_content += f"                required={param.required},\n"
            module_content += f"                description={repr(param.description)},\n"
            if param.min_length is not None:
                module_content += f"                min_length={param.min_length},\n"
            if param.max_length is not None:
                module_content += f"                max_length={param.max_length},\n"
            if param.minimum is not None:
                module_content += f"                minimum={param.minimum},\n"
            if param.maximum is not None:
                module_content += f"                maximum={param.maximum},\n"
            if param.enum is not None:
                module_content += f"                enum={repr(param.enum)},\n"
            module_content += f"            ),\n"
        module_content += f"        ],\n"
        
        module_content += f"        request_body_schema={repr(endpoint.request_body_schema)},\n"
        module_content += f"        response_schema={repr(endpoint.response_schema)},\n"
        module_content += f"        implemented_in={repr(endpoint.implemented_in)},\n"
        module_content += f"        signature={repr(endpoint.signature)},\n"
        module_content += f"        rate_limits={repr(endpoint.rate_limits)},\n"
        module_content += f"    ),\n"
    
    module_content += "]\n\n"
    
    # Add utility functions and indexes
    module_content += '''
# Utility functions for endpoint lookup and filtering

def get_endpoint_by_id(endpoint_id: int) -> Optional[EndpointInfo]:
    """Get endpoint by ID."""
    for endpoint in ENDPOINTS:
        if endpoint.id == endpoint_id:
            return endpoint
    return None


def get_endpoints_by_path(path: str) -> List[EndpointInfo]:
    """Get all endpoints for a specific path."""
    return [ep for ep in ENDPOINTS if ep.path == path]


def get_endpoints_by_method(method: str) -> List[EndpointInfo]:
    """Get all endpoints for a specific HTTP method."""
    method = method.upper()
    return [ep for ep in ENDPOINTS if ep.method == method]


def get_endpoints_by_module(module: str) -> List[EndpointInfo]:
    """Get all endpoints for a specific module."""
    return [ep for ep in ENDPOINTS if ep.module == module]


def get_endpoints_by_tag(tag: str) -> List[EndpointInfo]:
    """Get all endpoints with a specific tag."""
    return [ep for ep in ENDPOINTS if tag in ep.tags]


def find_endpoint(method: str, path: str) -> Optional[EndpointInfo]:
    """Find endpoint by method and path."""
    method = method.upper()
    for endpoint in ENDPOINTS:
        if endpoint.method == method and endpoint.path == path:
            return endpoint
    return None


# Indexes by module
ENDPOINTS_BY_MODULE: Dict[str, List[EndpointInfo]] = {}
for endpoint in ENDPOINTS:
    if endpoint.module not in ENDPOINTS_BY_MODULE:
        ENDPOINTS_BY_MODULE[endpoint.module] = []
    ENDPOINTS_BY_MODULE[endpoint.module].append(endpoint)

# Indexes by method
ENDPOINTS_BY_METHOD: Dict[str, List[EndpointInfo]] = {}
for endpoint in ENDPOINTS:
    if endpoint.method not in ENDPOINTS_BY_METHOD:
        ENDPOINTS_BY_METHOD[endpoint.method] = []
    ENDPOINTS_BY_METHOD[endpoint.method].append(endpoint)

# Summary statistics
TOTAL_ENDPOINTS = len(ENDPOINTS)
ENDPOINTS_COUNT_BY_MODULE = {module: len(endpoints) for module, endpoints in ENDPOINTS_BY_MODULE.items()}
ENDPOINTS_COUNT_BY_METHOD = {method: len(endpoints) for method, endpoints in ENDPOINTS_BY_METHOD.items()}
'''
    
    return module_content


def main():
    """Main function to generate the endpoints registry."""
    print("Extracting endpoints from swagger.json...")
    
    endpoints = extract_endpoints_from_swagger("response_examples/swagger.json")
    print(f"Extracted {len(endpoints)} endpoints")
    
    # Generate the module
    module_content = generate_registry_module(endpoints)
    
    # Ensure tests/fixtures directory exists
    fixtures_dir = Path("tests/fixtures")
    fixtures_dir.mkdir(parents=True, exist_ok=True)
    
    # Write the module
    registry_file = fixtures_dir / "endpoints_registry.py"
    with open(registry_file, 'w') as f:
        f.write(module_content)
    
    print(f"Generated {registry_file}")
    print(f"Module contains {len(endpoints)} endpoints across modules:")
    
    # Statistics
    by_module = {}
    for endpoint in endpoints:
        by_module[endpoint.module] = by_module.get(endpoint.module, 0) + 1
    
    for module, count in sorted(by_module.items()):
        print(f"  {module}: {count} endpoints")


if __name__ == "__main__":
    main()