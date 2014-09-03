import os
import json
import unittest
from requests import get
from app import app
from settings import API_KEY
from bus_stops import get_stop_id, get_place_details
from stop_id_strategies import strategy_crawler
from travel_apis import API_NextBus


class BaseApiTest(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
    
    def test_get_index(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(type(response.data) == str, True)
    
    def test_get_stop_id_pass(self):
        url = '/api/v1/stop_id/ChIJATvJ0S98hYARcEmyhx7c7Hs'
        response = self.app.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual('agency' in json.loads(response.data), True)
        self.assertEqual('stop_ids' in json.loads(response.data), True)
        self.assertEqual('url' in json.loads(response.data), True)
        self.assertEqual('place_id' in json.loads(response.data), True)

    def test_get_stop_id_fail(self):
        url = '/api/v1/stop_id/will_fail'
        response = self.app.get(url)
        self.assertEqual(response.status_code, 500)

    def test_get_place_details(self):
        place_id = 'ChIJATvJ0S98hYARcEmyhx7c7Hs'
        url = 'https://maps.google.com/maps/place?cid=8929754184852588912' 
        response = get_place_details(place_id, API_KEY)
        self.assertEqual(response['agency'], 'actransit')
        self.assertEqual(response['url'], url)


class StopIDStrategyTest(unittest.TestCase):
    def test_strategy_crawler(self):
        details = {
            'url':'https://maps.google.com/maps/place?cid=8929754184852588912' 
        }
        response = strategy_crawler(details)
        self.assertEqual(type(response['stop_ids']), list)
        self.assertEqual(response['url'], details['url'])

    def test_strategy_mappers(self):
        # TODO
        pass


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


class RedisTest(unittest.TestCase):
    pass

if __name__ == '__main__':
    unittest.main()
