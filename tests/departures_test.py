import os
import json
import unittest
from requests import get
from app import app
from departures.travel_apis import API_NextBus

class APINextBusTest(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.agency = 'actransit'
        self.stop_id = '54655'

    def test_ac_tranit_set(self):
        ac_transit = API_NextBus()
        ac_transit.set_params(self.agency, self.stop_id)
        self.assertEqual(ac_transit.params['a'], self.agency)
        self.assertEqual(ac_transit.params['stopId'], self.stop_id)

    def test_ac_transit_get(self):
        ac_transit = API_NextBus()
        ac_transit.set_params(self.agency, self.stop_id)
        response = get(ac_transit.api_url, 
                       params=ac_transit.params)
        self.assertEqual(response.status_code, 200)

    def test_ac_transit_parse(self):
        ac_transit = API_NextBus()
        ac_transit.set_params(self.agency, self.stop_id)
        response = get(ac_transit.api_url, 
                       params=ac_transit.params)
        r = ac_transit.transform(response)
        self.assertEqual(type(r), dict)

