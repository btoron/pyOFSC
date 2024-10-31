## OFSC

A simple Python wrapper for Oracle OFS REST API

## Models

Starting with OFS 1.17 we added models for the most common entities and metadata. All models should be imported from `ofsc.models`. All existing create functions will be eventually transitioned to models.

The models are based on the Pydantic BaseModel, so it is possible to build an entity using the `model_validate` static methods.

Currently implemented:
- ActivityTypeGroup
- ActivityType
- CapacityArea
- CapacityCategory
- InventoryType
- Property
- Workskill
- WorkSkillCondition
- WorkSkillGroup
- Workzone


Experimental:
- Resource
- ResourceType
- User

## Functions implemented



### Core / Activities
    get_activities (self, params, response_type=TEXT_RESPONSE)
    get_activity (self, activity_id, response_type=TEXT_RESPONSE):
    update_activity (self, activity_id, data, response_type=TEXT_RESPONSE)
    move_activity (self, activity_id, data, response_type=TEXT_RESPONSE)
    get_file_property(self, activityId, label, mediaType="application/octet-stream", response_type=FULL_RESPONSE)
    get_all_activities( self, root, date_from, date_to, activity_fields, initial_offset=0, limit=5000)
    search_activities(self, params, response_type=TEXT_RESPONSE)
    bulk_update(self, data:BulkUpdateRequest, response_type=OBJ_RESPONSE)


### Core / Events
    get_subscriptions(self, response_type=OBJ_RESPONSE)
    create_subscription(self, data, response_type=OBJ_RESPONSE)
    delete_subscription(self, subscription_id, response_type=OBJ_RESPONSE)
    get_subscription_details(self, subscription_id, response_type=OBJ_RESPONSE)
    get_events(self, params, response_type=OBJ_RESPONSE)

### Core / Resources
    create_resource(self, resourceId, data, response_type=OBJ_RESPONSE)
    get_resource(self, resource_id, inventories=False, workSkills=False, workZones=False, workSchedules=False , response_type=OBJ_RESPONSE)
    get_position_history(self, resource_id,date,response_type=OBJ_RESPONSE)
    get_resource_route(self, resource_id, date, activityFields = None, offset=0, limit=100, response_type=OBJ_RESPONSE)
    get_resource_descendants(self, resource_id,  resourceFields=None, offset=0, limit=100, inventories=False, workSkills=False, workZones=False, workSchedules=False, response_type=OBJ_RESPONSE)

### Core / Users
    get_users(self, offset=0, limit=100, response_type=OBJ_RESPONSE)
    get_user(self, login, response_type=OBJ_RESPONSE):
    update_user (self, login, data, response_type=OBJ_RESPONSE)
    create_user(self, login, data, response_type=OBJ_RESPONSE)
    delete_user(self, login, response_type=OBJ_RESPONSE)

### Core / Daily Extract
    get_daily_extract_dates(self, response_type=OBJ_RESPONSE)
    get_daily_extract_files(self, date, response_type=OBJ_RESPONSE)
    get_daily_extract_file(self, date, filename, response_type=OBJ_RESPONSE)
\
### Metadata / Activity Type Groups
    get_activity_type_groups (self, expand="parent", offset=0, limit=100, response_type=OBJ_RESPONSE)
    get_activity_type_group (self,label, response_type=OBJ_RESPONSE)   

### Metadata / Activity Types
    get_activity_types(self, offset=0, limit=100, response_type=OBJ_RESPONSE)
    get_activity_type (self, label, response_type=OBJ_RESPONSE)

### Metadata / Capacity
    get_capacity_areas (self, expand="parent", fields=capacityAreasFields, status="active", queryType="area", response_type=OBJ_RESPONSE)
    get_capacity_area (self,label, response_type=OBJ_RESPONSE)

### Metadata / Inventory
    get_inventory_types (self, offset=0, limit=100, response_type=OBJ_RESPONSE)
    get_inventory_type (self, label, response_type=OBJ_RESPONSE)
    create_or_replace_inventory_type(self, inventory: InventoryType, response_type=OBJ_RESPONSE)

### Metadata / Properties
    get_properties (self, offset=0, limit=100, response_type=OBJ_RESPONSE)
    get_property(self, label: str, response_type=OBJ_RESPONSE)
    create_or_replace_property(self, property: Property, response_type=OBJ_RESPONSE)

### Metadata / Workskills
    get_workskills (self, offset=0, limit=100, response_type=OBJ_RESPONSE)
    get_workskill(self, label: str, response_type=OBJ_RESPONSE)
    create_or_update_workskill(self, skill: Workskill, response_type=OBJ_RESPONSE)
    delete_workskill(self, label: str, response_type=OBJ_RESPONSE)
    get_workskill_conditions(self, response_type=OBJ_RESPONSE)
    replace_workskill_conditions(self, data: WorskillConditionList, response_type=OBJ_RESPONSE)
    get_workskill_groups(self, response_type=OBJ_RESPONSE)
    get_workskill_group(self, label: str, response_type=OBJ_RESPONSE)
    create_or_update_workskill_group(self, group: WorkSkillGroup, response_type=OBJ_RESPONSE)
    delete_workskill_group(self, label: str, response_type=OBJ_RESPONSE)

### Metadata / Plugins
    import_plugin(self, plugin: str)
    import_plugin_file(self, plugin: Path)

### Metadata / Resource Types
    get_resource_types(self, response_type=OBJ_RESPONSE):

### Metadata / Workzones
    get_workzones(self, response_type=OBJ_RESPONSE)
    
## Test History

OFS REST API Version | PyOFSC
------------ | -------------
20C| 1.7
21A| 1.8, 1.8,1, 1.9
21D| 1.15
22B| 1.16, 1.17
22D| 1.18
24C| 2.0

## Deprecation Warning

Starting in OFSC 2.0  all functions are called using the API name (Core or Metadata). See the examples.

Instead of

    instance = OFSC(..)
    list_of_activities = instance.get_activities(...)

It will be required to use the right API module:

    instance = OFSC(..)
    list_of_activites = instance.core.get_activities(...)

During the transition period a DeprecationWarning will be raised if the functions are used in the old way

## What's new in OFSC 2.0

- All metadata functions now use models, when available
- All functions are now using the API name (Core or Metadata)
- All functions return a python object by default. If there is an available model it will be used, otherwise a dict will be returned (see `response_type` parameter and `auto_model` parameter)
- Errors during API calls can raise exceptions and will by default when returning an object (see `auto_raise` parameter)
- OBJ_RESPONS and TEXT_RESPONSE are now deprecated. Use `response_type` parameter to control the response type