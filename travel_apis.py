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

        {'6-Parnassus': 
            {'title': 'Inbound to Downtown'
                {'prediction':
                    [
                        {'@seconds': 500},
                        {'@seconds': 1000},
                        {'@seconds': 1500},
                    ]
                }
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
        predictions = json_obj['body']['predictions']
        next_busses = filter(lambda x: x.has_key('direction'), predictions)
        routes = map(lambda bus: bus['@routeTitle'], next_busses)
        predictions = map(lambda bus: bus['direction'], next_busses)
        return dict(zip(routes, predictions))


class API_511(AbstractAgency): #TODO
    pass

class API_GreyHound(AbstractAgency):
    pass

class API_CalTrain(AbstractAgency):
    pass

agency_map = {
    'sf-muni': API_NextBus,
    'BART' : API_NextBus,
    'actransit' : API_NextBus,
}
