import requests
import base64

class OFSC:


    def __init__    (self, clientID, companyName, secret):
        self.headers ={}
        self.clientID = clientID
        self.companyName = companyName
        # Calculate Authorization
        mypass = base64.b64encode(bytes(clientID+"@"+companyName+":"+secret, 'utf-8'))
        self.headers["Authorization"] = "Basic "+mypass.decode('utf-8')



    # OFSC Function Library
    def get_activities (self, params):
        response = requests.get('https://api.etadirect.com/rest/ofscCore/v1/activities', headers=self.headers, params=params)
        return response.text

    def get_activity (self, activity_id):
        response = requests.get('https://api.etadirect.com/rest/ofscCore/v1/activities/' + str(activity_id), headers=self.headers)
        #print (response.status_code)
        return response.text

    def update_activity (self, activity_id, data):
        response = requests.patch('https://api.etadirect.com/rest/ofscCore/v1/activities/' + str(activity_id), headers=self.headers, data=data)
        #print (response.status_code)
        return response.text

    def move_activity (self, activity_id, data):
        response = requests.post('https://api.etadirect.com/rest/ofscCore/v1/activities/' + str(activity_id) + '/custom-actions/move', headers=self.headers, data=data)
        #print (response.status_code)
        return response.text

    def get_subscriptions(self):
        response = requests.get('https://api.etadirect.com/rest/ofscCore/v1/events/subscriptions', headers=self.headers)
        return response.text

    def create_subscription(self, data):
        response = requests.post('https://api.etadirect.com/rest/ofscCore/v1/events/subscriptions', headers=self.headers, data = data)
        return response.text

    def get_subscription_details(self, subscription_id):
        response = requests.get('https://api.etadirect.com/rest/ofscCore/v1/events/subscriptions/{}'.format(str(subscription_id)), headers=self.headers)
        return response.text

    def get_events(self, params):
        response = requests.get('https://api.etadirect.com/rest/ofscCore/v1/events', headers=self.headers, params=params)
        return response.text
