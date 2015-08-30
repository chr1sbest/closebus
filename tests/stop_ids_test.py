import os
import json
import unittest
from requests import get
from closebus.app import app
from closebus.stop_ids import bus_stops, stop_id_strategies
from nose.plugins.attrib import attr

class StopIDTest(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        url = "/api/v1/stop_id/ChIJ0brW5oJ-hYARPVmHstG33dg?url=https%3A%2F%2Fmaps.google.com%2Fmaps%2Fplace%3Fcid%3D15626848393316751677&name=Haste+St%3AShattuck+Av&website=http%3A%2F%2Fwww.actransit.org%2F&place_id=ChIJ0brW5oJ-hYARPVmHstG33dg"
        response = self.app.get(url).data
        self.good_details = json.loads(response)
        self.good_details['stop_ids'] = "Unavailable"
        self.good_details['agency'] = ['actransit']
        
        # Set up failure.
        self.bad_details = json.loads(response)
        self.bad_details['stop_ids'] = "Unavailable"
        self.bad_details['agency'] = ['lametro']

    def test_website_map(self):
        wmap = stop_id_strategies.website_map
        actrans = 'http://www.actransit.org/'
        mta = 'http://www.mta.info/'
        self.assertEqual(wmap[actrans], ['actransit'])
        self.assertEqual(wmap[mta], ['bronx', 'brooklyn', 'staten-island'])

    def test_location_mapper_pass(self):
        details = self.good_details
        updated = stop_id_strategies.strategy_location_mapper(details)
        self.assertEqual(updated['stop_ids'], ['58005'])

    def test_location_mapper_fail(self):
        details = self.bad_details
        details['agency'] = ['lametro']
        details['stop_ids'] = "Unavailable"
        updated = stop_id_strategies.strategy_location_mapper(details)
        self.assertEqual(updated['stop_ids'], "Unavailable")

    def test_normalizer(self):
        address = 'Dwight PK/w 156 St'
        normalized = stop_id_strategies.normalize_address(address)
        self.assertEqual(normalized, 'Dwight Pk & W 156th St')
        
    def test_ordinal(self):
        x1, x2, x3, x4 = '151 St', '152 St', '153 St', '156 St'
        conv = stop_id_strategies.normalize_address
        self.assertEqual(conv(x1), '151st St')
        self.assertEqual(conv(x2), '152nd St')
        self.assertEqual(conv(x3), '153rd St')
        self.assertEqual(conv(x4), '156th St')

