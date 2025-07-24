#!/usr/bin/env python3
"""
Script to extract endpoint information from swagger.json and create the endpoints registry.
"""

import json
import re
import ast
import inspect
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import importlib.util
import sys


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


def scan_client_api_methods() -> Dict[str, Dict[str, Any]]:
    """Scan ofsc.client.*_api modules to find implemented methods and map them to endpoints."""
    
    # First, add the project root to Python path for imports
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    method_mapping = {}
    client_dir = project_root / "ofsc" / "client"
    
    if not client_dir.exists():
        print("Warning: ofsc/client directory not found, skipping method detection")
        return method_mapping
    
    # Find all *_api.py files
    api_files = list(client_dir.glob("*_api.py"))
    print(f"Scanning {len(api_files)} client API files for method implementations...")
    
    for api_file in api_files:
        try:
            # Extract module name from filename (e.g., core_api.py -> core)
            module_name = api_file.stem.replace("_api", "")
            
            # Read and parse the file to extract method information
            with open(api_file, 'r') as f:
                file_content = f.read()
            
            # Parse the AST to find async method definitions
            try:
                tree = ast.parse(file_content)
                methods = extract_methods_from_ast(tree, api_file.name, module_name)
                method_mapping.update(methods)
            except SyntaxError as e:
                print(f"Warning: Could not parse {api_file}: {e}")
                continue
                
        except Exception as e:
            print(f"Warning: Error processing {api_file}: {e}")
            continue
    
    print(f"Found {len(method_mapping)} implemented methods across all API modules")
    return method_mapping


def extract_methods_from_ast(tree: ast.AST, filename: str, module_name: str) -> Dict[str, Dict[str, Any]]:
    """Extract method information from an AST tree."""
    methods = {}
    
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef):
            # Skip private methods and special methods
            if node.name.startswith('_'):
                continue
            
            # Extract method information
            method_info = {
                'method_name': node.name,
                'module': module_name,
                'filename': filename,
                'class_name': None,
                'endpoints': [],
                'docstring': ast.get_docstring(node),
                'line_number': node.lineno
            }
            
            # Find the class this method belongs to
            for parent in ast.walk(tree):
                if isinstance(parent, ast.ClassDef):
                    for child in ast.walk(parent):
                        if child is node:
                            method_info['class_name'] = parent.name
                            break
            
            # Extract endpoint URLs from the method body
            endpoints = extract_endpoints_from_method(node)
            method_info['endpoints'] = endpoints
            
            # Create a key that includes both method name and endpoints
            for endpoint in endpoints:
                method_key = f"{method_info['class_name']}.{node.name}" if method_info['class_name'] else node.name
                methods[endpoint] = method_info.copy()
                methods[endpoint]['endpoint_url'] = endpoint
    
    return methods


def extract_endpoints_from_method(method_node: ast.AsyncFunctionDef) -> List[str]:
    """Extract endpoint URLs from method body by looking for string assignments."""
    endpoints = []
    
    for node in ast.walk(method_node):
        if isinstance(node, ast.Assign):
            # Look for assignments like: endpoint = "/rest/ofscCore/v1/users"
            for target in node.targets:
                if (isinstance(target, ast.Name) and target.id == 'endpoint'):
                    # Handle both ast.Str (older Python) and ast.Constant (Python 3.8+)
                    if hasattr(node.value, 's'):  # ast.Str
                        endpoints.append(node.value.s)
                    elif (isinstance(node.value, ast.Constant) and 
                          isinstance(node.value.value, str)):
                        endpoints.append(node.value.value)
    
    return endpoints


def find_method_for_endpoint(method_mapping: Dict[str, Dict[str, Any]], 
                           endpoint_method: str, endpoint_path: str) -> Optional[str]:
    """Find the implementation method for a given endpoint."""
    
    # Normalize the endpoint path for comparison
    normalized_path = endpoint_path
    
    # Try exact match first
    if normalized_path in method_mapping:
        method_info = method_mapping[normalized_path]
        class_name = method_info['class_name']
        method_name = method_info['method_name']
        filename = method_info['filename']
        
        return f"{filename}:{class_name}.{method_name}()"
    
    # Try partial matches (for parameterized endpoints)
    for endpoint_url, method_info in method_mapping.items():
        # Replace path parameters with wildcards for matching
        pattern_path = re.sub(r'\{[^}]+\}', r'[^/]+', re.escape(endpoint_url))
        if re.match(f"^{pattern_path}$", normalized_path):
            class_name = method_info['class_name']
            method_name = method_info['method_name']
            filename = method_info['filename']
            
            return f"{filename}:{class_name}.{method_name}()"
    
    return None


def generate_method_signature(method_mapping: Dict[str, Dict[str, Any]], 
                            endpoint_method: str, endpoint_path: str) -> str:
    """Generate a method signature for the endpoint if implemented."""
    
    # Find the method implementation
    normalized_path = endpoint_path
    method_info = None
    
    # Try exact match first
    if normalized_path in method_mapping:
        method_info = method_mapping[normalized_path]
    else:
        # Try partial matches
        for endpoint_url, info in method_mapping.items():
            pattern_path = re.sub(r'\{[^}]+\}', r'[^/]+', re.escape(endpoint_url))
            if re.match(f"^{pattern_path}$", normalized_path):
                method_info = info
                break
    
    if not method_info:
        return ""
    
    # Create a simple signature based on the method name
    method_name = method_info['method_name']
    
    # Extract parameter names from path
    path_params = re.findall(r'\{([^}]+)\}', endpoint_path)
    
    # Basic signature generation
    params = []
    if path_params:
        params.extend([f"{param}: str" for param in path_params])
    
    # Add common parameters based on method type
    if endpoint_method.upper() == 'GET':
        if 'offset' not in str(path_params) and 'get_' in method_name and any(word in method_name for word in ['list', 's', 'activities', 'users', 'resources']):
            params.extend(["offset: int = 0", "limit: int = 100"])
    elif endpoint_method.upper() in ['POST', 'PUT', 'PATCH']:
        if 'data' not in str(path_params):
            params.append("data: dict")
    
    signature = f"async def {method_name}({', '.join(['self'] + params)}) -> ResponseModel"
    return signature


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
    
    # Scan client API methods to find implementations
    print("Scanning client API methods for implementation mapping...")
    method_mapping = scan_client_api_methods()
    
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
            
            # Find method implementation
            implemented_in = find_method_for_endpoint(method_mapping, method, path)
            signature = generate_method_signature(method_mapping, method, path)
            
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
                implemented_in=implemented_in or "",
                signature=signature,
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
    implemented_count = 0
    for endpoint in endpoints:
        by_module[endpoint.module] = by_module.get(endpoint.module, 0) + 1
        if endpoint.implemented_in:
            implemented_count += 1
    
    for module, count in sorted(by_module.items()):
        module_implemented = sum(1 for ep in endpoints if ep.module == module and ep.implemented_in)
        print(f"  {module}: {count} endpoints ({module_implemented} implemented, {module_implemented/count*100:.1f}%)")
    
    print(f"\nImplementation Summary:")
    print(f"  Total endpoints: {len(endpoints)}")
    print(f"  Implemented endpoints: {implemented_count}")
    print(f"  Implementation coverage: {implemented_count/len(endpoints)*100:.1f}%")


if __name__ == "__main__":
    main()