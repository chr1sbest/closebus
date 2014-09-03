import bs4
import re
from requests import get

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
        pass
    except:
        pass
    details['stop_ids'] = "Unavailable"
    return details
