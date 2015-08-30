import os
import json
import unittest
from requests import get
from closebus.app import app
from closebus.departures.travel_apis import NextBus, ChicagoCTA

class APINextBusTest(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.agency = 'actransit'
        self.stop_id = '54655'

    def test_ac_tranit_set(self):
        ac_transit = NextBus()
        ac_transit.set_params(self.agency, self.stop_id)
        self.assertEqual(ac_transit.params['a'], self.agency)
        self.assertEqual(ac_transit.params['stopId'], self.stop_id)

    def test_ac_transit_get(self):
        ac_transit = NextBus()
        ac_transit.set_params(self.agency, self.stop_id)
        response = get(ac_transit.api_url, 
                       params=ac_transit.params)
        self.assertEqual(response.status_code, 200)

    def test_ac_transit_parse(self):
        ac_transit = NextBus()
        ac_transit.set_params(self.agency, self.stop_id)
        response = get(ac_transit.api_url, 
                       params=ac_transit.params)
        r = ac_transit.transform(response)
        self.assertEqual(type(r), dict)

class APITChicagoCTATest(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.agency = 'chicago-cta'
        self.stop_id = '1115'

    def test_cta_set(self):
        cta = ChicagoCTA()
        cta.set_params(self.agency, self.stop_id)
        self.assertEqual(cta.params['stpid'], self.stop_id)

    def test_cta_get(self):
        cta = ChicagoCTA()
        cta.set_params(self.agency, self.stop_id)
        response = get(cta.api_url, 
                       params=cta.params)
        self.assertEqual(response.status_code, 200)

    def test_cta_parse(self):
        cta = ChicagoCTA()
        cta.set_params(self.agency, self.stop_id)
        response = get(cta.api_url, 
                       params=cta.params)
        r = cta.transform(response)
        self.assertEqual(type(r), dict)

