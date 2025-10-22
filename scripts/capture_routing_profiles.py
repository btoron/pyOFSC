"""
Script to capture real routing profiles API responses from Oracle Field Service.
This script will call all GET endpoints and save responses for model design and testing.
"""

import json
import os
from datetime import date
from pathlib import Path
from dotenv import load_dotenv
from ofsc import OFSC

# Load environment variables
load_dotenv()

# Initialize OFSC instance
instance = OFSC(
    clientID=os.getenv("OFSC_CLIENT_ID"),
    companyName=os.getenv("OFSC_COMPANY"),
    secret=os.getenv("OFSC_CLIENT_SECRET"),
    root=os.getenv("OFSC_ROOT"),
)

# Output directory
output_dir = Path(__file__).parent.parent / "tests" / "saved_responses" / "routing_profiles"
output_dir.mkdir(parents=True, exist_ok=True)

print("Starting routing profiles API exploration...")
print(f"Output directory: {output_dir}")
print("=" * 80)


def save_response(filename: str, description: str, request_params: dict, response_data: dict, status_code: int):
    """Save API response to JSON file."""
    data = {
        "description": description,
        "request_params": request_params,
        "status_code": status_code,
        "response_data": response_data
    }

    filepath = output_dir / filename
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    print(f"✓ Saved: {filename}")


# Step 1: Get all routing profiles
print("\n1. Fetching all routing profiles...")
print("-" * 80)

try:
    # Try to access the routing profiles endpoint
    # Since this is not yet implemented, we'll need to use the raw API
    import requests
    from urllib.parse import urljoin

    base_url = instance._config.baseURL
    headers = instance.metadata.headers

    # GET /routingProfiles
    url = urljoin(base_url, "/rest/ofscMetadata/v1/routingProfiles")
    print(f"Calling: {url}")

    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Response structure: {list(data.keys())}")
        if "items" in data:
            print(f"Number of profiles: {len(data['items'])}")
            if data['items']:
                print(f"First profile sample: {json.dumps(data['items'][0], indent=2)}")

        save_response(
            "get_routing_profiles.json",
            "Get all routing profiles",
            {},
            data,
            response.status_code
        )

        # Store profile labels for next steps
        profile_labels = []
        if "items" in data and data["items"]:
            # Try both 'label' and 'profileLabel' keys
            profile_labels = [
                item.get("profileLabel") or item.get("label")
                for item in data["items"]
                if "profileLabel" in item or "label" in item
            ]
            print(f"Profile labels found: {profile_labels}")

    else:
        print(f"Error: {response.status_code}")
        print(f"Response: {response.text}")
        save_response(
            "get_routing_profiles_error.json",
            "Error getting routing profiles",
            {},
            {"error": response.text},
            response.status_code
        )
        profile_labels = []

except Exception as e:
    print(f"Exception: {e}")
    profile_labels = []


# Step 2: Get routing plans for each profile
if profile_labels:
    print(f"\n2. Fetching routing plans for first profile: {profile_labels[0]}...")
    print("-" * 80)

    try:
        profile_label = profile_labels[0]
        url = urljoin(base_url, f"/rest/ofscMetadata/v1/routingProfiles/{profile_label}/plans")
        print(f"Calling: {url}")

        response = requests.get(url, headers=headers)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Response structure: {list(data.keys())}")
            if "items" in data:
                print(f"Number of plans: {len(data['items'])}")
                if data['items']:
                    print(f"First plan sample: {json.dumps(data['items'][0], indent=2)}")

            save_response(
                "get_routing_profile_plans.json",
                f"Get routing plans for profile {profile_label}",
                {"profileLabel": profile_label},
                data,
                response.status_code
            )

            # Store plan labels for next step
            plan_labels = []
            if "items" in data and data["items"]:
                # Try both 'label' and 'planLabel' keys
                plan_labels = [
                    item.get("planLabel") or item.get("label")
                    for item in data["items"]
                    if "planLabel" in item or "label" in item
                ]
                print(f"Plan labels found: {plan_labels}")
        else:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text}")
            plan_labels = []

    except Exception as e:
        print(f"Exception: {e}")
        plan_labels = []


    # Step 3: Export a routing plan
    if profile_labels and plan_labels:
        print(f"\n3. Exporting routing plan: {profile_labels[0]}/{plan_labels[0]}...")
        print("-" * 80)

        try:
            profile_label = profile_labels[0]
            plan_label = plan_labels[0]
            url = urljoin(
                base_url,
                f"/rest/ofscMetadata/v1/routingProfiles/{profile_label}/plans/{plan_label}/custom-actions/export"
            )
            print(f"Calling: {url}")

            response = requests.get(url, headers=headers)
            print(f"Status: {response.status_code}")
            print(f"Content-Type: {response.headers.get('Content-Type')}")

            if response.status_code == 200:
                # Check if response is JSON or other format
                content_type = response.headers.get('Content-Type', '')

                if 'json' in content_type:
                    data = response.json()
                    print(f"Response structure: {list(data.keys())}")
                else:
                    # Binary or text content
                    print(f"Response size: {len(response.content)} bytes")
                    print(f"First 500 chars: {response.text[:500]}")
                    data = {
                        "content_type": content_type,
                        "content_length": len(response.content),
                        "content_preview": response.text[:1000] if len(response.text) < 10000 else response.text[:1000] + "..."
                    }

                save_response(
                    "export_routing_plan.json",
                    f"Export routing plan {profile_label}/{plan_label}",
                    {"profileLabel": profile_label, "planLabel": plan_label},
                    data,
                    response.status_code
                )
            else:
                print(f"Error: {response.status_code}")
                print(f"Response: {response.text}")

        except Exception as e:
            print(f"Exception: {e}")
    else:
        print("\n3. Skipping export (no plans available)")
else:
    print("\n2-3. Skipping plan operations (no profiles available)")


print("\n" + "=" * 80)
print("API exploration complete!")
print(f"Saved responses in: {output_dir}")
print("\nNext steps:")
print("1. Review the captured responses")
print("2. Design Pydantic models based on actual structure")
print("3. Create tests using the saved responses")
