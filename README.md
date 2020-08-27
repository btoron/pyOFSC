    ## Functions implemented

    def get_activities (self, params, response_type=TEXT_RESPONSE):
    def get_activity (self, activity_id, response_type=TEXT_RESPONSE):
    def update_activity (self, activity_id, data, response_type=TEXT_RESPONSE):
    def move_activity (self, activity_id, data, response_type=TEXT_RESPONSE):
    def get_subscriptions(self, response_type=TEXT_RESPONSE):
    def create_subscription(self, data, response_type=TEXT_RESPONSE):
    def get_subscription_details(self, subscription_id, response_type=TEXT_RESPONSE):
    def get_events(self, params, response_type=TEXT_RESPONSE):
    def get_resource(self, resource_id, inventories=False, workSkills=False, workZones=False, workSchedules=False , response_type=TEXT_RESPONSE):
    def get_position_history(self, resource_id,date,response_type=TEXT_RESPONSE):
    def get_resource_route(self, resource_id, date, activityFields = None, offset=0, limit=100, response_type=TEXT_RESPONSE):
    def get_resource_descendants(self, resource_id,  resourceFields=None, offset=0, limit=100, inventories=False, workSkills=False, workZones=False, workSchedules=False , response_type=TEXT_RESPONSE):

    additionalCapacityFields = ['parentLabel', 'configuration.isTimeSlotBase',"configuration.byCapacityCategory", "configuration.byDay", 'configuration.byTimeSlot', 'configuration.isAllowCloseOnWorkzoneLevel', 'configuration.definitionLevel.day', 'configuration.definitionLevel.timeSlot', 'configuration.definitionLevel.capacityCategory']
    def get_capacity_areas (self, expand="parent", fields=capacityAreasFields, status="active", queryType="area", response_type=FULL_RESPONSE):
    def get_capacity_area (self,label, response_type=FULL_RESPONSE):
