import requests
import base64
import json
import urllib
from urllib.parse import urljoin
TEXT_RESPONSE=1
FULL_RESPONSE=2
JSON_RESPONSE=3

class OFSC:

    API_PORTAL = "https://api.etadirect.com"

    def __init__    (self, clientID, companyName, secret, baseUrl=API_PORTAL):
        self.headers ={}
        self.clientID = clientID
        self.companyName = companyName
        self.baseUrl = baseUrl
        # Calculate Authorization
        mypass = base64.b64encode(bytes(clientID+"@"+companyName+":"+secret, 'utf-8'))
        self.headers["Authorization"] = "Basic "+mypass.decode('utf-8')



    # OFSC Function Library
    def get_activities (self, params, response_type=TEXT_RESPONSE):
        url = urljoin(self.baseUrl, "/rest/ofscCore/v1/activities")
        response = requests.get(url, headers=self.headers, params=params)
        if response_type==FULL_RESPONSE:
            return response
        elif response_type==JSON_RESPONSE:
            return response.json()
        else:
            return response.text

    def get_activity (self, activity_id, response_type=TEXT_RESPONSE):
        url = urljoin(self.baseUrl, "/rest/ofscCore/v1/activities/{}".format(activity_id))
        response = requests.get(url, headers=self.headers)
        #print (response.status_code)
        if response_type==FULL_RESPONSE:
            return response
        elif response_type==JSON_RESPONSE:
            return response.json()
        else:
            return response.text

    def update_activity (self, activity_id, data, response_type=TEXT_RESPONSE):
        url = urljoin(self.baseUrl, "/rest/ofscCore/v1/activities/{}".format(activity_id))
        response = requests.patch(url, headers=self.headers, data=data)
        #print (response.status_code)
        if response_type==FULL_RESPONSE:
            return response
        elif response_type==JSON_RESPONSE:
            return response.json()
        else:
            return response.text

    def move_activity (self, activity_id, data, response_type=TEXT_RESPONSE):
        url = urljoin(self.baseUrl, "/rest/ofscCore/v1/activities/{}/custom-actions/move".format(activity_id))
        response = requests.post(url, headers=self.headers, data=data)
        #print (response.status_code)
        if response_type==FULL_RESPONSE:
            return response
        elif response_type==JSON_RESPONSE:
            return response.json()
        else:
            return response.text

    def get_subscriptions(self, response_type=TEXT_RESPONSE):
        url = urljoin(self.baseUrl, "/rest/ofscCore/v1/events/subscriptions")
        response = requests.get(url, headers=self.headers)
        if response_type==FULL_RESPONSE:
            return response
        elif response_type==JSON_RESPONSE:
            return response.json()
        else:
            return response.text

    def create_subscription(self, data, response_type=TEXT_RESPONSE):
        url = urljoin(self.baseUrl, "/rest/ofscCore/v1/events/subscriptions")
        response = requests.post(url, headers=self.headers, data = data)
        if response_type==FULL_RESPONSE:
            return response
        elif response_type==JSON_RESPONSE:
            return response.json()
        else:
            return response.text

    def get_subscription_details(self, subscription_id, response_type=TEXT_RESPONSE):
        url = urljoin(self.baseUrl, "/rest/ofscCore/v1/events/subscriptions/{}".format(str(subscription_id)))
        response = requests.get(url, headers=self.headers)
        if response_type==FULL_RESPONSE:
            return response
        elif response_type==JSON_RESPONSE:
            return response.json()
        else:
            return response.text

    def get_events(self, params, response_type=TEXT_RESPONSE):
        url = urljoin(self.baseUrl, "rest/ofscCore/v1/events")
        response = requests.get('https://api.etadirect.com/rest/ofscCore/v1/events', headers=self.headers, params=params)
        if response_type==FULL_RESPONSE:
            return response
        elif response_type==JSON_RESPONSE:
            return response.json()
        else:
            return response.text

    def get_resource(self, resource_id, inventories=False, workSkills=False, workZones=False, workSchedules=False , response_type=TEXT_RESPONSE):
        url = urljoin(self.baseUrl, "/rest/ofscCore/v1/resources/{}".format(str(resource_id)))
        data = {}
        expand = ""
        if inventories:
            expand = "inventories"
        if workSkills:
            if len(expand) > 0:
                expand = "{},workSkills".format(expand)
            else:
                expand = "workSkills"
        if workZones:
            if len(expand) > 0:
                expand = "{},workZones".format(expand)
            else:
                expand = "workZones"
        if workSchedules:
            if len(expand) > 0:
                expand = "{},workSchedules".format(expand)
            else:
                expand = "workSchedules"

        if len(expand) > 0:
            data['expand'] = expand

        response = requests.get(url, params=data, headers=self.headers)

        if response_type==FULL_RESPONSE:
            return response
        elif response_type==JSON_RESPONSE:
            return response.json()
        else:
            return response.text

    def get_position_history(self, resource_id,date,response_type=TEXT_RESPONSE):
        url = urljoin(self.baseUrl, "/rest/ofscCore/v1/resources/{}/positionHistory".format(str(resource_id)))
        params = {}
        params['date'] = date
        response = requests.get(url, params=params, headers=self.headers)

        if response_type==FULL_RESPONSE:
            return response
        elif response_type==JSON_RESPONSE:
            return response.json()
        else:
            return response.text

    def get_resource_route(self, resource_id, date, activityFields = None, offset=0, limit=100, response_type=TEXT_RESPONSE):
        url = urljoin(self.baseUrl, "/rest/ofscCore/v1/resources/{}/routes/{}".format(str(resource_id), date))
        params = {}
        if activityFields is not None:
            params['activityFields'] = activityFields
        response = requests.get(url, params=params, headers=self.headers)

        if response_type==FULL_RESPONSE:
            return response
        elif response_type==JSON_RESPONSE:
            return response.json()
        else:
            return response.text

    def get_resource_descendants(self, resource_id,  resourceFields=None, offset=0, limit=100, inventories=False, workSkills=False, workZones=False, workSchedules=False , response_type=TEXT_RESPONSE):
        url = urljoin(self.baseUrl, "/rest/ofscCore/v1/resources/{}/descendants".format(str(resource_id)))
        # Calculate expand
        params = {}
        expand = ""
        if inventories:
            expand = "inventories"
        if workSkills:
            if len(expand) > 0:
                expand = "{},workSkills".format(expand)
            else:
                expand = "workSkills"
        if workZones:
            if len(expand) > 0:
                expand = "{},workZones".format(expand)
            else:
                expand = "workZones"
        if workSchedules:
            if len(expand) > 0:
                expand = "{},workSchedules".format(expand)
            else:
                expand = "workSchedules"

        if len(expand) > 0:
            params['expand'] = expand

        if resourceFields is not None:
            params['fields'] = resourceFields
        params['limit'] = limit
        params['offset']= offset

        response = requests.get(url, params=params, headers=self.headers)

        if response_type==FULL_RESPONSE:
            return response
        elif response_type==JSON_RESPONSE:
            return response.json()
        else:
            return response.text

    capacityAreasFields= "label,name,type,status,parent.name,parent.label"
    additionalCapacityFields = ['parentLabel', 'configuration.isTimeSlotBase',"configuration.byCapacityCategory", "configuration.byDay", 'configuration.byTimeSlot', 'configuration.isAllowCloseOnWorkzoneLevel', 'configuration.definitionLevel.day', 'configuration.definitionLevel.timeSlot', 'configuration.definitionLevel.capacityCategory']
    capacityHeaders = capacityAreasFields.split(",")+additionalCapacityFields

    def get_capacity_areas (self, expand="parent", fields=capacityAreasFields, status="active", queryType="area", response_type=FULL_RESPONSE):
        url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/capacityAreas")
        params = {}
        params["expand"] = expand
        params["fields"] = fields
        params["status"] = status
        params["type"] = queryType
        response = requests.get(url, params = params, headers=self.headers)
        if response_type==FULL_RESPONSE:
            return response
        elif response_type==JSON_RESPONSE:
            return response.json()
        else:
            return response.text

    def get_capacity_area (self,label, response_type=FULL_RESPONSE):
        encoded_label = urllib.parse.quote_plus(label)
        url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/capacityAreas/{}".format(encoded_label))
        response = requests.get(url, headers=self.headers)
        if response_type==FULL_RESPONSE:
            return response
        elif response_type==JSON_RESPONSE:
            return response.json()
        else:
            return response.text
    
    def get_activity_type_groups(self, offset=0, limit=100, response_type=FULL_RESPONSE):
        url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/activityTypeGroups")
        response = requests.get(url, headers=self.headers)
        if response_type==FULL_RESPONSE:
            return response
        elif response_type==JSON_RESPONSE:
            return response.json()
        else:
            return response.text

    def get_activity_type_group(self, label, response_type=FULL_RESPONSE):
        encoded_label = urllib.parse.quote_plus(label)
        url = urljoin(self.baseUrl, "/rest/ofscMetadata/v1/activityTypeGroups/{}".format(encoded_label))
        response = requests.get(url, headers=self.headers)
        if response_type==FULL_RESPONSE:
            return response
        elif response_type==JSON_RESPONSE:
            return response.json()
        else:
            return response.text

    ## 202104 User Management
    def get_users(self, offset=0, limit=100, response_type=FULL_RESPONSE):
        url = urljoin(self.baseUrl, "/rest/ofscCore/v1/users")
        params = {}
        params["offset"]= offset
        params["limit"]= limit
        response = requests.get(url, params, headers=self.headers)
        if response_type==FULL_RESPONSE:
            return response
        elif response_type==JSON_RESPONSE:
            return response.json()
        else:
            return response.text

    def get_user(self, login, response_type=FULL_RESPONSE):
        url = urljoin(self.baseUrl, "/rest/ofscCore/v1/users/{}".format(login))
        response = requests.get(url, headers=self.headers)
        if response_type==FULL_RESPONSE:
            return response
        elif response_type==JSON_RESPONSE:
            return response.json()
        else:
            return response.text

    def update_user (self, login, data, response_type=FULL_RESPONSE):
        url = urljoin(self.baseUrl, "/rest/ofscCore/v1/users/{}".format(login))
        response = requests.patch(url, headers=self.headers, data=data)
        #print (response.status_code)
        if response_type==FULL_RESPONSE:
            return response
        elif response_type==JSON_RESPONSE:
            return response.json()
        else:
            return response.text

    ##202106
    def create_user (self, login, data, response_type=FULL_RESPONSE):
        url = urljoin(self.baseUrl, f"/rest/ofscCore/v1/users/{login}")
        response = requests.put(url, headers=self.headers, data=data)
        #print (response.status_code)
        if response_type==FULL_RESPONSE:
            return response
        elif response_type==JSON_RESPONSE:
            return response.json()
        else:
            return response.text

    ##202106 
    def delete_user(self, login, response_type=FULL_RESPONSE):
        url = urljoin(self.baseUrl, f"/rest/ofscCore/v1/users/{login}")
        response = requests.delete(url, headers=self.headers)
        if response_type==FULL_RESPONSE:
            return response
        elif response_type==JSON_RESPONSE:
            return response.json()
        else:
            return response.text

    ##202105 Daily Extract - NOT TESTED
    def get_daily_extract_dates(self, response_type=FULL_RESPONSE):
        url = urljoin(self.baseUrl, "/rest/ofscCore/v1/folders/dailyExtract/folders/")
        response = requests.get(url, headers=self.headers)
        if response_type==FULL_RESPONSE:
            return response
        elif response_type==JSON_RESPONSE:
            return response.json()
        else:
            return response.text   

    ##202105 Daily Extract - NOT TESTED   
    def get_daily_extract_files(self, date, response_type=FULL_RESPONSE):
        url = urljoin(self.baseUrl, "/rest/ofscCore/v1/folders/dailyExtract/folders/{}/files".format(date))
        response = requests.get(url, headers=self.headers)
        if response_type==FULL_RESPONSE:
            return response
        elif response_type==JSON_RESPONSE:
            return response.json()
        else:
            return response.text       
            
    ##202105 Daily Extract - NOT TESTED
    def get_daily_extract_file(self, date, filename, response_type=FULL_RESPONSE):
        url = urljoin(self.baseUrl, "/rest/ofscCore/v1/folders/dailyExtract/folders/{}/files/{}".format(date, filename))
        response = requests.get(url, headers=self.headers)
        if response_type==FULL_RESPONSE:
            return response
        elif response_type==JSON_RESPONSE:
            return response.json()
        else:
            return response.text