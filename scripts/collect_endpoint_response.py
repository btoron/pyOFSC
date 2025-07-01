#!/usr/bin/env python3
"""Script to collect API response for a specific OFSC endpoint by ID.

This script reads the endpoint information from ENDPOINTS.md and makes
an actual API call to collect the response example.

Usage:
    python scripts/collect_endpoint_response.py <endpoint_id> [--label LABEL]
    
Examples:
    python scripts/collect_endpoint_response.py 27  # Collects response for forms endpoint
    python scripts/collect_endpoint_response.py 28 --label "mobile_provider_request#8#"  # Get specific form
    python scripts/collect_endpoint_response.py 54 --label "country_code"  # Get property enumeration
"""
import argparse
import asyncio
import json
import os
import re
import sys
from datetime import datetime, UTC
from pathlib import Path
from typing import Dict, Optional, Tuple

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
    
    with open(ENDPOINTS_FILE, 'r') as f:
        content = f.read()
    
    # Find the table section
    table_pattern = r'\| ID \| Endpoint Path \| Method \| Module \|.*?\n((?:\|.*?\n)+)'
    table_match = re.search(table_pattern, content, re.DOTALL)
    
    if not table_match:
        raise ValueError("Could not find endpoints table in ENDPOINTS.md")
    
    # Parse each row
    rows = table_match.group(1).strip().split('\n')
    for row in rows:
        if row.startswith('|---'):  # Skip separator rows
            continue
            
        parts = [p.strip() for p in row.split('|')[1:-1]]  # Remove empty first/last elements
        if len(parts) >= 4:
            try:
                endpoint_id = int(parts[0])
                path = parts[1].strip('`')
                method = parts[2]
                module = parts[3]
                endpoints[endpoint_id] = (path, method, module)
            except (ValueError, IndexError):
                continue
    
    return endpoints


def get_description_from_path(path: str) -> str:
    """Generate a description from the endpoint path."""
    # Remove base path and parameters
    clean_path = path.replace('/rest/ofscMetadata/v1/', '').replace('/rest/ofscCore/v1/', '')
    clean_path = re.sub(r'\{[^}]+\}', '', clean_path)  # Remove parameters
    clean_path = clean_path.strip('/')
    
    # Convert to snake_case
    description = clean_path.replace('/', '_')
    
    # Handle special cases
    if '{' in path:
        description = f"get_{description}"
    else:
        description = f"get_{description}"
    
    return description


async def collect_endpoint_response(endpoint_id: int, label: Optional[str] = None) -> bool:
    """Collect response for a specific endpoint ID.
    
    Args:
        endpoint_id: The endpoint ID from ENDPOINTS.md
        label: Optional label parameter for parameterized endpoints
        
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
        print(f"❌ Only GET methods are supported. Endpoint {endpoint_id} uses {method}")
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
    if '{' in path:
        if not label:
            print("⚠️  This endpoint requires parameters. Use --label to provide a value.")
            print(f"   Example: python scripts/collect_endpoint_response.py {endpoint_id} --label 'your_label_here'")
            return False
        
        # Replace {label} with the provided label value
        # Support common parameter patterns like {label}, {apiLabel}, {profileLabel}, etc.
        parameterized_path = path.replace('{label}', label)
        parameterized_path = parameterized_path.replace('{apiLabel}', label)
        parameterized_path = parameterized_path.replace('{profileLabel}', label)
        
        # URL encode the label to handle special characters
        from urllib.parse import quote_plus
        # For safety, let's encode the entire label portion
        path_parts = parameterized_path.split('/')
        for i, part in enumerate(path_parts):
            if part == label:
                path_parts[i] = quote_plus(label)
        path = '/'.join(path_parts)
        
        print(f"   Using label: {label}")
        print(f"   Final path: {path}")
    
    async with OFSC(
        instance=OFSC_INSTANCE,
        client_id=OFSC_CLIENT_ID,
        client_secret=OFSC_CLIENT_SECRET,
        use_token=False  # Use Basic Auth
    ) as client:
        try:
            # Make the API call
            response = await client._client.get(path)
            
            # Create response data with metadata
            response_data = {
                "_metadata": {
                    "endpoint_id": endpoint_id,
                    "path": path,
                    "method": method,
                    "timestamp": datetime.now(UTC).isoformat(),
                    "status_code": response.status_code
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
                        print(f"ℹ️  Empty collection (totalResults: 0)")
                        
                except json.JSONDecodeError:
                    response_data["raw_content"] = response.text
                    print(f"⚠️  Non-JSON response")
            else:
                try:
                    response_data.update(response.json())
                except:
                    response_data["error"] = response.text
                print(f"❌ Error {response.status_code}: {response.text[:100]}...")
                
            # Save response
            description = get_description_from_path(path)
            # If we used a label, include it in the filename for clarity
            if label and '{' in endpoints[endpoint_id][0]:  # Check original path had parameters
                safe_label = re.sub(r'[^\w\-_.]', '_', label)  # Replace unsafe chars with underscores
                filename = f"{endpoint_id}_{description}_{safe_label}.json"
            else:
                filename = f"{endpoint_id}_{description}.json"
            filepath = RESPONSE_DIR / filename
            
            # Ensure response directory exists
            RESPONSE_DIR.mkdir(exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
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
        "endpoint_id",
        type=int,
        help="The endpoint ID from ENDPOINTS.md"
    )
    parser.add_argument(
        "--label",
        type=str,
        help="Label parameter for parameterized endpoints (e.g., resource label, property name)"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available endpoints instead of collecting"
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
    success = asyncio.run(collect_endpoint_response(args.endpoint_id, args.label))
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()