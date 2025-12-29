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
        {
            "name": "get_workzones_200_success",
            "description": "Get all workzones",
            "method": "GET",
            "path": "/rest/ofscMetadata/v1/workZones",
            "params": None,
            "body": None,
            "metadata": {"workzone_label": "ALL_WORKZONES"},
        },
    ],
    "properties": [
        {
            "name": "get_properties_200_success",
            "description": "Get all properties with pagination",
            "method": "GET",
            "path": "/rest/ofscMetadata/v1/properties",
            "params": {"offset": 0, "limit": 100},
            "body": None,
            "metadata": {},
        },
        {
            "name": "get_property_200_success",
            "description": "Get a single property by label",
            "method": "GET",
            "path": "/rest/ofscMetadata/v1/properties/appt_number",
            "params": None,
            "body": None,
            "metadata": {"property_label": "appt_number"},
        },
        {
            "name": "get_property_404_not_found",
            "description": "Get a non-existent property",
            "method": "GET",
            "path": "/rest/ofscMetadata/v1/properties/NONEXISTENT_PROPERTY_12345",
            "params": None,
            "body": None,
            "metadata": {"property_label": "NONEXISTENT_PROPERTY_12345"},
        },
        {
            "name": "get_enumeration_values_200_success",
            "description": "Get enumeration values for a property",
            "method": "GET",
            "path": "/rest/ofscMetadata/v1/properties/complete_code/enumerationList",
            "params": {"offset": 0, "limit": 100},
            "body": None,
            "metadata": {"property_label": "complete_code"},
        },
        {
            "name": "get_enumeration_values_404_not_found",
            "description": "Get enumeration values for non-existent property",
            "method": "GET",
            "path": "/rest/ofscMetadata/v1/properties/NONEXISTENT_PROPERTY_12345/enumerationList",
            "params": None,
            "body": None,
            "metadata": {"property_label": "NONEXISTENT_PROPERTY_12345"},
        },
        {
            "name": "create_or_update_enumeration_values_200_success",
            "description": "Create or update enumeration values for a property",
            "method": "PUT",
            "path": "/rest/ofscMetadata/v1/properties/complete_code/enumerationList",
            "params": None,
            "body": {
                "items": [
                    {
                        "label": "1",
                        "active": True,
                        "translations": [
                            {"language": "en", "name": "E1 - Complete, No Issues"}
                        ],
                    },
                    {
                        "label": "2",
                        "active": True,
                        "translations": [
                            {"language": "en", "name": "E2 - Complete, Plant Issue"}
                        ],
                    },
                    {
                        "label": "3",
                        "active": True,
                        "translations": [
                            {"language": "en", "name": "E3 - Complete, Drop Replace"}
                        ],
                    },
                ]
            },
            "metadata": {"property_label": "complete_code"},
        },
        {
            "name": "create_or_update_enumeration_values_404_not_found",
            "description": "Create or update enumeration values for non-existent property",
            "method": "PUT",
            "path": "/rest/ofscMetadata/v1/properties/NONEXISTENT_PROPERTY_12345/enumerationList",
            "params": None,
            "body": {
                "items": [
                    {
                        "label": "TEST",
                        "active": True,
                        "translations": [{"language": "en", "name": "Test Value"}],
                    }
                ]
            },
            "metadata": {"property_label": "NONEXISTENT_PROPERTY_12345"},
        },
    ],
    "time_slots": [
        {
            "name": "get_time_slots_200_success",
            "description": "Get all time slots with pagination",
            "method": "GET",
            "path": "/rest/ofscMetadata/v1/timeSlots",
            "params": {"offset": 0, "limit": 100},
            "body": None,
            "metadata": {},
        },
        {
            "name": "get_time_slot_200_success",
            "description": "Get a single time slot by label",
            "method": "GET",
            "path": "/rest/ofscMetadata/v1/timeSlots/08-10",
            "params": None,
            "body": None,
            "metadata": {"time_slot_label": "08-10"},
        },
        {
            "name": "get_time_slot_404_not_found",
            "description": "Get a non-existent time slot",
            "method": "GET",
            "path": "/rest/ofscMetadata/v1/timeSlots/NONEXISTENT_TIME_SLOT_12345",
            "params": None,
            "body": None,
            "metadata": {"time_slot_label": "NONEXISTENT_TIME_SLOT_12345"},
        },
    ],
    "activity_type_groups": [
        {
            "name": "get_activity_type_groups_200_success",
            "description": "Get all activity type groups with pagination",
            "method": "GET",
            "path": "/rest/ofscMetadata/v1/activityTypeGroups",
            "params": {"offset": 0, "limit": 100},
            "body": None,
            "metadata": {},
        },
        {
            "name": "get_activity_type_group_200_success",
            "description": "Get a single activity type group by label",
            "method": "GET",
            "path": "/rest/ofscMetadata/v1/activityTypeGroups/customer",
            "params": None,
            "body": None,
            "metadata": {"activity_type_group_label": "customer"},
        },
        {
            "name": "get_activity_type_group_404_not_found",
            "description": "Get a non-existent activity type group",
            "method": "GET",
            "path": "/rest/ofscMetadata/v1/activityTypeGroups/NONEXISTENT_GROUP_12345",
            "params": None,
            "body": None,
            "metadata": {"activity_type_group_label": "NONEXISTENT_GROUP_12345"},
        },
    ],
    "activity_types": [
        {
            "name": "get_activity_types_200_success",
            "description": "Get all activity types with pagination",
            "method": "GET",
            "path": "/rest/ofscMetadata/v1/activityTypes",
            "params": {"offset": 0, "limit": 100},
            "body": None,
            "metadata": {},
        },
        {
            "name": "get_activity_type_200_success",
            "description": "Get a single activity type by label",
            "method": "GET",
            "path": "/rest/ofscMetadata/v1/activityTypes/LU",
            "params": None,
            "body": None,
            "metadata": {"activity_type_label": "LU"},
        },
        {
            "name": "get_activity_type_404_not_found",
            "description": "Get a non-existent activity type",
            "method": "GET",
            "path": "/rest/ofscMetadata/v1/activityTypes/NONEXISTENT_TYPE_12345",
            "params": None,
            "body": None,
            "metadata": {"activity_type_label": "NONEXISTENT_TYPE_12345"},
        },
    ],
    "capacity_areas": [
        {
            "name": "get_capacity_areas_200_success",
            "description": "Get all capacity areas with default fields",
            "method": "GET",
            "path": "/rest/ofscMetadata/v1/capacityAreas",
            "params": None,
            "body": None,
            "metadata": {},
        },
        {
            "name": "get_capacity_areas_expanded_200_success",
            "description": "Get all capacity areas with parent expansion and all fields",
            "method": "GET",
            "path": "/rest/ofscMetadata/v1/capacityAreas",
            "params": {
                "expand": "parent",
                "fields": "label,name,type,status,parent.name,parent.label",
            },
            "body": None,
            "metadata": {},
        },
        {
            "name": "get_capacity_area_200_success",
            "description": "Get a single capacity area by label",
            "method": "GET",
            "path": "/rest/ofscMetadata/v1/capacityAreas/FLUSA",
            "params": None,
            "body": None,
            "metadata": {"capacity_area_label": "FLUSA"},
        },
        {
            "name": "get_capacity_area_404_not_found",
            "description": "Get a non-existent capacity area",
            "method": "GET",
            "path": "/rest/ofscMetadata/v1/capacityAreas/NONEXISTENT_AREA_12345",
            "params": None,
            "body": None,
            "metadata": {"capacity_area_label": "NONEXISTENT_AREA_12345"},
        },
    ],
    "capacity_categories": [
        {
            "name": "get_capacity_categories_200_success",
            "description": "Get all capacity categories with pagination",
            "method": "GET",
            "path": "/rest/ofscMetadata/v1/capacityCategories",
            "params": {"offset": 0, "limit": 100},
            "body": None,
            "metadata": {},
        },
        {
            "name": "get_capacity_category_200_success",
            "description": "Get a single capacity category by label",
            "method": "GET",
            "path": "/rest/ofscMetadata/v1/capacityCategories/EST",
            "params": None,
            "body": None,
            "metadata": {"capacity_category_label": "EST"},
        },
        {
            "name": "get_capacity_category_404_not_found",
            "description": "Get a non-existent capacity category",
            "method": "GET",
            "path": "/rest/ofscMetadata/v1/capacityCategories/NONEXISTENT_CATEGORY_12345",
            "params": None,
            "body": None,
            "metadata": {"capacity_category_label": "NONEXISTENT_CATEGORY_12345"},
        },
    ],
    "forms": [
        {
            "name": "get_forms_200_success",
            "description": "Get all forms with pagination",
            "method": "GET",
            "path": "/rest/ofscMetadata/v1/forms",
            "params": {"offset": 0, "limit": 100},
            "body": None,
            "metadata": {},
        },
        {
            "name": "get_form_200_success",
            "description": "Get a single form by label",
            "method": "GET",
            "path": "/rest/ofscMetadata/v1/forms/case",
            "params": None,
            "body": None,
            "metadata": {"form_label": "case"},
        },
        {
            "name": "get_form_404_not_found",
            "description": "Get a non-existent form",
            "method": "GET",
            "path": "/rest/ofscMetadata/v1/forms/NONEXISTENT_FORM_12345",
            "params": None,
            "body": None,
            "metadata": {"form_label": "NONEXISTENT_FORM_12345"},
        },
    ],
    "non_working_reasons": [
        {
            "name": "get_non_working_reasons_200_success",
            "description": "Get all non-working reasons with pagination",
            "method": "GET",
            "path": "/rest/ofscMetadata/v1/nonWorkingReasons",
            "params": {"offset": 0, "limit": 100},
            "body": None,
            "metadata": {},
        },
        {
            "name": "get_non_working_reason_200_success",
            "description": "Get a single non-working reason by label",
            "method": "GET",
            "path": "/rest/ofscMetadata/v1/nonWorkingReasons/ILLNESS",
            "params": None,
            "body": None,
            "metadata": {"non_working_reason_label": "ILLNESS"},
        },
        {
            "name": "get_non_working_reason_404_not_found",
            "description": "Get a non-existent non-working reason",
            "method": "GET",
            "path": "/rest/ofscMetadata/v1/nonWorkingReasons/NONEXISTENT_REASON_12345",
            "params": None,
            "body": None,
            "metadata": {"non_working_reason_label": "NONEXISTENT_REASON_12345"},
        },
    ],
    "resource_types": [
        {
            "name": "get_resource_types_200_success",
            "description": "Get all resource types",
            "method": "GET",
            "path": "/rest/ofscMetadata/v1/resourceTypes",
            "params": None,
            "body": None,
            "metadata": {},
        },
    ],
    "organizations": [
        {
            "name": "get_organizations_200_success",
            "description": "Get all organizations",
            "method": "GET",
            "path": "/rest/ofscMetadata/v1/organizations",
            "params": None,
            "body": None,
            "metadata": {},
        },
        {
            "name": "get_organization_200_success",
            "description": "Get a single organization by label",
            "method": "GET",
            "path": "/rest/ofscMetadata/v1/organizations/default",
            "params": None,
            "body": None,
            "metadata": {"organization_label": "default"},
        },
        {
            "name": "get_organization_404_not_found",
            "description": "Get a non-existent organization",
            "method": "GET",
            "path": "/rest/ofscMetadata/v1/organizations/NONEXISTENT_ORG_12345",
            "params": None,
            "body": None,
            "metadata": {"organization_label": "NONEXISTENT_ORG_12345"},
        },
    ],
    "link_templates": [
        {
            "name": "get_link_templates_200_success",
            "description": "Get all link templates with pagination",
            "method": "GET",
            "path": "/rest/ofscMetadata/v1/linkTemplates",
            "params": {"offset": 0, "limit": 100},
            "body": None,
            "metadata": {},
        },
        {
            "name": "get_link_template_200_success",
            "description": "Get a single link template by label",
            "method": "GET",
            "path": "/rest/ofscMetadata/v1/linkTemplates/starts_after",
            "params": None,
            "body": None,
            "metadata": {"link_template_label": "starts_after"},
        },
        {
            "name": "get_link_template_404_not_found",
            "description": "Get a non-existent link template",
            "method": "GET",
            "path": "/rest/ofscMetadata/v1/linkTemplates/NONEXISTENT_TEMPLATE_12345",
            "params": None,
            "body": None,
            "metadata": {"link_template_label": "NONEXISTENT_TEMPLATE_12345"},
        },
    ],
    "map_layers": [
        {
            "name": "get_map_layers_200_success",
            "description": "Get all map layers with pagination",
            "method": "GET",
            "path": "/rest/ofscMetadata/v1/mapLayers",
            "params": {"offset": 0, "limit": 100},
            "body": None,
            "metadata": {},
        },
        {
            "name": "get_map_layer_404_not_found",
            "description": "Get a non-existent map layer",
            "method": "GET",
            "path": "/rest/ofscMetadata/v1/mapLayers/NONEXISTENT_LAYER_12345",
            "params": None,
            "body": None,
            "metadata": {"map_layer_label": "NONEXISTENT_LAYER_12345"},
        },
    ],
    "languages": [
        {
            "name": "get_languages_200_success",
            "description": "Get all languages with pagination",
            "method": "GET",
            "path": "/rest/ofscMetadata/v1/languages",
            "params": {"offset": 0, "limit": 100},
            "body": None,
            "metadata": {},
        },
        {
            "name": "get_language_200_success",
            "description": "Get a single language by label",
            "method": "GET",
            "path": "/rest/ofscMetadata/v1/languages/en-US",
            "params": None,
            "body": None,
            "metadata": {"language_label": "en-US"},
        },
        {
            "name": "get_language_404_not_found",
            "description": "Get a non-existent language",
            "method": "GET",
            "path": "/rest/ofscMetadata/v1/languages/NONEXISTENT_LANG_12345",
            "params": None,
            "body": None,
            "metadata": {"language_label": "NONEXISTENT_LANG_12345"},
        },
    ],
    "inventory_types": [
        {
            "name": "get_inventory_types_200_success",
            "description": "Get all inventory types with pagination",
            "method": "GET",
            "path": "/rest/ofscMetadata/v1/inventoryTypes",
            "params": {"offset": 0, "limit": 100},
            "body": None,
            "metadata": {},
        },
        {
            "name": "get_inventory_type_200_success",
            "description": "Get a single inventory type by label",
            "method": "GET",
            "path": "/rest/ofscMetadata/v1/inventoryTypes/gend205",
            "params": None,
            "body": None,
            "metadata": {"inventory_type_label": "gend205"},
        },
        {
            "name": "get_inventory_type_404_not_found",
            "description": "Get a non-existent inventory type",
            "method": "GET",
            "path": "/rest/ofscMetadata/v1/inventoryTypes/NONEXISTENT_TYPE_12345",
            "params": None,
            "body": None,
            "metadata": {"inventory_type_label": "NONEXISTENT_TYPE_12345"},
        },
    ],
    "routing_profiles": [
        {
            "name": "get_routing_profiles_200_success",
            "description": "Get all routing profiles",
            "method": "GET",
            "path": "/rest/ofscMetadata/v1/routingProfiles",
            "params": {"offset": 0, "limit": 100},
            "body": None,
            "metadata": {},
        },
        {
            "name": "get_routing_profile_plans_200_success",
            "description": "Get all routing plans for a profile",
            "method": "GET",
            "path": "/rest/ofscMetadata/v1/routingProfiles/MaintenanceRoutingProfile/plans",
            "params": {"offset": 0, "limit": 100},
            "body": None,
            "metadata": {"profile_label": "MaintenanceRoutingProfile"},
        },
        {
            "name": "get_routing_profile_plans_404_not_found",
            "description": "Get plans for a non-existent routing profile",
            "method": "GET",
            "path": "/rest/ofscMetadata/v1/routingProfiles/NONEXISTENT_PROFILE_12345/plans",
            "params": None,
            "body": None,
            "metadata": {"profile_label": "NONEXISTENT_PROFILE_12345"},
        },
        {
            "name": "export_routing_plan_200_success",
            "description": "Export a routing plan",
            "method": "GET",
            "path": "/rest/ofscMetadata/v1/routingProfiles/MaintenanceRoutingProfile/plans/Optimization/custom-actions/export",
            "params": None,
            "body": None,
            "metadata": {
                "profile_label": "MaintenanceRoutingProfile",
                "plan_label": "Optimization",
            },
        },
        {
            "name": "export_routing_plan_404_not_found",
            "description": "Export a non-existent routing plan",
            "method": "GET",
            "path": "/rest/ofscMetadata/v1/routingProfiles/MaintenanceRoutingProfile/plans/NONEXISTENT_PLAN_12345/custom-actions/export",
            "params": None,
            "body": None,
            "metadata": {
                "profile_label": "MaintenanceRoutingProfile",
                "plan_label": "NONEXISTENT_PLAN_12345",
            },
        },
    ],
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
    print("Client credentials loaded.\n")

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
