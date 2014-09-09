import xmltodict
from requests import get as rget
from settings import CTA_KEY
from datetime import datetime
from pytz import timezone

class AbstractAgency(object):
    """
    Base class for all agency API's to inherit from. Each API must have
    methods to get, set_parameters, and transform the result into JSON.
    """
    def __init__(self):
        """
        Each agency needs an api_url and URL params.
        """
        self.api_url = ""
        self.params = {}

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

class NextBus(AbstractAgency):
    """
    Contains methods to communicate and parse the NextBus API.
    """
    def __init__(self):
        url = 'http://webservices.nextbus.com/service/publicXMLFeed'
        self.api_url = url
        self.params = {'command': 'predictions'}

    def set_params(self, agency, stop_id):
        """
        NextBus takes agency and stop_id as parameters.
        """
        self.params['a'] = agency
        self.params['stopId'] = stop_id

    def transform(self, response):
        """
        The NextBus API returns XML. Format XML response into a
        JSON object with correct info.
        """
        json_obj = xmltodict.parse(response.content)
        if json_obj['body'].has_key('Error'):   # NextBus API Error.
            return {'No information available for this stop.': None}
        busses = json_obj['body']['predictions']
        if type(busses) == list:                # Handle list of busses.
            routes = [bus.get('@routeTitle', None) for bus in busses]
            predictions = [bus.get('direction', None) for bus in busses]
            return dict(zip(routes, predictions))
        else:                                   # Handle single bus
            route = busses.get('@routeTitle', None)
            prediction = busses.get('direction', None)
            return {route: prediction}


class ChicagoCTA(AbstractAgency):
    """
    Contains methods to communicate with and parse data from the BART
    ETD API.
    """
    def __init__(self):
        self.api_url = \
            'http://www.ctabustracker.com/bustime/api/v1/getpredictions'
        self.params = {'key': CTA_KEY}

    def set_params(self, agency, stop_id):
        """
        Chicago CTA uses a 'stpid' -> stop_id
        """
        self.params['stpid'] = stop_id

    def transform(self, response):
        """
        The Chicago CTA API returns XML. Format the XML response into a
        JSON object with correct info.
        """
        json_obj = xmltodict.parse(response.content)
        if json_obj['bustime-response'].has_key('error'):   # API Error
            return {'No information available for this stop.': None}
        busses = json_obj['bustime-response']['prd']
        if type(busses) == list:            # Handle list of busses.
            routes = {bus.get('rt'): {'@title': "{0} to {1}".format\
                (bus.get('rtdir'), bus.get('des')), 'prediction':[]}\
                for bus in busses}
            for bus in busses:
                route = bus.get('rt')
                direction = bus.get('rtdir')
                time = self.time_delta(bus.get('prdtm'))
                routes[route]['prediction'].append({'@seconds': time})
        else:                               # Handle single bus.
            route = busses.get('rt')
            direction = busses.get('rtdir')
            title = "{0} to {1}"\
                .format(busses.get('rtdir'), busses.get('des'))
            time = self.time_delta(busses.get('prdtm'))
            routes = {route: \
                {'@title': title, 'prediction': [{'@seconds': time}]}}
        return routes

    def time_delta(self, time):
        """
        Find arrival time by subtracting predicted time from now.
        """
        formatter = "%Y%m%d %H:%M"
        chicago_time = timezone('America/Chicago')
        arrival = datetime.strptime(time, formatter)\
            .replace(tzinfo=chicago_time)
        now = datetime.now(chicago_time)
        diff = (arrival - now).seconds
        diff -= 60 * 51     # Hack to fix weird chicago_time bug! 
        return diff


class BART(AbstractAgency):
    """
    Contains methods to communicate with and parse data from the BART
    ETD API.
    """
    def __init__(self):
        self.api_url = 'http://api.bart.gov/api/etd.aspx'
        self.params = {'cmd': 'etd'}

    def set_params(self, stop):
        """
        BART only requires a stop key.
        """
        self.params['stop'] = stop

    def transform(self, response):
        """
        The BART API return XML. Format the XML response into a
        JSON object with correct info.
        """
        json_obj = xmltodict.parse(response.content)    #TODO
        trains = json_obj['root']['station']['etd']
        return trains


agency_map = {
    'actransit' : NextBus,
    'berkeley' : NextBus,
    'lametro' : NextBus,
    'lametro-rail': NextBus,
    'foothill' : NextBus,
    'sf-muni': NextBus,
    'bronx': NextBus,
    'brooklyn': NextBus,
    'staten-island': NextBus,
    'chicago-cta': ChicagoCTA,
    'BART' : BART
}
