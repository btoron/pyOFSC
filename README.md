## OFSC

A simple Python wrapper for Oracle OFS REST API

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

### Daily Extract
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

## Test History

OFS REST API Version | PyOFSC
------------ | -------------
20C| 1.7
21A| 1.8, 1.8,1, 1.9
21D| 1.15
22B| 1.16

