#!/usr/bin/env python3
"""
Script to extract endpoint information from swagger.json and create the endpoints registry.
"""

import json
import re
import ast
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
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
        type=param_data.get(
            "type", param_data.get("schema", {}).get("type", "unknown")
        ),
        required=param_data.get("required", False),
        description=param_data.get("description", "")
        .replace("<p>", "")
        .replace("</p>", "")
        .strip(),
        min_length=param_data.get("minLength"),
        max_length=param_data.get("maxLength"),
        minimum=param_data.get("minimum"),
        maximum=param_data.get("maximum"),
        enum=param_data.get("enum"),
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
            with open(api_file, "r") as f:
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


def extract_methods_from_ast(
    tree: ast.AST, filename: str, module_name: str
) -> Dict[str, Dict[str, Any]]:
    """Extract method information from an AST tree."""
    methods = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef):
            # Skip private methods and special methods
            if node.name.startswith("_"):
                continue

            # Extract method information
            method_info = {
                "method_name": node.name,
                "module": module_name,
                "filename": filename,
                "class_name": None,
                "endpoints": [],
                "docstring": ast.get_docstring(node),
                "line_number": node.lineno,
                "parameters": _extract_method_parameters(node),
                "return_annotation": _extract_return_annotation(node),
            }

            # Find the class this method belongs to
            for parent in ast.walk(tree):
                if isinstance(parent, ast.ClassDef):
                    for child in ast.walk(parent):
                        if child is node:
                            method_info["class_name"] = parent.name
                            break

            # Extract endpoint URLs from the method body
            endpoints = extract_endpoints_from_method(node)
            method_info["endpoints"] = endpoints

            # Store methods with endpoints - allow multiple methods per endpoint
            for endpoint in endpoints:
                if endpoint not in methods:
                    methods[endpoint] = []
                method_info_copy = method_info.copy()
                method_info_copy["endpoint_url"] = endpoint
                methods[endpoint].append(method_info_copy)

    return methods


def _extract_method_parameters(
    method_node: ast.AsyncFunctionDef,
) -> List[Dict[str, Any]]:
    """Extract parameter information from method AST node."""
    parameters = []

    args = method_node.args

    # Skip 'self' parameter
    arg_names = [arg.arg for arg in args.args[1:]] if args.args else []

    # Get default values
    defaults = args.defaults if args.defaults else []
    default_offset = len(arg_names) - len(defaults)

    for i, arg_name in enumerate(arg_names):
        param_info = {
            "name": arg_name,
            "annotation": None,
            "default": None,
            "is_optional": False,
        }

        # Extract type annotation
        if i < len(args.args[1:]):  # Skip self
            arg_node = args.args[i + 1]  # +1 to skip self
            if arg_node.annotation:
                param_info["annotation"] = _ast_to_string(arg_node.annotation)

        # Extract default value
        if i >= default_offset:
            default_index = i - default_offset
            if default_index < len(defaults):
                default_node = defaults[default_index]
                param_info["default"] = _ast_to_signature_string(default_node)
                param_info["is_optional"] = True

        parameters.append(param_info)

    # Handle *args parameter
    if args.vararg:
        parameters.append(
            {
                "name": f"*{args.vararg.arg}",
                "annotation": _ast_to_string(args.vararg.annotation)
                if args.vararg.annotation
                else None,
                "default": None,
                "is_optional": False,
            }
        )

    # Handle **kwargs parameter
    if args.kwarg:
        parameters.append(
            {
                "name": f"**{args.kwarg.arg}",
                "annotation": _ast_to_string(args.kwarg.annotation)
                if args.kwarg.annotation
                else None,
                "default": None,
                "is_optional": False,
            }
        )

    return parameters


def _extract_return_annotation(method_node: ast.AsyncFunctionDef) -> Optional[str]:
    """Extract return type annotation from method AST node."""
    if method_node.returns:
        return _ast_to_string(method_node.returns)
    return None


def _ast_to_signature_string(node: ast.AST) -> str:
    """Convert AST node to string representation for method signatures (with proper quoting)."""
    try:
        import astor

        return astor.to_source(node).strip()
    except ImportError:
        # Fallback to basic representation with proper quoting for signatures
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Constant):
            if isinstance(node.value, str):
                return f'"{node.value}"'  # Include quotes for string defaults in signatures
            return repr(node.value)
        elif hasattr(node, "s"):  # ast.Str (deprecated but still used)
            return f'"{node.s}"'  # Include quotes for string defaults in signatures
        elif isinstance(node, ast.Attribute):
            # Special case: Handle ExportMediaType.OCTET_STREAM.value -> "application/octet-stream"
            if (
                isinstance(node.value, ast.Attribute)
                and isinstance(node.value.value, ast.Name)
                and node.value.value.id == "ExportMediaType"
                and node.value.attr == "OCTET_STREAM"
                and node.attr == "value"
            ):
                return '"application/octet-stream"'

            value_str = (
                _ast_to_signature_string(node.value) if hasattr(node, "value") else ""
            )
            return f"{value_str}.{node.attr}"
        elif isinstance(node, ast.Subscript):
            value_str = _ast_to_signature_string(node.value)
            slice_str = _ast_to_signature_string(node.slice)
            return f"{value_str}[{slice_str}]"
        elif isinstance(node, ast.List):
            # Handle list literals like ["label"]
            elements = []
            for elt in node.elts:
                elements.append(_ast_to_signature_string(elt))
            return f"[{', '.join(elements)}]"
        else:
            return str(type(node).__name__)


def _ast_to_string(node: ast.AST) -> str:
    """Convert AST node to string representation."""
    try:
        import astor

        return astor.to_source(node).strip()
    except ImportError:
        # Fallback to basic representation
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Constant):
            # For string constants in URL contexts, return the raw value
            if isinstance(node.value, str):
                return node.value  # Return raw string without extra quotes
            return repr(node.value)
        elif hasattr(node, "s"):  # ast.Str (deprecated but still used)
            return node.s  # Return raw string without extra quotes
        elif isinstance(node, ast.Attribute):
            value_str = _ast_to_string(node.value) if hasattr(node, "value") else ""
            return f"{value_str}.{node.attr}"
        elif isinstance(node, ast.Subscript):
            value_str = _ast_to_string(node.value)
            slice_str = _ast_to_string(node.slice)
            return f"{value_str}[{slice_str}]"
        elif isinstance(node, ast.List):
            # Handle list literals like ["label"]
            elements = []
            for elt in node.elts:
                elements.append(_ast_to_string(elt))
            return f"[{', '.join(elements)}]"
        else:
            return str(type(node).__name__)


def extract_endpoints_from_method(method_node: ast.AsyncFunctionDef) -> List[str]:
    """Extract endpoint URLs from method body using multiple detection strategies."""
    endpoints = []

    for node in ast.walk(method_node):
        if isinstance(node, ast.Assign):
            # Look for assignments like: endpoint = "/rest/ofscCore/v1/users"
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "endpoint":
                    endpoint_url = _extract_endpoint_from_assignment(node.value)
                    if endpoint_url:
                        endpoints.append(endpoint_url)
        elif isinstance(node, ast.Call):
            # Look for self.client.request(url="...") calls
            endpoint_url = _extract_endpoint_from_client_request(node)
            if endpoint_url and endpoint_url not in endpoints:
                endpoints.append(endpoint_url)

    # If no endpoints found with assignment, try method name inference
    if not endpoints:
        inferred_endpoint = _infer_endpoint_from_method_name(method_node.name)
        if inferred_endpoint:
            endpoints.append(inferred_endpoint)

    # Also check docstring for endpoint information
    docstring_endpoint = _extract_endpoint_from_docstring(method_node)
    if docstring_endpoint and docstring_endpoint not in endpoints:
        endpoints.append(docstring_endpoint)

    return endpoints


def _extract_endpoint_from_client_request(call_node: ast.Call) -> Optional[str]:
    """Extract endpoint URL from self.client.request(url="...") calls."""
    # Check if this is a call to self.client.request
    if (
        isinstance(call_node.func, ast.Attribute)
        and isinstance(call_node.func.value, ast.Attribute)
        and isinstance(call_node.func.value.value, ast.Name)
        and call_node.func.value.value.id == "self"
        and call_node.func.value.attr == "client"
        and call_node.func.attr == "request"
    ):
        # Look for url keyword argument
        for keyword in call_node.keywords:
            if keyword.arg == "url":
                return _ast_to_string(keyword.value)

    return None


def _extract_endpoint_from_assignment(value_node: ast.AST) -> Optional[str]:
    """Extract endpoint URL from various assignment value types."""

    # Handle direct string literals
    if isinstance(value_node, ast.Constant) and isinstance(value_node.value, str):
        return value_node.value
    elif hasattr(value_node, "s"):  # ast.Str (deprecated)
        return value_node.s

    # Handle f-strings like f"/rest/ofscMetadata/v1/activityTypes/{label}"
    elif isinstance(value_node, ast.JoinedStr):
        return _reconstruct_fstring_endpoint(value_node)

    # Handle format calls like "/rest/ofscCore/v1/users/{}".format(user_id)
    elif isinstance(value_node, ast.Call):
        if (
            isinstance(value_node.func, ast.Attribute)
            and value_node.func.attr == "format"
        ):
            base_str = _extract_string_from_node(value_node.func.value)
            if base_str:
                return _convert_format_to_template(base_str)

    return None


def _reconstruct_fstring_endpoint(fstring_node: ast.JoinedStr) -> Optional[str]:
    """Reconstruct endpoint URL from f-string, replacing variables with {param} placeholders."""
    parts = []

    for value in fstring_node.values:
        if isinstance(value, ast.Constant):
            # String literal part
            parts.append(value.value)
        elif isinstance(value, ast.FormattedValue):
            # Variable part - convert to template placeholder
            if isinstance(value.value, ast.Name):
                var_name = value.value.id

                # Normalize parameter names to match swagger spec
                normalized_name = var_name

                # Remove 'encoded_' prefix if present
                if var_name.startswith("encoded_"):
                    normalized_name = var_name[8:]  # len('encoded_') = 8

                # Convert snake_case to camelCase for common parameters
                snake_to_camel_map = {
                    "activity_id": "activityId",
                    "resource_id": "resourceId",
                    "user_id": "userId",
                    "inventory_id": "inventoryId",
                    "property_label": "propertyLabel",
                    "api_label": "apiLabel",
                    "profile_label": "profileLabel",
                    "plan_label": "planLabel",
                    "area_label": "areaLabel",
                    "linked_activity_id": "linkedActivityId",
                    "link_type": "linkType",
                    "schedule_item_id": "scheduleItemId",
                    "location_id": "locationId",
                    "request_id": "requestId",
                    "extract_date": "dailyExtractDate",
                    "daily_extract_date": "dailyExtractDate",
                    "filename": "dailyExtractFilename",
                    "daily_extract_filename": "dailyExtractFilename",
                }

                # Apply snake_case to camelCase conversion if needed
                if normalized_name in snake_to_camel_map:
                    normalized_name = snake_to_camel_map[normalized_name]

                # Special case: Handle routing profile endpoints where label -> profileLabel
                current_endpoint = "".join(parts)
                if normalized_name == "label" and "routingProfiles" in current_endpoint:
                    normalized_name = "profileLabel"

                # Add the parameter placeholder
                parts.append(f"{{{normalized_name}}}")

    return "".join(parts) if parts else None


def _extract_string_from_node(node: ast.AST) -> Optional[str]:
    """Extract string value from AST node."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    elif hasattr(node, "s"):  # ast.Str (deprecated but still used)
        return node.s
    return None


def _convert_format_to_template(format_string: str) -> str:
    """Convert format string with {} to template with {param}."""
    # Simple conversion - replace {} with {param}
    # This is a basic implementation, could be enhanced
    import re

    return re.sub(r"\{\}", "{param}", format_string)


def _infer_endpoint_from_method_name(method_name: str) -> Optional[str]:
    """Infer endpoint URL from method name using common patterns."""

    # Comprehensive patterns for all API modules
    endpoint_patterns = {
        # Metadata API - Activity Types
        "get_activity_types": "/rest/ofscMetadata/v1/activityTypes",
        "get_activity_type": "/rest/ofscMetadata/v1/activityTypes/{label}",
        "get_activity_type_groups": "/rest/ofscMetadata/v1/activityTypeGroups",
        "get_activity_type_group": "/rest/ofscMetadata/v1/activityTypeGroups/{label}",
        "create_or_replace_activity_type_group": "/rest/ofscMetadata/v1/activityTypeGroups/{label}",
        # Metadata API - Applications
        "get_applications": "/rest/ofscMetadata/v1/applications",
        "get_application": "/rest/ofscMetadata/v1/applications/{label}",
        "get_application_api_accesses": "/rest/ofscMetadata/v1/applications/{label}/apiAccess",
        "get_application_api_access": "/rest/ofscMetadata/v1/applications/{label}/apiAccess/{apiLabel}",
        # Metadata API - Capacity
        "get_capacity_areas": "/rest/ofscMetadata/v1/capacityAreas",
        "get_capacity_area": "/rest/ofscMetadata/v1/capacityAreas/{label}",
        "get_capacity_categories": "/rest/ofscMetadata/v1/capacityCategories",
        "get_capacity_category": "/rest/ofscMetadata/v1/capacityCategories/{label}",
        "create_or_replace_capacity_category": "/rest/ofscMetadata/v1/capacityCategories/{label}",
        "delete_capacity_category": "/rest/ofscMetadata/v1/capacityCategories/{label}",
        "get_capacity_area_categories": "/rest/ofscMetadata/v1/capacityAreas/{label}/capacityCategories",
        "get_capacity_area_workzones": "/rest/ofscMetadata/v2/capacityAreas/{label}/workZones",
        "get_capacity_area_timeslots": "/rest/ofscMetadata/v1/capacityAreas/{label}/timeSlots",
        "get_capacity_area_timeintervals": "/rest/ofscMetadata/v1/capacityAreas/{label}/timeIntervals",
        "get_capacity_area_organizations": "/rest/ofscMetadata/v1/capacityAreas/{label}/organizations",
        # Metadata API - Properties
        "get_properties": "/rest/ofscMetadata/v1/properties",
        "get_property": "/rest/ofscMetadata/v1/properties/{label}",
        "create_or_replace_property": "/rest/ofscMetadata/v1/properties/{label}",
        "get_enumeration_values": "/rest/ofscMetadata/v1/properties/{label}/enumerationList",
        # Metadata API - Work Skills
        "get_workskills": "/rest/ofscMetadata/v1/workSkills",
        "get_workskill": "/rest/ofscMetadata/v1/workSkills/{label}",
        "get_workskill_groups": "/rest/ofscMetadata/v1/workSkillGroups",
        "get_workskill_group": "/rest/ofscMetadata/v1/workSkillGroups/{label}",
        "get_workskill_conditions": "/rest/ofscMetadata/v1/workSkillConditions",
        # Metadata API - Organizations & Others
        "get_organizations": "/rest/ofscMetadata/v1/organizations",
        "get_organization": "/rest/ofscMetadata/v1/organizations/{label}",
        "get_inventory_types": "/rest/ofscMetadata/v1/inventoryTypes",
        "get_inventory_type": "/rest/ofscMetadata/v1/inventoryTypes/{label}",
        "get_forms": "/rest/ofscMetadata/v1/forms",
        "get_form": "/rest/ofscMetadata/v1/forms/{label}",
        "get_languages": "/rest/ofscMetadata/v1/languages",
        "get_link_templates": "/rest/ofscMetadata/v1/linkTemplates",
        "get_link_template": "/rest/ofscMetadata/v1/linkTemplates/{label}",
        "get_non_working_reasons": "/rest/ofscMetadata/v1/nonWorkingReasons",
        "get_resource_types": "/rest/ofscMetadata/v1/resourceTypes",
        "get_routing_profiles": "/rest/ofscMetadata/v1/routingProfiles",
        "get_routing_profile_plans": "/rest/ofscMetadata/v1/routingProfiles/{profileLabel}/plans",
        "get_routing_profile_plan_export": "/rest/ofscMetadata/v1/routingProfiles/{profileLabel}/plans/{planLabel}/custom-actions/export",
        "get_shifts": "/rest/ofscMetadata/v1/shifts",
        "get_shift": "/rest/ofscMetadata/v1/shifts/{label}",
        "get_timeslots": "/rest/ofscMetadata/v1/timeSlots",
        "get_workzones": "/rest/ofscMetadata/v1/workZones",
        "get_workzone": "/rest/ofscMetadata/v1/workZones/{label}",
        "get_work_zone_key": "/rest/ofscMetadata/v1/workZoneKey",
        # Core API - Activities
        "create_activity": "/rest/ofscCore/v1/activities",
        "get_activities": "/rest/ofscCore/v1/activities",
        "get_activity": "/rest/ofscCore/v1/activities/{activityId}",
        "update_activity": "/rest/ofscCore/v1/activities/{activityId}",
        "delete_activity": "/rest/ofscCore/v1/activities/{activityId}",
        "search_activities": "/rest/ofscCore/v1/activities/custom-actions/search",
        "bulk_update_activities": "/rest/ofscCore/v1/activities/custom-actions/bulkUpdate",
        # Core API - Users & Resources
        "get_users": "/rest/ofscCore/v1/users",
        "get_user": "/rest/ofscCore/v1/users/{userId}",
        "create_user": "/rest/ofscCore/v1/users",
        "update_user": "/rest/ofscCore/v1/users/{userId}",
        "delete_user": "/rest/ofscCore/v1/users/{userId}",
        "get_resources": "/rest/ofscCore/v1/resources",
        "get_resource": "/rest/ofscCore/v1/resources/{resourceId}",
        "create_resource": "/rest/ofscCore/v1/resources",
        "update_resource": "/rest/ofscCore/v1/resources/{resourceId}",
        "delete_resource": "/rest/ofscCore/v1/resources/{resourceId}",
    }

    # Try direct match first
    if method_name in endpoint_patterns:
        return endpoint_patterns[method_name]

    # Try pattern-based inference for common CRUD operations
    return _infer_crud_endpoint(method_name)


def _infer_crud_endpoint(method_name: str) -> Optional[str]:
    """Infer endpoint from method name using CRUD patterns."""
    import re

    # Common CRUD patterns
    patterns = [
        # GET operations
        (r"^get_([a-z_]+)s$", r"/rest/ofscMetadata/v1/\1s"),  # get_users -> /users
        (
            r"^get_([a-z_]+)$",
            r"/rest/ofscMetadata/v1/\1s/{label}",
        ),  # get_user -> /users/{label}
        # CREATE operations
        (r"^create_([a-z_]+)$", r"/rest/ofscCore/v1/\1s"),  # create_user -> /users
        (
            r"^create_or_replace_([a-z_]+)$",
            r"/rest/ofscMetadata/v1/\1s/{label}",
        ),  # create_or_replace_user -> /users/{label}
        # UPDATE operations
        (
            r"^update_([a-z_]+)$",
            r"/rest/ofscCore/v1/\1s/{id}",
        ),  # update_user -> /users/{id}
        # DELETE operations
        (
            r"^delete_([a-z_]+)$",
            r"/rest/ofscCore/v1/\1s/{id}",
        ),  # delete_user -> /users/{id}
    ]

    for pattern, replacement in patterns:
        match = re.match(pattern, method_name)
        if match:
            # Convert underscore to camelCase for some resources
            resource = match.group(1)
            if resource == "activity_type":
                resource = "activityType"
            elif resource == "work_skill":
                resource = "workSkill"

            return re.sub(r"\\1", resource, replacement)

    return None


def _extract_endpoint_from_docstring(
    method_node: ast.AsyncFunctionDef,
) -> Optional[str]:
    """Extract endpoint URL from method docstring if it contains endpoint info."""
    docstring = ast.get_docstring(method_node)
    if not docstring:
        return None

    # Look for patterns like "endpoint 5: GET /rest/ofscMetadata/v1/activityTypes/{label}"
    import re

    endpoint_pattern = r"endpoint \d+:\s*\w+\s+(/rest/[^\s\n]+)"
    match = re.search(endpoint_pattern, docstring, re.IGNORECASE)
    if match:
        return match.group(1)

    # Look for direct endpoint URLs in docstrings
    url_pattern = r"(/rest/ofsc[A-Za-z]+/v\d+/[^\s\n]+)"
    match = re.search(url_pattern, docstring)
    if match:
        return match.group(1)

    return None


def find_method_for_endpoint(
    method_mapping: Dict[str, List[Dict[str, Any]]],
    endpoint_method: str,
    endpoint_path: str,
) -> Optional[str]:
    """Find the implementation method for a given endpoint with HTTP method awareness."""

    normalized_path = endpoint_path
    http_method = endpoint_method.upper()

    # Create list of candidate methods from method_mapping
    candidates = []

    # Try exact path matches first
    for endpoint_url, method_infos in method_mapping.items():
        if endpoint_url == normalized_path:
            # Handle multiple methods for the same endpoint
            for method_info in method_infos:
                candidates.append((endpoint_url, method_info, "exact"))

    # Then try pattern matches for parameterized endpoints
    if not candidates:
        for endpoint_url, method_infos in method_mapping.items():
            pattern_path = re.sub(r"\{[^}]+\}", r"[^/]+", re.escape(endpoint_url))
            if re.match(f"^{pattern_path}$", normalized_path):
                # Handle multiple methods for the same endpoint
                for method_info in method_infos:
                    candidates.append((endpoint_url, method_info, "pattern"))

    # If no candidates found, return None
    if not candidates:
        return None

    # Filter candidates by HTTP method compatibility
    best_match = _find_best_method_match(candidates, http_method, normalized_path)

    if best_match:
        method_info = best_match[1]
        class_name = method_info["class_name"]
        method_name = method_info["method_name"]
        filename = method_info["filename"]
        return f"{filename}:{class_name}.{method_name}()"

    return None


def _find_best_method_match(
    candidates: List[Tuple[str, Dict[str, Any], str]],
    http_method: str,
    endpoint_path: str,
) -> Optional[Tuple[str, Dict[str, Any], str]]:
    """Find the best method match based on HTTP method and method name patterns."""

    # Score each candidate based on HTTP method compatibility
    scored_candidates = []

    for endpoint_url, method_info, match_type in candidates:
        method_name = method_info["method_name"]
        score = 0

        # HTTP method compatibility scoring
        if http_method == "GET":
            if method_name.startswith("get_"):
                score += 100
            elif method_name.startswith(("list_", "search_", "find_")):
                score += 80
            elif method_name.startswith(("create_", "update_", "delete_", "set_")):
                score -= 50  # Penalize non-GET methods for GET endpoints

        elif http_method == "POST":
            if method_name.startswith(
                ("create_", "add_", "start_", "complete_", "cancel_", "move_")
            ):
                score += 100
            elif method_name.startswith("post_"):
                score += 90
            elif "bulk" in method_name.lower():
                score += 85
            elif method_name.startswith("get_"):
                score -= 50

        elif http_method == "PUT":
            if method_name.startswith(("create_", "create_or_replace_")):
                score += 105  # Prefer create methods for PUT (upsert semantics)
            elif method_name.startswith("set_"):
                score += 100
            elif method_name.startswith("put_"):
                score += 90
            elif method_name.startswith(("get_", "delete_")):
                score -= 50

        elif http_method == "PATCH":
            if method_name.startswith(("update_", "patch_", "modify_")):
                score += 100
            elif method_name.startswith(("get_", "delete_", "create_")):
                score -= 50

        elif http_method == "DELETE":
            if method_name.startswith("delete_"):
                score += 100
            elif method_name.startswith(("remove_", "clear_")):
                score += 80
            elif method_name.startswith(("get_", "create_", "update_")):
                score -= 50

        # Path parameter compatibility
        endpoint_params = set(re.findall(r"\{([^}]+)\}", endpoint_path))
        if "label" in endpoint_params and not method_name.endswith("s"):
            score += 20  # Single resource methods
        elif not endpoint_params and method_name.endswith("s"):
            score += 20  # List methods

        # Exact match bonus
        if match_type == "exact":
            score += 10

        scored_candidates.append((score, endpoint_url, method_info, match_type))

    # Sort by score (highest first) and return the best match
    if scored_candidates:
        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        best_score, endpoint_url, method_info, match_type = scored_candidates[0]

        # Only return if score is positive (indicates good compatibility)
        if best_score > 0:
            return (endpoint_url, method_info, match_type)

    return None


def create_schema_to_model_mapping() -> Dict[str, str]:
    """Create mapping from swagger schema names to actual Pydantic model names."""

    # Schema name -> Model name mapping
    schema_mappings = {
        # Activity Types
        "ActivityTypes": "ActivityTypeListResponse",
        "ActivityType": "ActivityType",
        "ActivityTypeGroups": "ActivityTypeGroupListResponse",
        "ActivityTypeGroup": "ActivityTypeGroup",
        # Applications
        "Applications": "ApplicationListResponse",
        "Application": "Application",
        "ApplicationApiAccess": "ApplicationApiAccess",
        "ApplicationApiAccessList": "ApplicationApiAccessListResponse",
        # Capacity
        "CapacityAreas": "CapacityAreaListResponse",
        "CapacityArea": "CapacityArea",
        "CapacityCategories": "CapacityCategoryListResponse",
        "CapacityCategory": "CapacityCategoryResponse",
        "CapacityAreaCategories": "CapacityAreaCategoryListResponse",
        "CapacityAreaWorkzones": "CapacityAreaWorkzoneListResponse",
        "CapacityAreaTimeSlots": "CapacityAreaTimeSlotListResponse",
        "CapacityAreaTimeIntervals": "CapacityAreaTimeIntervalListResponse",
        "CapacityAreaOrganizations": "CapacityAreaOrganizationListResponse",
        # Properties
        "PropertiesGet": "PropertyListResponse",
        "PropertyResponse": "PropertyResponse",
        "EnumerationValueList": "EnumerationValueList",
        # Work Skills
        "WorkSkills": "WorkskillListResponse",
        "WorkSkill": "Workskill",
        "WorkSkillGroups": "WorkSkillGroupListResponse",
        "WorkSkillGroup": "WorkSkillGroup",
        "WorkSkillConditions": "WorkskillConditionListResponse",
        # Organizations
        "Organizations": "OrganizationListResponse",
        "Organization": "Organization",
        # Resource Types
        "ResourceTypes": "ResourceTypeListResponse",
        # Inventory Types
        "InventoryTypes": "InventoryTypeListResponse",
        "InventoryType": "InventoryType",
        # Forms
        "Forms": "FormListResponse",
        "Form": "Form",
        # Languages
        "Languages": "LanguageListResponse",
        # Link Templates
        "LinkTemplates": "LinkTemplateListResponse",
        "LinkTemplate": "LinkTemplate",
        # Non-Working Reasons
        "NonWorkingReasons": "NonWorkingReasonListResponse",
        # Routing
        "routingProfileLabels": "RoutingProfileListResponse",
        "RoutingPlanList": "RoutingPlanListResponse",
        "RoutingPlanExportResponse": "RoutingPlanExportResponse",
        # Shifts
        "Shifts": "ShiftListResponse",
        "Shift": "Shift",
        # Time Slots
        "TimeSlots": "TimeSlotListResponse",
        # Work Zones
        "workZones": "WorkzoneListResponse",
        "workZone": "Workzone",
        "workZoneKey": "WorkZoneKeyResponse",
        # Core API Types
        "activities": "ActivityListResponse",
        "activity": "Activity",
        "getActivitiesResponse": "ActivityListResponse",
        "users": "UserListResponse",
        "user": "User",
        "resources": "ResourceListResponse",
        "resource": "Resource",
    }

    return schema_mappings


def map_schema_to_model_name(schema_name: str) -> str:
    """Map swagger schema name to actual Pydantic model name."""
    if not schema_name:
        return "ResponseModel"

    mappings = create_schema_to_model_mapping()

    # Try direct mapping first
    if schema_name in mappings:
        return mappings[schema_name]

    # Pattern-based mapping for common cases
    if schema_name.endswith("s") and not schema_name.endswith("ss"):
        # Likely a plural/list response
        singular = schema_name[:-1]
        if singular in mappings:
            return mappings[singular].replace("Response", "ListResponse")
        else:
            return f"{singular}ListResponse"

    # If no mapping found, return as-is (might be a valid model name already)
    return schema_name


def generate_method_signature(
    method_mapping: Dict[str, Dict[str, Any]],
    endpoint_method: str,
    endpoint_path: str,
    response_schema: str = "",
) -> str:
    """Generate a method signature for the endpoint if implemented."""

    # Use the HTTP method-aware matching to find the correct method
    method_name = find_method_for_endpoint(
        method_mapping, endpoint_method, endpoint_path
    )
    if not method_name:
        return ""

    # Extract just the method name from the full reference (e.g., "file.py:Class.method()" -> "method")
    if ":" in method_name and "." in method_name:
        method_name_only = method_name.split(".")[-1].replace("()", "")
    else:
        return ""

    # Find the method info for parameter extraction
    method_info = None
    for endpoint_url, method_infos in method_mapping.items():
        # Handle multiple methods per endpoint
        for info in method_infos:
            if info["method_name"] == method_name_only:
                # First try exact match
                if endpoint_url == endpoint_path:
                    method_info = info
                    break
                # Then try pattern match for parameterized endpoints
                pattern_path = re.sub(r"\{[^}]+\}", r"[^/]+", re.escape(endpoint_url))
                if re.match(f"^{pattern_path}$", endpoint_path):
                    method_info = info
                    break
        if method_info:
            break

    if not method_info:
        return ""

    # Use the correctly matched method name
    method_name = method_name_only

    # Use actual parsed parameters if available
    if "parameters" in method_info:
        params = []
        for param in method_info["parameters"]:
            param_str = param["name"]

            # Add type annotation if available
            if param["annotation"]:
                param_str += f": {param['annotation']}"
            elif param["name"].startswith("**") or param["name"].startswith("*"):
                # Don't add default type annotations for *args or **kwargs
                pass
            elif param["name"] in ["offset", "limit"]:
                param_str += ": int"
            elif param["name"] in ["label", "id"]:
                param_str += ": str"
            else:
                param_str += ": str"  # Default assumption

            # Add default value if available
            if param["default"]:
                param_str += f" = {param['default']}"

            params.append(param_str)
    else:
        # Fallback to basic parameter inference
        params = _infer_basic_parameters(endpoint_method, endpoint_path, method_name)

    # Determine the correct return type
    if "return_annotation" in method_info and method_info["return_annotation"]:
        return_type = method_info["return_annotation"]
    else:
        return_type = (
            map_schema_to_model_name(response_schema)
            if response_schema
            else "ResponseModel"
        )

    signature = (
        f"async def {method_name}({', '.join(['self'] + params)}) -> {return_type}"
    )
    return signature


def _infer_basic_parameters(
    endpoint_method: str, endpoint_path: str, method_name: str
) -> List[str]:
    """Fallback parameter inference when AST parsing doesn't provide parameters."""
    params = []

    # Extract parameter names from path
    path_params = re.findall(r"\{([^}]+)\}", endpoint_path)

    if path_params:
        params.extend([f"{param}: str" for param in path_params])

    # Add common parameters based on method type
    if endpoint_method.upper() == "GET":
        if (
            "offset" not in str(path_params)
            and "get_" in method_name
            and any(
                word in method_name
                for word in ["list", "s", "activities", "users", "resources"]
            )
        ):
            params.extend(["offset: int = 0", "limit: int = 100"])
    elif endpoint_method.upper() in ["POST", "PUT", "PATCH"]:
        if "data" not in str(path_params):
            params.append("data: dict")

    return params


def load_endpoints_mapping() -> Dict[str, int]:
    """Load endpoint mapping from ENDPOINTS.md."""
    endpoints_file = Path("docs/ENDPOINTS.md")
    if not endpoints_file.exists():
        print(f"Warning: {endpoints_file} not found, using sequential IDs")
        return {}

    mapping = {}
    with open(endpoints_file, "r") as f:
        for line in f:
            # Parse table rows like: | 1 | `/rest/ofscMetadata/v1/activityTypeGroups` | GET | metadata | v3.0.0-dev |...
            if re.match(r"^\|\s*\d+\s*\|", line):
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 4:
                    try:
                        endpoint_id = int(parts[1])
                        path = parts[2].strip("`")
                        method = parts[3].upper()
                        key = f"{method} {path}"
                        mapping[key] = endpoint_id
                    except (ValueError, IndexError):
                        continue

    print(f"Loaded {len(mapping)} endpoint mappings from ENDPOINTS.md")
    return mapping


def extract_endpoints_from_swagger(swagger_file: str) -> List[EndpointInfo]:
    """Extract all endpoint information from swagger.json."""

    with open(swagger_file, "r") as f:
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
            if method_name.lower() not in ["get", "post", "put", "patch", "delete"]:
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
                    request_body_schema = (
                        schema_ref.replace("#/definitions/", "") if schema_ref else None
                    )
                elif param_obj.required:
                    required_params.append(param_obj)
                else:
                    optional_params.append(param_obj)

            # Get response schema
            responses = method_data.get("responses", {})
            response_schema = ""
            if "200" in responses:
                schema_ref = responses["200"].get("schema", {}).get("$ref", "")
                response_schema = (
                    schema_ref.replace("#/definitions/", "") if schema_ref else ""
                )

            # Find method implementation
            implemented_in = find_method_for_endpoint(method_mapping, method, path)
            signature = generate_method_signature(
                method_mapping, method, path, response_schema
            )

            endpoint = EndpointInfo(
                id=mapped_id,
                path=path,
                method=method,
                module=get_module_from_path(path),
                summary=method_data.get("summary", ""),
                description=method_data.get("description", "")
                .replace("<p>", "")
                .replace("</p>", "")
                .strip(),
                operation_id=method_data.get("operationId", ""),
                tags=method_data.get("tags", []),
                required_parameters=required_params,
                optional_parameters=optional_params,
                request_body_schema=request_body_schema,
                response_schema=response_schema,
                implemented_in=implemented_in or "",
                signature=signature,
                rate_limits=None,  # No rate limits found in swagger
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
        module_content += "    EndpointInfo(\n"
        module_content += f"        id={endpoint.id},\n"
        module_content += f"        path={repr(endpoint.path)},\n"
        module_content += f"        method={repr(endpoint.method)},\n"
        module_content += f"        module={repr(endpoint.module)},\n"
        module_content += f"        summary={repr(endpoint.summary)},\n"
        module_content += f"        description={repr(endpoint.description)},\n"
        module_content += f"        operation_id={repr(endpoint.operation_id)},\n"
        module_content += f"        tags={repr(endpoint.tags)},\n"

        # Parameters
        module_content += "        required_parameters=[\n"
        for param in endpoint.required_parameters:
            module_content += "            EndpointParameter(\n"
            module_content += f"                name={repr(param.name)},\n"
            module_content += f"                location={repr(param.location)},\n"
            module_content += f"                type={repr(param.type)},\n"
            module_content += f"                required={param.required},\n"
            module_content += (
                f"                description={repr(param.description)},\n"
            )
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
            module_content += "            ),\n"
        module_content += "        ],\n"

        module_content += "        optional_parameters=[\n"
        for param in endpoint.optional_parameters:
            module_content += "            EndpointParameter(\n"
            module_content += f"                name={repr(param.name)},\n"
            module_content += f"                location={repr(param.location)},\n"
            module_content += f"                type={repr(param.type)},\n"
            module_content += f"                required={param.required},\n"
            module_content += (
                f"                description={repr(param.description)},\n"
            )
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
            module_content += "            ),\n"
        module_content += "        ],\n"

        module_content += (
            f"        request_body_schema={repr(endpoint.request_body_schema)},\n"
        )
        module_content += f"        response_schema={repr(endpoint.response_schema)},\n"
        module_content += f"        implemented_in={repr(endpoint.implemented_in)},\n"
        module_content += f"        signature={repr(endpoint.signature)},\n"
        module_content += f"        rate_limits={repr(endpoint.rate_limits)},\n"
        module_content += "    ),\n"

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
    with open(registry_file, "w") as f:
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
        module_implemented = sum(
            1 for ep in endpoints if ep.module == module and ep.implemented_in
        )
        print(
            f"  {module}: {count} endpoints ({module_implemented} implemented, {module_implemented / count * 100:.1f}%)"
        )

    print("\nImplementation Summary:")
    print(f"  Total endpoints: {len(endpoints)}")
    print(f"  Implemented endpoints: {implemented_count}")
    print(f"  Implementation coverage: {implemented_count / len(endpoints) * 100:.1f}%")


if __name__ == "__main__":
    main()
