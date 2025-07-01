#!/usr/bin/env python3
"""Script to collect real API responses from OFSC for endpoint implementation.

This script uses the existing .env credentials to make actual API calls to collect
real response examples for endpoints that need implementation.
"""
import asyncio
import json
import os
import sys
from datetime import datetime, UTC
from pathlib import Path
from typing import Dict, List, Optional

from dotenv import load_dotenv

# Add the project root to the path so we can import the OFSC client
sys.path.insert(0, str(Path(__file__).parent))

from ofsc.client import OFSC

# Load environment variables
load_dotenv()

# OFSC credentials from .env
OFSC_INSTANCE = os.getenv("OFSC_INSTANCE")  # sunrise0511
OFSC_CLIENT_ID = os.getenv("OFSC_CLIENT_ID")  # demoauth
OFSC_CLIENT_SECRET = os.getenv("OFSC_CLIENT_SECRET")

# Response examples directory
RESPONSE_DIR = Path(__file__).parent / "response_examples"


class OFSCResponseCollector:
    """Collects real API responses from OFSC endpoints."""

    def __init__(self):
        """Initialize the collector with OFSC credentials."""
        if not all([OFSC_INSTANCE, OFSC_CLIENT_ID, OFSC_CLIENT_SECRET]):
            raise ValueError("Missing OFSC credentials in .env file")
            
        self.client = OFSC(
            instance=OFSC_INSTANCE,
            client_id=OFSC_CLIENT_ID,
            client_secret=OFSC_CLIENT_SECRET,
            use_token=False  # Use Basic Auth like the tests
        )
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.client.__aenter__()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.client.__aexit__(exc_type, exc_val, exc_tb)
            
    async def collect_response(self, endpoint_id: int, path: str, description: str) -> bool:
        """Collect a single API response.
        
        Args:
            endpoint_id: OFSC endpoint ID number
            path: API endpoint path
            description: Description for filename
            
        Returns:
            True if successful, False if should stop (403, 404, etc.)
        """
        print(f"📡 Collecting endpoint #{endpoint_id}: {path}")
        
        try:
            # Use the OFSC client's HTTP client directly for raw API calls
            response = await self.client._client.get(path)
            
            # Create response data with metadata
            response_data = {
                "_metadata": {
                    "endpoint_id": endpoint_id,
                    "path": path,
                    "method": "GET",
                    "timestamp": datetime.now(UTC).isoformat(),
                    "status_code": response.status_code
                }
            }
            
            # Handle different response types
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
                    print(f"⚠️  Non-JSON response: {response.text[:100]}...")
                    
            elif response.status_code == 403:
                try:
                    response_data.update(response.json())
                except:
                    response_data["error"] = response.text
                print(f"🚫 Forbidden (403): Insufficient permissions")
                print(f"   Response: {response_data}")
                self._save_response(endpoint_id, description, response_data)
                return False  # Stop on permission error
                
            elif response.status_code == 404:
                try:
                    response_data.update(response.json())
                except:
                    response_data["error"] = response.text
                print(f"❌ Not Found (404): Endpoint may not exist or requires valid identifier")
                self._save_response(endpoint_id, description, response_data)
                return False  # Stop on not found
                
            else:
                try:
                    response_data.update(response.json())
                except:
                    response_data["error"] = response.text
                print(f"❌ Error {response.status_code}: {response_data}")
                self._save_response(endpoint_id, description, response_data)
                return False  # Stop on other errors
                
            # Save successful response
            self._save_response(endpoint_id, description, response_data)
            return True
            
        except Exception as e:
            print(f"💥 Exception collecting {path}: {e}")
            return False
            
    def _save_response(self, endpoint_id: int, description: str, response_data: dict):
        """Save response data to file."""
        filename = f"{endpoint_id}_{description}.json"
        filepath = RESPONSE_DIR / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(response_data, f, indent=2, ensure_ascii=False)
            
        print(f"💾 Saved: {filename}")
        
    def _get_existing_labels(self, response_file: str, label_field: str = "label") -> List[str]:
        """Get labels from existing response files."""
        filepath = RESPONSE_DIR / response_file
        if not filepath.exists():
            return []
            
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                items = data.get("items", [])
                return [item.get(label_field) for item in items if item.get(label_field)]
        except:
            return []


async def main():
    """Main collection routine."""
    print("🚀 Starting OFSC API Response Collection")
    print(f"   Instance: {OFSC_INSTANCE}")
    print(f"   Client ID: {OFSC_CLIENT_ID}")
    print()
    
    async with OFSCResponseCollector() as collector:
        
        # Phase 1: Collect list endpoints
        print("📋 Phase 1: List Endpoints")
        
        # Endpoint #27: Forms
        success = await collector.collect_response(27, "/rest/ofscMetadata/v1/forms", "get_forms")
        if not success:
            print("❌ Stopping due to error on forms endpoint")
            return
            
        # Endpoint #35: Link Templates  
        success = await collector.collect_response(35, "/rest/ofscMetadata/v1/linkTemplates", "get_link_templates")
        if not success:
            print("❌ Stopping due to error on link templates endpoint")
            return
            
        # Endpoint #57: Routing Profiles
        success = await collector.collect_response(57, "/rest/ofscMetadata/v1/routingProfiles", "get_routing_profiles")
        if not success:
            print("❌ Stopping due to error on routing profiles endpoint")
            return
            
        print()
        print("📋 Phase 2: Individual Endpoints with Known Labels")
        
        # Endpoint #64: Individual Shift (use label from existing shifts response)
        shift_labels = collector._get_existing_labels("63_shifts.json", "label")
        if shift_labels:
            shift_label = shift_labels[0]  # Use first available shift
            success = await collector.collect_response(64, f"/rest/ofscMetadata/v1/shifts/{shift_label}", "get_shift")
            if not success:
                print(f"❌ Stopping due to error on individual shift endpoint")
                return
        else:
            print("⚠️  No shift labels found in existing response")
            
        # Endpoint #82: Individual Work Zone (use label from existing workzones response)  
        workzone_labels = collector._get_existing_labels("78_workzones.json", "workZoneLabel")
        if workzone_labels:
            workzone_label = workzone_labels[0]  # Use first available workzone
            success = await collector.collect_response(82, f"/rest/ofscMetadata/v1/workZones/{workzone_label}", "get_workzone")
            if not success:
                print(f"❌ Stopping due to error on individual workzone endpoint")
                return
        else:
            print("⚠️  No workzone labels found in existing response")
            
        print()
        print("📋 Phase 3: Dependent Individual Endpoints")
        
        # Endpoint #36: Individual Link Template (if we got link templates list)
        link_template_labels = collector._get_existing_labels("35_get_link_templates.json", "label")
        if link_template_labels:
            template_label = link_template_labels[0]
            success = await collector.collect_response(36, f"/rest/ofscMetadata/v1/linkTemplates/{template_label}", "get_link_template")
            if not success:
                print(f"❌ Could not get individual link template")
        else:
            print("⚠️  No link template labels available for individual endpoint")
            
        # Endpoint #41: Individual Map Layer (check if any map layers exist)
        map_layer_data = None
        try:
            with open(RESPONSE_DIR / "39_get_custom_map_layers.json", 'r') as f:
                map_layer_data = json.load(f)
        except:
            pass
            
        if map_layer_data and map_layer_data.get("totalResults", 0) > 0:
            map_layer_labels = [item.get("label") for item in map_layer_data.get("items", []) if item.get("label")]
            if map_layer_labels:
                layer_label = map_layer_labels[0]
                success = await collector.collect_response(41, f"/rest/ofscMetadata/v1/mapLayers/{layer_label}", "get_map_layer")
                if not success:
                    print(f"❌ Could not get individual map layer")
        else:
            print("⚠️  No map layers available for individual endpoint (empty collection)")
            
        # Endpoint #58 & #59: Routing Profile Plans (if we got routing profiles)
        routing_profile_labels = collector._get_existing_labels("57_get_routing_profiles.json", "label")
        if routing_profile_labels:
            profile_label = routing_profile_labels[0]
            success = await collector.collect_response(58, f"/rest/ofscMetadata/v1/routingProfiles/{profile_label}/plans", "get_routing_profile_plans")
            if success:
                # Try to get plan export if plans exist
                plan_labels = collector._get_existing_labels("58_get_routing_profile_plans.json", "label")
                if plan_labels:
                    plan_label = plan_labels[0]
                    success = await collector.collect_response(59, f"/rest/ofscMetadata/v1/routingProfiles/{profile_label}/plans/{plan_label}/custom-actions/export", "get_routing_plan_export")
        else:
            print("⚠️  No routing profile labels available for dependent endpoints")
    
    print()
    print("✅ API Response Collection Complete!")
    print("📁 Check response_examples/ directory for collected responses")
    

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Collection interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Collection failed: {e}")
        sys.exit(1)