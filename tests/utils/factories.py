"""Factory functions for creating test data."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional


def create_test_translation(locale: str = "en", value: str = "Test") -> Dict[str, str]:
    """Create a test translation object.
    
    Args:
        locale: Language locale (default: "en")
        value: Translation value (default: "Test")
        
    Returns:
        Translation dictionary
    """
    return {"locale": locale, "value": value}


def create_test_user(
    login: str = "test_user",
    name: str = "Test User",
    status: str = "active",
    **kwargs
) -> Dict[str, Any]:
    """Create a test user object.
    
    Args:
        login: User login (default: "test_user")
        name: User name (default: "Test User")
        status: User status (default: "active")
        **kwargs: Additional user fields
        
    Returns:
        User dictionary
    """
    user = {
        "login": login,
        "name": name,
        "status": status,
        "userType": kwargs.get("userType", "technician"),
        "language": kwargs.get("language", "en"),
        "timeZone": kwargs.get("timeZone", "UTC"),
        "dateFormat": kwargs.get("dateFormat", "mm/dd/yyyy"),
        "timeFormat": kwargs.get("timeFormat", "12-hour"),
    }
    user.update(kwargs)
    return user


def create_test_resource(
    resourceId: str = "test_resource",
    name: str = "Test Resource",
    status: str = "active",
    resourceType: str = "FT",
    **kwargs
) -> Dict[str, Any]:
    """Create a test resource object.
    
    Args:
        resourceId: Resource ID (default: "test_resource")
        name: Resource name (default: "Test Resource")
        status: Resource status (default: "active") 
        resourceType: Resource type (default: "FT")
        **kwargs: Additional resource fields
        
    Returns:
        Resource dictionary
    """
    resource = {
        "resourceId": resourceId,
        "name": name,
        "status": status,
        "resourceType": resourceType,
        "timeZone": kwargs.get("timeZone", "UTC"),
        "dateFormat": kwargs.get("dateFormat", "mm/dd/yyyy"),
        "timeFormat": kwargs.get("timeFormat", "12-hour"),
    }
    resource.update(kwargs)
    return resource


def create_test_activity(
    activityId: str = "test_activity",
    activityType: str = "install",
    status: str = "pending",
    **kwargs
) -> Dict[str, Any]:
    """Create a test activity object.
    
    Args:
        activityId: Activity ID (default: "test_activity")
        activityType: Activity type (default: "install")
        status: Activity status (default: "pending")
        **kwargs: Additional activity fields
        
    Returns:
        Activity dictionary
    """
    activity = {
        "activityId": activityId,
        "activityType": activityType,
        "status": status,
        "duration": kwargs.get("duration", 60),
        "date": kwargs.get("date", datetime.now(timezone.utc).strftime("%Y-%m-%d")),
        "resourceId": kwargs.get("resourceId", "test_resource"),
    }
    activity.update(kwargs)
    return activity


def create_test_property(
    label: str = "test_property",
    name: str = "Test Property",
    entity: str = "activity",
    type: str = "string",
    **kwargs
) -> Dict[str, Any]:
    """Create a test property object.
    
    Args:
        label: Property label (default: "test_property")
        name: Property name (default: "Test Property")
        entity: Entity type (default: "activity")
        type: Property type (default: "string")
        **kwargs: Additional property fields
        
    Returns:
        Property dictionary
    """
    prop = {
        "label": label,
        "name": name,
        "entity": entity,
        "type": type,
        "gui": kwargs.get("gui", "text"),
        "translations": kwargs.get("translations", [
            create_test_translation("en", name)
        ]),
    }
    prop.update(kwargs)
    return prop


def create_test_workskill(
    label: str = "test_skill",
    name: str = "Test Skill",
    sharing: str = "maximal",
    **kwargs
) -> Dict[str, Any]:
    """Create a test work skill object.
    
    Args:
        label: Skill label (default: "test_skill")
        name: Skill name (default: "Test Skill")
        sharing: Sharing type (default: "maximal")
        **kwargs: Additional skill fields
        
    Returns:
        Work skill dictionary
    """
    skill = {
        "label": label,
        "name": name,
        "sharing": sharing,
        "translations": kwargs.get("translations", [
            create_test_translation("en", name)
        ]),
    }
    skill.update(kwargs)
    return skill


def create_test_capacity_area(
    label: str = "test_area",
    name: str = "Test Area",
    parent: Optional[str] = None,
    status: str = "active",
    **kwargs
) -> Dict[str, Any]:
    """Create a test capacity area object.
    
    Args:
        label: Area label (default: "test_area")
        name: Area name (default: "Test Area")
        parent: Parent area label (optional)
        status: Area status (default: "active")
        **kwargs: Additional area fields
        
    Returns:
        Capacity area dictionary
    """
    area = {
        "label": label,
        "name": name,
        "status": status,
        "configuration": kwargs.get("configuration", {
            "isTimeSlotBase": True,
            "isWorkZoneBase": True,
            "timeSlotDuration": 2
        }),
    }
    if parent:
        area["parent"] = parent
    area.update(kwargs)
    return area