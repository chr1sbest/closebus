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

class API_AC_Transit(AbstractAgency):
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
        busses = json_obj['body']['predictions']
        if type(busses) == list:    # Handle multiple values.
            busses = filter(lambda x: x.get('direction', False), busses)
            routes = map(lambda bus: bus.get('@routeTitle', None), busses)
            predictions = map(lambda bus: bus.get('direction', None), busses)
            return dict(zip(routes, predictions))
        else:                       # Handle single value.
            route = busses.get('@routeTitle', None)
            prediction = busses.get('direction', None)
            return {route: prediction}

class API_Muni(AbstractAgency): #TODO
    pass

class API_BART(AbstractAgency): #TODO
    pass

class API_GreyHound(AbstractAgency):
    pass

class API_CalTrain(AbstractAgency):
    pass

agency_map = {
    'actransit' : API_AC_Transit,
    'berkeley' : API_AC_Transit,
    'BART' : API_BART,
    'sf-muni': API_Muni
}
