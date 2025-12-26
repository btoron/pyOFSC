"""Script to capture and save OFSC API responses for testing.

This script uses httpx directly to capture real API responses from the OFSC API.
The ENDPOINTS dictionary can be expanded to capture responses from any metadata endpoint.

Usage:
    uv run python scripts/capture_api_responses.py

The script will:
1. Load credentials from .env file
2. Make HTTP requests to configured endpoints
3. Save responses to tests/saved_responses/{category}/{name}.json
"""

import asyncio
import base64
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

import httpx
from dotenv import load_dotenv


# Configuration for endpoints to capture
ENDPOINTS = {
    "workzones": [
        {
            "name": "get_workzone_200_success",
            "description": "Get a single workzone by label",
            "method": "GET",
            "path": "/rest/ofscMetadata/v1/workZones/ALTAMONTE_SPRINGS",
            "params": None,
            "body": None,
            "metadata": {"workzone_label": "ALTAMONTE_SPRINGS"},
        },
        {
            "name": "get_workzone_404_not_found",
            "description": "Get a non-existent workzone",
            "method": "GET",
            "path": "/rest/ofscMetadata/v1/workZones/NONEXISTENT_WORKZONE_12345",
            "params": None,
            "body": None,
            "metadata": {"workzone_label": "NONEXISTENT_WORKZONE_12345"},
        },
    ]
}


def load_config() -> Dict[str, Any]:
    """Load OFSC configuration from environment variables."""
    load_dotenv()

    client_id = os.environ.get("OFSC_CLIENT_ID")
    company_name = os.environ.get("OFSC_COMPANY")
    secret = os.environ.get("OFSC_CLIENT_SECRET")
    root = os.environ.get("OFSC_ROOT")

    if not all([client_id, company_name, secret]):
        raise ValueError(
            "Missing required environment variables: OFSC_CLIENT_ID, OFSC_COMPANY, OFSC_CLIENT_SECRET"
        )

    return {
        "clientID": client_id,
        "companyName": company_name,
        "secret": secret,
        "root": root,
    }


def get_auth_header(client_id: str, company_name: str, secret: str) -> str:
    """Generate Basic Auth header for OFSC API."""
    credentials = f"{client_id}@{company_name}:{secret}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return f"Basic {encoded}"


def get_base_url(company_name: str, base_url: Optional[str] = None) -> str:
    """Generate base URL for OFSC API."""
    return base_url or f"https://{company_name}.fs.ocs.oraclecloud.com"


async def capture_response(
    client: httpx.AsyncClient,
    endpoint: Dict[str, Any],
    base_url: str,
    auth_header: str,
) -> Dict[str, Any]:
    """Capture a single API response."""
    url = f"{base_url}{endpoint['path']}"
    headers = {
        "Authorization": auth_header,
        "Content-Type": "application/json",
    }

    print(f"  Capturing: {endpoint['method']} {endpoint['path']}")

    try:
        response = await client.request(
            method=endpoint["method"],
            url=url,
            headers=headers,
            params=endpoint.get("params"),
            json=endpoint.get("body"),
        )

        # Parse response body
        try:
            response_data = response.json()
        except Exception:
            response_data = response.text

        # Build the saved response structure
        saved_response = {
            "description": endpoint["description"],
            "status_code": response.status_code,
            "headers": {
                "Content-Type": response.headers.get(
                    "Content-Type", "application/json"
                ),
                "Cache-Control": response.headers.get(
                    "Cache-Control", "no-store, no-cache"
                ),
            },
            "request": {
                "url": url,
                "method": endpoint["method"],
            },
        }

        # Add request metadata if present
        if endpoint.get("metadata"):
            saved_response["request"].update(endpoint["metadata"])

        # Add params if present
        if endpoint.get("params"):
            saved_response["request"]["params"] = endpoint["params"]

        # Add body if present
        if endpoint.get("body"):
            saved_response["request"]["body"] = endpoint["body"]

        # For successful responses (2xx), store response_data
        # For error responses (4xx, 5xx), store body as JSON string
        if 200 <= response.status_code < 300:
            saved_response["response_data"] = response_data
        else:
            saved_response["body"] = (
                json.dumps(response_data)
                if isinstance(response_data, dict)
                else response_data
            )

        print(f"    ✓ Status: {response.status_code}")
        return saved_response

    except httpx.HTTPError as e:
        print(f"    ✗ HTTP Error: {e}")
        raise


async def save_all_responses():
    """Fetch and save all configured API responses."""
    # Load config
    config = load_config()
    client_id = config["clientID"]
    company_name = config["companyName"]
    secret = config["secret"]

    # Setup
    base_url = get_base_url(company_name)
    auth_header = get_auth_header(client_id, company_name, secret)

    print(f"Base URL: {base_url}")
    print(f"Client ID: {client_id}\n")

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Process each endpoint category
        for category, endpoints in ENDPOINTS.items():
            print(f"Processing category: {category}")

            # Create output directory
            output_dir = (
                Path(__file__).parent.parent / "tests" / "saved_responses" / category
            )
            output_dir.mkdir(parents=True, exist_ok=True)

            # Capture each endpoint
            for endpoint in endpoints:
                try:
                    saved_response = await capture_response(
                        client, endpoint, base_url, auth_header
                    )

                    # Save to file
                    output_file = output_dir / f"{endpoint['name']}.json"
                    with open(output_file, "w") as f:
                        json.dump(saved_response, f, indent=2)

                    print(f"    ✓ Saved to {output_file.relative_to(Path.cwd())}\n")

                except Exception as e:
                    print(f"    ✗ Error: {e}\n")

    print("Done!")


if __name__ == "__main__":
    asyncio.run(save_all_responses())
