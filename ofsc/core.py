import requests
import base64
import json

TEXT_RESPONSE=1
FULL_RESPONSE=2
JSON_RESPONSE=3

class OFSC:


    def __init__    (self, clientID, companyName, secret):
        self.headers ={}
        self.clientID = clientID
        self.companyName = companyName
        # Calculate Authorization
        mypass = base64.b64encode(bytes(clientID+"@"+companyName+":"+secret, 'utf-8'))
        self.headers["Authorization"] = "Basic "+mypass.decode('utf-8')



    # OFSC Function Library
    def get_activities (self, params, response_type=TEXT_RESPONSE):
        response = requests.get('https://api.etadirect.com/rest/ofscCore/v1/activities', headers=self.headers, params=params)
        if response_type==FULL_RESPONSE:
            return response
        elif response_type==JSON_RESPONSE:
            return response.json()
        else:
            return response.text

    def get_activity (self, activity_id, response_type=TEXT_RESPONSE):
        response = requests.get('https://api.etadirect.com/rest/ofscCore/v1/activities/' + str(activity_id), headers=self.headers)
        #print (response.status_code)
        if response_type==FULL_RESPONSE:
            return response
        elif response_type==JSON_RESPONSE:
            return response.json()
        else:
            return response.text

    def update_activity (self, activity_id, data, response_type=TEXT_RESPONSE):
        response = requests.patch('https://api.etadirect.com/rest/ofscCore/v1/activities/' + str(activity_id), headers=self.headers, data=data)
        #print (response.status_code)
        if response_type==FULL_RESPONSE:
            return response
        elif response_type==JSON_RESPONSE:
            return response.json()
        else:
            return response.text

    def move_activity (self, activity_id, data, response_type=TEXT_RESPONSE):
        response = requests.post('https://api.etadirect.com/rest/ofscCore/v1/activities/' + str(activity_id) + '/custom-actions/move', headers=self.headers, data=data)
        #print (response.status_code)
        if response_type==FULL_RESPONSE:
            return response
        elif response_type==JSON_RESPONSE:
            return response.json()
        else:
            return response.text

    def get_subscriptions(self, response_type=TEXT_RESPONSE):
        response = requests.get('https://api.etadirect.com/rest/ofscCore/v1/events/subscriptions', headers=self.headers)
        if response_type==FULL_RESPONSE:
            return response
        elif response_type==JSON_RESPONSE:
            return response.json()
        else:
            return response.text

    def create_subscription(self, data, response_type=TEXT_RESPONSE):
        response = requests.post('https://api.etadirect.com/rest/ofscCore/v1/events/subscriptions', headers=self.headers, data = data)
        if response_type==FULL_RESPONSE:
            return response
        elif response_type==JSON_RESPONSE:
            return response.json()
        else:
            return response.text

    def get_subscription_details(self, subscription_id, response_type=TEXT_RESPONSE):
        response = requests.get('https://api.etadirect.com/rest/ofscCore/v1/events/subscriptions/{}'.format(str(subscription_id)), headers=self.headers)
        if response_type==FULL_RESPONSE:
            return response
        elif response_type==JSON_RESPONSE:
            return response.json()
        else:
            return response.text

    def get_events(self, params, response_type=TEXT_RESPONSE):
        response = requests.get('https://api.etadirect.com/rest/ofscCore/v1/events', headers=self.headers, params=params)
        if response_type==FULL_RESPONSE:
            return response
        elif response_type==JSON_RESPONSE:
            return response.json()
        else:
            return response.text

    def get_resource(self, resource_id, inventories=False, workSkills=False, workZones=False, workSchedules=False , response_type=TEXT_RESPONSE):
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

        response = requests.get('https://api.etadirect.com/rest/ofscCore/v1/resources/{}'.format(str(resource_id)), params=data, headers=self.headers)

        if response_type==FULL_RESPONSE:
            return response
        elif response_type==JSON_RESPONSE:
            return response.json()
        else:
            return response.text

    def get_position_history(self, resource_id,date,response_type=TEXT_RESPONSE):
        params = {}
        params['date'] = date
        response = requests.get('https://api.etadirect.com/rest/ofscCore/v1/resources/{}/positionHistory'.format(str(resource_id)), params=params, headers=self.headers)

        if response_type==FULL_RESPONSE:
            return response
        elif response_type==JSON_RESPONSE:
            return response.json()
        else:
            return response.text

    def get_resource_route(self, resource_id, date, activityFields = None, offset=0, limit=100, response_type=TEXT_RESPONSE):
        params = {}
        if activityFields is not None:
            params['activityFields'] = activityFields
        response = requests.get('https://api.etadirect.com/rest/ofscCore/v1/resources/{}/routes/{}'.format(str(resource_id),date), params=params, headers=self.headers)

        if response_type==FULL_RESPONSE:
            return response
        elif response_type==JSON_RESPONSE:
            return response.json()
        else:
            return response.text
