## OFSC

A simple Python wrapper for Oracle OFS REST API

## Models

Starting with OFS 1.18 we are adding models for the most common entities. All models should be imported from `ofsc.models`

Currently implemented
- Workskill


## Functions implemented



### Core / Activities
    get_activities (self, params, response_type=TEXT_RESPONSE)
    get_activity (self, activity_id, response_type=TEXT_RESPONSE):
    update_activity (self, activity_id, data, response_type=TEXT_RESPONSE)
    move_activity (self, activity_id, data, response_type=TEXT_RESPONSE)
    get_file_property(self, activityId, label, mediaType="application/octet-stream", response_type=FULL_RESPONSE)
    get_all_activities( self, root, date_from, date_to, activity_fields, initial_offset=0, limit=5000)
    search_activities(self, params, response_type=TEXT_RESPONSE)


### Core / Events
    get_subscriptions(self, response_type=TEXT_RESPONSE)
    create_subscription(self, data, response_type=TEXT_RESPONSE)
    delete_subscription(self, subscription_id, response_type=FULL_RESPONSE)
    get_subscription_details(self, subscription_id, response_type=TEXT_RESPONSE)
    get_events(self, params, response_type=TEXT_RESPONSE)

### Core / Resources
    create_resource(self, resourceId, data, response_type=TEXT_RESPONSE)
    get_resource(self, resource_id, inventories=False, workSkills=False, workZones=False, workSchedules=False , response_type=TEXT_RESPONSE)
    get_position_history(self, resource_id,date,response_type=TEXT_RESPONSE)
    get_resource_route(self, resource_id, date, activityFields = None, offset=0, limit=100, response_type=TEXT_RESPONSE)
    get_resource_descendants(self, resource_id,  resourceFields=None, offset=0, limit=100, inventories=False, workSkills=False, workZones=False, workSchedules=False, response_type=TEXT_RESPONSE)

### Core / Users
    get_users(self, offset=0, limit=100, response_type=FULL_RESPONSE)
    get_user(self, login, response_type=FULL_RESPONSE):
    update_user (self, login, data, response_type=TEXT_RESPONSE)
    create_user(self, login, data, response_type=FULL_RESPONSE)
    delete_user(self, login, response_type=FULL_RESPONSE)

### Core / Daily Extract
    get_daily_extract_dates(self, response_type=FULL_RESPONSE)
    get_daily_extract_files(self, date, response_type=FULL_RESPONSE)
    get_daily_extract_file(self, date, filename, response_type=FULL_RESPONSE)

### Metadata / Capacity
    get_capacity_areas (self, expand="parent", fields=capacityAreasFields, status="active", queryType="area", response_type=FULL_RESPONSE)
    get_capacity_area (self,label, response_type=FULL_RESPONSE)

### Metadata / Activity Types
    get_activity_type_groups (self, expand="parent", offset=0, limit=100, response_type=FULL_RESPONSE)
    get_activity_type_group (self,label, response_type=FULL_RESPONSE)   
    get_activity_types(self, offset=0, limit=100, response_type=FULL_RESPONSE)
    get_activity_type (self, label, response_type=FULL_RESPONSE)

### Metadata / properties
    get_properties (self, offset=0, limit=100, response_type=FULL_RESPONSE)
     get_all_properties(self, initial_offset=0, limit=100)

### Metadata / workskills
    get_workskills (self, offset=0, limit=100, response_type=FULL_RESPONSE)
    get_workskill(self, label: str, response_type=FULL_RESPONSE)
    create_or_update_workskill(self, skill: Workskill, response_type=FULL_RESPONSE)


## Test History

OFS REST API Version | PyOFSC
------------ | -------------
20C| 1.7
21A| 1.8, 1.8,1, 1.9
21D| 1.15
22B| 1.16, 1.17

## Deprecation Warning

Starting in OFSC 2.0  (estimated for December 2022) all functions will have to be called using the API name (Core or Metadata). See the examples.

Instead of

    instance = OFSC(..)
    list_of_activities = instance.get_activities(...)

It will be required to use the right API module:

    instance = OFSC(..)
    list_of_activites = instance.core.get_activities(...)

During the transition period a DeprecationWarning will be raised if the functions are used in the old way