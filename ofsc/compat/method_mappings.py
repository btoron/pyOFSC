"""API method mappings for backward compatibility wrapper.

This module defines all the API methods that need to be wrapped for backward compatibility,
including their parameters, defaults, and expected behavior.
"""

from typing import Dict, Any

# Core API Methods Mapping
CORE_METHODS = {
    # User Management
    "get_users": {
        "params": ["offset", "limit"],
        "defaults": {"offset": 0, "limit": 100},
        "doc": "Get users from the OFS Core API",
    },
    "get_user": {
        "params": ["login"],
        "defaults": {},
        "doc": "Get single user by login",
    },
    "create_user": {
        "params": ["login", "data"],
        "defaults": {},
        "doc": "Create a new user",
    },
    "update_user": {
        "params": ["login", "data"],
        "defaults": {},
        "doc": "Update existing user",
    },
    "delete_user": {"params": ["login"], "defaults": {}, "doc": "Delete user by login"},
    # Activity Management
    "get_activities": {
        "params": ["params"],
        "defaults": {},
        "doc": "Get activities with search parameters",
    },
    "get_activity": {
        "params": ["activity_id"],
        "defaults": {},
        "doc": "Get single activity by ID",
    },
    "update_activity": {
        "params": ["activity_id", "data"],
        "defaults": {},
        "doc": "Update activity data",
    },
    "move_activity": {
        "params": ["activity_id", "data"],
        "defaults": {},
        "doc": "Move activity to different resource/time",
    },
    "search_activities": {
        "params": ["params"],
        "defaults": {},
        "doc": "Search activities with parameters",
    },
    "bulk_update": {
        "params": ["data"],
        "defaults": {},
        "doc": "Bulk update activities",
    },
    # Events & Subscriptions
    "get_subscriptions": {
        "params": ["allSubscriptions"],
        "defaults": {"allSubscriptions": False},
        "doc": "Get event subscriptions",
    },
    "create_subscription": {
        "params": ["data"],
        "defaults": {},
        "doc": "Create event subscription",
    },
    "delete_subscription": {
        "params": ["subscription_id"],
        "defaults": {},
        "doc": "Delete event subscription",
    },
    "get_subscription_details": {
        "params": ["subscription_id"],
        "defaults": {},
        "doc": "Get subscription details",
    },
    "get_events": {
        "params": ["params"],
        "defaults": {},
        "doc": "Get events with parameters",
    },
    # Resource Management
    "get_resource": {
        "params": [
            "resource_id",
            "inventories",
            "workSkills",
            "workZones",
            "workSchedules",
        ],
        "defaults": {
            "inventories": False,
            "workSkills": False,
            "workZones": False,
            "workSchedules": False,
        },
        "doc": "Get resource details",
    },
    "create_resource": {
        "params": ["resourceId", "data"],
        "defaults": {},
        "doc": "Create new resource",
    },
    "update_resource": {
        "params": ["resourceId", "data", "identify_by_internal_id"],
        "defaults": {"identify_by_internal_id": False},
        "doc": "Update resource data",
    },
    "get_position_history": {
        "params": ["resource_id", "date"],
        "defaults": {},
        "doc": "Get resource position history",
    },
    "get_resource_route": {
        "params": ["resource_id", "date", "activityFields", "offset", "limit"],
        "defaults": {"activityFields": None, "offset": 0, "limit": 100},
        "doc": "Get resource route for date",
    },
    "get_resource_descendants": {
        "params": [
            "resource_id",
            "resourceFields",
            "offset",
            "limit",
            "inventories",
            "workSkills",
            "workZones",
            "workSchedules",
        ],
        "defaults": {
            "resourceFields": None,
            "offset": 0,
            "limit": 100,
            "inventories": False,
            "workSkills": False,
            "workZones": False,
            "workSchedules": False,
        },
        "doc": "Get resource descendants",
    },
    # Daily Extract
    "get_daily_extract_dates": {
        "params": [],
        "defaults": {},
        "doc": "Get available daily extract dates",
    },
    "get_daily_extract_files": {
        "params": ["date"],
        "defaults": {},
        "doc": "Get daily extract files for date",
    },
    "get_daily_extract_file": {
        "params": ["date", "filename"],
        "defaults": {},
        "doc": "Download daily extract file",
    },
}

# Metadata API Methods Mapping
METADATA_METHODS = {
    # Properties
    "get_properties": {
        "params": ["offset", "limit"],
        "defaults": {"offset": 0, "limit": 100},
        "doc": "Get properties list",
    },
    "get_property": {
        "params": ["label"],
        "defaults": {},
        "doc": "Get single property by label",
    },
    "create_or_replace_property": {
        "params": ["property"],
        "defaults": {},
        "doc": "Create or replace property",
    },
    "get_enumeration_values": {
        "params": ["label", "offset", "limit"],
        "defaults": {"offset": 0, "limit": 100},
        "doc": "Get enumeration values for property",
    },
    # Work Skills
    "get_workskills": {
        "params": ["offset", "limit"],
        "defaults": {"offset": 0, "limit": 100},
        "doc": "Get work skills list",
    },
    "get_workskill": {
        "params": ["label"],
        "defaults": {},
        "doc": "Get single work skill by label",
    },
    "create_or_update_workskill": {
        "params": ["skill"],
        "defaults": {},
        "doc": "Create or update work skill",
    },
    "delete_workskill": {
        "params": ["label"],
        "defaults": {},
        "doc": "Delete work skill",
    },
    "get_workskill_conditions": {
        "params": [],
        "defaults": {},
        "doc": "Get work skill conditions",
    },
    "get_workskill_groups": {
        "params": [],
        "defaults": {},
        "doc": "Get work skill groups",
    },
    "get_workskill_group": {
        "params": ["label"],
        "defaults": {},
        "doc": "Get work skill group by label",
    },
    # Activity Types
    "get_activity_types": {
        "params": ["offset", "limit"],
        "defaults": {"offset": 0, "limit": 100},
        "doc": "Get activity types list",
    },
    "get_activity_type": {
        "params": ["label"],
        "defaults": {},
        "doc": "Get activity type by label",
    },
    "get_activity_type_groups": {
        "params": ["expand", "offset", "limit"],
        "defaults": {"expand": "parent", "offset": 0, "limit": 100},
        "doc": "Get activity type groups",
    },
    "get_activity_type_group": {
        "params": ["label"],
        "defaults": {},
        "doc": "Get activity type group by label",
    },
    # Capacity
    "get_capacity_areas": {
        "params": ["expandParent", "fields", "activeOnly", "areasOnly"],
        "defaults": {
            "expandParent": False,
            "fields": ["label"],
            "activeOnly": False,
            "areasOnly": False,
        },
        "doc": "Get capacity areas",
    },
    "get_capacity_area": {
        "params": ["label"],
        "defaults": {},
        "doc": "Get capacity area by label",
    },
    "get_capacity_categories": {
        "params": ["offset", "limit"],
        "defaults": {"offset": 0, "limit": 100},
        "doc": "Get capacity categories",
    },
    "get_capacity_category": {
        "params": ["label"],
        "defaults": {},
        "doc": "Get capacity category by label",
    },
    # Inventory
    "get_inventory_types": {"params": [], "defaults": {}, "doc": "Get inventory types"},
    "get_inventory_type": {
        "params": ["label"],
        "defaults": {},
        "doc": "Get inventory type by label",
    },
    # Resource Types
    "get_resource_types": {"params": [], "defaults": {}, "doc": "Get resource types"},
    # Work Zones
    "get_workzones": {
        "params": ["offset", "limit"],
        "defaults": {"offset": 0, "limit": 100},
        "doc": "Get work zones",
    },
    # Applications
    "get_applications": {"params": [], "defaults": {}, "doc": "Get applications"},
    "get_application": {
        "params": ["label"],
        "defaults": {},
        "doc": "Get application by label",
    },
    "get_application_api_accesses": {
        "params": ["label"],
        "defaults": {},
        "doc": "Get application API accesses",
    },
    "get_application_api_access": {
        "params": ["label", "accessId"],
        "defaults": {},
        "doc": "Get application API access",
    },
    # Organizations
    "get_organizations": {"params": [], "defaults": {}, "doc": "Get organizations"},
    "get_organization": {
        "params": ["label"],
        "defaults": {},
        "doc": "Get organization by label",
    },
}

# Capacity API Methods (if implemented)
CAPACITY_METHODS = {
    "getAvailableCapacity": {
        "params": [
            "dates",
            "areas",
            "categories",
            "aggregateResults",
            "availableTimeIntervals",
            "calendarTimeIntervals",
            "fields",
        ],
        "defaults": {
            "categories": None,
            "aggregateResults": None,
            "availableTimeIntervals": "all",
            "calendarTimeIntervals": "all",
            "fields": None,
        },
        "doc": "Get available capacity",
    },
    "getQuota": {
        "params": [
            "dates",
            "areas",
            "categories",
            "aggregateResults",
            "categoryLevel",
            "intervalLevel",
            "returnStatuses",
            "timeSlotLevel",
        ],
        "defaults": {
            "areas": None,
            "categories": None,
            "aggregateResults": None,
            "categoryLevel": None,
            "intervalLevel": None,
            "returnStatuses": None,
            "timeSlotLevel": None,
        },
        "doc": "Get quota information",
    },
}


def get_all_methods() -> Dict[str, Dict[str, Any]]:
    """Get all method mappings organized by API."""
    return {
        "core": CORE_METHODS,
        "metadata": METADATA_METHODS,
        "capacity": CAPACITY_METHODS,
    }
