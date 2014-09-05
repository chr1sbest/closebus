import xmltodict
import json
from requests import get as rget

class AbstractAgency(object):
    def get(self, agency, stop_id):
        """
        Submit GET request to agency -> then parse and transform
        the response to JSON object with correct fields.
        """
        self.set_params(agency, stop_id)
        response = rget(self.api_url, params=self.params)
        return self.transform(response)

    def set_params(self):
        """
        Each Agency API uses different request parameters.
        Implement appropriately in subclass.
        """
        raise NotImplementedError
    
    def transform(self):
        """
        Each Agency API returns different data formats. Need to parse and
        transform each dataset into JSON in this format:

        {'6-Parnassus': {
            'title': 'Inbound to Downtown',
            'prediction':
                [
                    {'@seconds': 500},
                    {'@seconds': 1000},
                    {'@seconds': 1500},
                ]
            }
        }

        Implement appropriately in subclass.
        """
        raise NotImplementedError

class API_NextBus(AbstractAgency):
    def __init__(self):
        self.api_url = 'http://webservices.nextbus.com/service/publicXMLFeed'
        self.params = {'command': 'predictions'}

    def set_params(self, agency, stop_id):
        self.params['a'] = agency
        self.params['stopId'] =  stop_id

    def transform(self, response):
        """ 
        Format XML response into JSON object with correct info.
        """
        json_obj = xmltodict.parse(response.content)
        if json_obj['body'].has_key('Error'):
            # Failure to retrieve information.
            return {'No information available': None}
        busses = json_obj['body']['predictions']
        if type(busses) == list:
            # Handle array of busses.
            routes = map(lambda bus: bus.get('@routeTitle', None), busses)
            predictions = map(lambda bus: bus.get('direction', None), busses)
            return dict(zip(routes, predictions))
        else:                        
            # Handle single bus.
            route = busses.get('@routeTitle', None)
            prediction = busses.get('direction', None)
            return {route: prediction}

class API_BART(AbstractAgency): #TODO
    def __init__(self):
        self.api_url = 'http://api.bart.gov/api/etd.aspx'
        self.params = {'cmd': 'etd'}

    def set_params(self, stop):
        pass

    def parse(self, response):
        json_obj = xmltodict.parse(response.content)
        trains = json_obj['root']['station']['etd']



class API_GreyHound(AbstractAgency):
    pass

class API_CalTrain(AbstractAgency):
    pass

agency_map = {
    'actransit' : API_NextBus,
    'berkeley' : API_NextBus,
    'lametro' : API_NextBus,
    'lametro-rail': API_NextBus,
    'foothill' : API_NextBus,
    'sf-muni': API_NextBus,
    'bronx': API_NextBus,
    'brooklyn': API_NextBus,
    'staten-island': API_NextBus,
    'BART' : API_BART
}
