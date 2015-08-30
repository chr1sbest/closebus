import os
import json
import unittest
from requests import get
from closebus.app import app

class BaseApiTest(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
    
    def test_get_index(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(type(response.data) == str, True)
    
    def test_get_stop_id_pass(self):
        url = '/api/v1/stop_id/ChIJa0V-IYJ-hYARZNrfnrYaUFk?url=https\
                %3A%2F%2Fmaps.google.com%2Fmaps%2Fplace%3Fcid%3D6435\
                673239164279396&name=Shattuck+Av%3AParker+St&website\
                =http%3A%2F%2Fwww.actransit.org%2F&place_id=ChIJa0V-\
                IYJ-hYARZNrfnrYaUFk'
        response = self.app.get(url)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)['details']
        self.assertEqual('url' in response_data, True)
        self.assertEqual('place_id' in response_data, True)
        self.assertEqual('name' in response_data, True)

    def test_get_stop_id_nothing_found(self):
        url = '/api/v1/stop_id/ChIJoWHkRwtnINKUZOTo?url=https%3A%2F%2Fm\
                aps.google.com%2Fmaps%2Fplace%3Fcid%3D41954127252182040\
                98&name=W+23+St%2FAv+of+the+Americas&website=http%3A%2F\
                %2Fwww.mta.info%2F&place_id=ChIJoWZwokRwtnINKUZOTo'
        response = self.app.get(url)
        self.assertEqual(response.status_code, 200)
        message = json.loads(response.data)['message']
        self.assertEqual(message, "Failed to find stop_id's.")

    def test_get_departures_pass(self):
        url = '/api/v1/departures/actransit/50229'
        response = self.app.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual('49' in data, True)

    def test_get_departures_fail(self):
        url = '/api/v1/departures/actransit/50229234'
        response = self.app.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        no_info = data.keys()[0]
        self.assertEqual(no_info, "No information available for this stop.")

