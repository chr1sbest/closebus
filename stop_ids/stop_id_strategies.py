import bs4
import re
import json
from requests import get
from bus_stops import website_map

def strategy_location_mapper(details):
    """
    This strategy will map details['location'] to a list of routes
    that contains details on stop_id's. 

    **I believe these lists can be attained by reaching out to the
      public transportation companies directly!**

    The list of stops should be sorted and held on disk.
    Once the stop_id has been retrieved once, it will be mapped 
    accordingly and cached on redis.
    """
    try:    # TODO
        agency = website_map.get(details['website'])
        place = details['name']
        with open('LocationMaps/{0}.txt'.format(agency) as data):
            name_2_stop_id = json.loads(data)
            details['stop_ids'] = name2_stop_id.get('name', None)
    except:
        details['stop_ids'] = "Unavailable"
    return details

def strategy_crawler(details):
    """
    Scrape URL that corresponds with "place_id" to find bus_stop id.

    Google Places unfortunately does not return stop_id, a vital
    component for our realtime NextBus query. Fortunately, they do give
    us details for a URL which maps to a page that contains details on
    "stop_id"!
    """
    try:
        r = get(details['url'])
        soup = bs4.BeautifulSoup(r.text)
        # Regex any div with class 'tppjsc' for a stop_id number
        stop_divs = soup.select('div.tppjsc')
        stop_ids = map(lambda div: re.findall('(\d+)', div.text), stop_divs)
        stop_ids = reduce(lambda x, y: x + y, stop_ids)
        details['stop_ids'] = list(set(stop_ids))   # Remove duplicates
        return details
    except:
        details['stop_ids'] = "Unavailable"
    return details

