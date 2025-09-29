#!/usr/bin/env python3
"""Script to collect API response for a specific OFSC endpoint by ID.

This script reads the endpoint information from ENDPOINTS.md and makes
an actual API call to collect the response example.

Usage:
    python scripts/collect_endpoint_response.py <endpoint_id> [--label LABEL] [--params PARAM1 PARAM2 ...] [--media-type MEDIA_TYPE]

Examples:
    python scripts/collect_endpoint_response.py 27  # Collects response for forms endpoint
    python scripts/collect_endpoint_response.py 28 --label "mobile_provider_request#8#"  # Get specific form
    python scripts/collect_endpoint_response.py 54 --label "country_code"  # Get property enumeration
    python scripts/collect_endpoint_response.py 11 --params "demoauth" "metadataAPI"  # Get specific API access
    python scripts/collect_endpoint_response.py 11 --params demoauth metadataAPI  # Same as above
    python scripts/collect_endpoint_response.py 59 --params demoauth Optimization --media-type application/json  # Export with JSON format
"""

import argparse
import asyncio
import json
import os
import re
import sys
from datetime import datetime, UTC
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from dotenv import load_dotenv

# Add the project root to the path so we can import the OFSC client
sys.path.insert(0, str(Path(__file__).parent.parent))

from ofsc.client import OFSC

# Load environment variables
load_dotenv()

# OFSC credentials from .env
OFSC_INSTANCE = os.getenv("OFSC_INSTANCE")
OFSC_CLIENT_ID = os.getenv("OFSC_CLIENT_ID")
OFSC_CLIENT_SECRET = os.getenv("OFSC_CLIENT_SECRET")

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
ENDPOINTS_FILE = PROJECT_ROOT / "docs" / "ENDPOINTS.md"
RESPONSE_DIR = PROJECT_ROOT / "response_examples"


def parse_endpoints_file() -> Dict[int, Tuple[str, str, str]]:
    """Parse ENDPOINTS.md to extract endpoint information.

    Returns:
        Dict mapping endpoint ID to (path, method, module) tuple
    """
    endpoints = {}

    with open(ENDPOINTS_FILE, "r") as f:
        content = f.read()

    # Find the table section
    table_pattern = r"\| ID \| Endpoint Path \| Method \| Module \|.*?\n((?:\|.*?\n)+)"
    table_match = re.search(table_pattern, content, re.DOTALL)

    if not table_match:
        raise ValueError("Could not find endpoints table in ENDPOINTS.md")

    # Parse each row
    rows = table_match.group(1).strip().split("\n")
    for row in rows:
        if row.startswith("|---"):  # Skip separator rows
            continue

        parts = [
            p.strip() for p in row.split("|")[1:-1]
        ]  # Remove empty first/last elements
        if len(parts) >= 4:
            try:
                endpoint_id = int(parts[0])
                path = parts[1].strip("`")
                method = parts[2]
                module = parts[3]
                endpoints[endpoint_id] = (path, method, module)
            except (ValueError, IndexError):
                continue

    return endpoints


def get_description_from_path(path: str) -> str:
    """Generate a description from the endpoint path."""
    # Remove base path and parameters
    clean_path = path.replace("/rest/ofscMetadata/v1/", "").replace(
        "/rest/ofscCore/v1/", ""
    )
    clean_path = re.sub(r"\{[^}]+\}", "", clean_path)  # Remove parameters
    clean_path = clean_path.strip("/")

    # Convert to snake_case
    description = clean_path.replace("/", "_")

    # Handle special cases
    if "{" in path:
        description = f"get_{description}"
    else:
        description = f"get_{description}"

    return description


def extract_path_parameters(path: str) -> List[str]:
    """Extract parameter names from a path in order.

    Args:
        path: API path with parameters like '/rest/api/{param1}/sub/{param2}'

    Returns:
        List of parameter names in order: ['param1', 'param2']
    """
    import re

    # Find all parameters in curly braces
    parameters = re.findall(r"\{([^}]+)\}", path)
    return parameters


def replace_path_parameters(path: str, parameters: List[str]) -> str:
    """Replace path parameters with provided values in order.

    Args:
        path: API path with parameters like '/rest/api/{param1}/sub/{param2}'
        parameters: List of parameter values to substitute

    Returns:
        Path with parameters replaced
    """
    import re
    from urllib.parse import quote_plus

    # Find all parameter placeholders
    placeholders = re.findall(r"\{[^}]+\}", path)

    if len(parameters) != len(placeholders):
        raise ValueError(
            f"Expected {len(placeholders)} parameters, got {len(parameters)}"
        )

    # Replace each placeholder with the corresponding parameter value
    result_path = path
    for placeholder, param_value in zip(placeholders, parameters):
        # URL encode the parameter value
        encoded_value = quote_plus(str(param_value))
        result_path = result_path.replace(placeholder, encoded_value, 1)

    return result_path


async def collect_endpoint_response(
    endpoint_id: int,
    label: Optional[str] = None,
    params: Optional[List[str]] = None,
    media_type: Optional[str] = None,
) -> bool:
    """Collect response for a specific endpoint ID.

    Args:
        endpoint_id: The endpoint ID from ENDPOINTS.md
        label: Optional label parameter for single-parameter endpoints (legacy)
        params: Optional list of parameters for multi-parameter endpoints
        media_type: Optional media type for Accept header (e.g., 'application/json')

    Returns:
        True if successful, False otherwise
    """
    # Parse endpoints file
    endpoints = parse_endpoints_file()

    if endpoint_id not in endpoints:
        print(f"❌ Endpoint ID {endpoint_id} not found in ENDPOINTS.md")
        return False

    path, method, module = endpoints[endpoint_id]

    # Only support GET methods for now
    if method != "GET":
        print(
            f"❌ Only GET methods are supported. Endpoint {endpoint_id} uses {method}"
        )
        return False

    print(f"📡 Collecting endpoint #{endpoint_id}")
    print(f"   Path: {path}")
    print(f"   Method: {method}")
    print(f"   Module: {module}")

    # Check if credentials are available
    if not all([OFSC_INSTANCE, OFSC_CLIENT_ID, OFSC_CLIENT_SECRET]):
        print("❌ Missing OFSC credentials in .env file")
        return False

    # Handle parameterized paths
    if "{" in path:
        # Determine which parameter approach to use
        path_params = extract_path_parameters(path)

        if params:
            # New multi-parameter approach
            if len(params) != len(path_params):
                print(
                    f"⚠️  This endpoint requires {len(path_params)} parameters: {path_params}"
                )
                print(f"   You provided {len(params)} parameters: {params}")
                print(
                    f"   Example: python scripts/collect_endpoint_response.py {endpoint_id} --params {' '.join(['<' + p + '>' for p in path_params])}"
                )
                return False

            # Replace parameters using the new helper function
            path = replace_path_parameters(path, params)
            print(f"   Using parameters: {dict(zip(path_params, params))}")
            print(f"   Final path: {path}")

        elif label:
            # Legacy single-parameter approach (for backward compatibility)
            if len(path_params) > 1:
                print(f"⚠️  This endpoint requires multiple parameters: {path_params}")
                print(
                    f"   Use --params instead: python scripts/collect_endpoint_response.py {endpoint_id} --params {' '.join(['<' + p + '>' for p in path_params])}"
                )
                return False

            # Replace single parameter with legacy method
            path = replace_path_parameters(path, [label])
            print(f"   Using label: {label}")
            print(f"   Final path: {path}")

        else:
            # No parameters provided
            print(f"⚠️  This endpoint requires parameters: {path_params}")
            if len(path_params) == 1:
                print(
                    f"   Example: python scripts/collect_endpoint_response.py {endpoint_id} --label 'your_label_here'"
                )
            else:
                print(
                    f"   Example: python scripts/collect_endpoint_response.py {endpoint_id} --params {' '.join(['<' + p + '>' for p in path_params])}"
                )
            return False

    async with OFSC(
        instance=OFSC_INSTANCE,
        client_id=OFSC_CLIENT_ID,
        client_secret=OFSC_CLIENT_SECRET,
        use_token=False,  # Use Basic Auth
    ) as client:
        try:
            # Prepare headers
            headers = {}
            if media_type:
                headers["Accept"] = media_type
                print(f"   Using Accept header: {media_type}")

            # Make the API call
            response = await client._client.get(
                path, headers=headers if headers else None
            )

            # Create response data with metadata
            response_data = {
                "_metadata": {
                    "endpoint_id": endpoint_id,
                    "path": path,
                    "method": method,
                    "timestamp": datetime.now(UTC).isoformat(),
                    "status_code": response.status_code,
                }
            }

            # Handle response
            if response.status_code == 200:
                try:
                    api_data = response.json()
                    response_data.update(api_data)
                    print(f"✅ Success: {response.status_code}")

                    # Check if it's an empty collection
                    if isinstance(api_data, dict) and api_data.get("totalResults") == 0:
                        print("ℹ️  Empty collection (totalResults: 0)")

                except json.JSONDecodeError:
                    response_data["raw_content"] = response.text
                    print("⚠️  Non-JSON response")
            else:
                try:
                    response_data.update(response.json())
                except:
                    response_data["error"] = response.text
                print(f"❌ Error {response.status_code}: {response.text[:100]}...")

            # Save response
            description = get_description_from_path(path)
            # If we used parameters, include them in the filename for clarity
            original_path = endpoints[endpoint_id][0]
            if (
                label or params
            ) and "{" in original_path:  # Check original path had parameters
                if params:
                    # Use all params for filename
                    safe_params = "_".join(
                        [re.sub(r"[^\w\-_.]", "_", str(p)) for p in params]
                    )
                    filename = f"{endpoint_id}_{description}_{safe_params}.json"
                elif label:
                    # Use label for backward compatibility
                    safe_label = re.sub(r"[^\w\-_.]", "_", label)
                    filename = f"{endpoint_id}_{description}_{safe_label}.json"
                else:
                    filename = f"{endpoint_id}_{description}.json"
            else:
                filename = f"{endpoint_id}_{description}.json"
            filepath = RESPONSE_DIR / filename

            # Ensure response directory exists
            RESPONSE_DIR.mkdir(exist_ok=True)

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(response_data, f, indent=2, ensure_ascii=False)

            print(f"💾 Saved: {filename}")
            return response.status_code == 200

        except Exception as e:
            print(f"💥 Exception: {e}")
            return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Collect OFSC API response for a specific endpoint"
    )
    parser.add_argument(
        "endpoint_id", type=int, help="The endpoint ID from ENDPOINTS.md"
    )
    parser.add_argument(
        "--label",
        type=str,
        help="Label parameter for parameterized endpoints (e.g., resource label, property name)",
    )
    parser.add_argument(
        "--params",
        nargs="*",
        help="Parameters for multi-parameter endpoints (e.g., --params param1 param2)",
    )
    parser.add_argument(
        "--media-type",
        type=str,
        help="Media type for Accept header (e.g., application/json, text/csv)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available endpoints instead of collecting",
    )

    args = parser.parse_args()

    if args.list:
        # List all endpoints
        endpoints = parse_endpoints_file()
        print("Available endpoints:")
        for eid, (path, method, module) in sorted(endpoints.items()):
            print(f"  {eid:3d}: {method:6s} {path}")
        return

    # Run the collection
    success = asyncio.run(
        collect_endpoint_response(
            args.endpoint_id, args.label, args.params, getattr(args, "media_type", None)
        )
    )

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
