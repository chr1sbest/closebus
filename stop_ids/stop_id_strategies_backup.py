import bs4
import re
import json
from requests import get

import os

website_map = {
    "http://pt.berkeley.edu/around/transit/shuttles": 'actransit',
    "http://www.actransit.org/": 'actransit',
    "http://www.sfmta.com/": 'sf-muni',
    "http://www.goldengate.org/": 'sf-muni'
}

def strategy_location_mapper(details):
    """
    This strategy opens the text file that corresponds to the agency,
    loads up the dictionary, and finds the corresponding 'stop_id' for 
    the name.
    """
    try:    # TODO
        agency = website_map.get(details['website'])
        place = details['name']
        current = os.path.dirname(__file__)
        path = os.path.join(current, 'LocationMaps', agency + '.txt')
        with open(path) as data:
            name_2_stop_id = json.load(data)
            stop_ids = name_2_stop_id.get(place)
            details['stop_ids'] = [stop_ids]
    except:
        details['stop_ids'] = "Unavailable"
    return details

def strategy_crawler(details):
    #OBSOLETE STRATEGY. Will use this as a backup to location_mapper.
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

