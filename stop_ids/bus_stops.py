from requests import get
from stop_id_strategies import strategy_crawler, strategy_location_mapper

def get_stop_id(place_id, key):
    """
    Use multiple strategies to mine for "stop_id" that corresponds to
    the specific place.
   
    Default strategy is a crawler.
    """
    # Get the details and url from Google Places API
    details = get_place_details(place_id, key)
    # Try each strategy to retrive stop_id details
    strategies = [strategy_location_mapper, strategy_crawler]
    for strategy in strategies:
        details = strategy(details)
        # If strategy successful, stop_id's will be populated.
        if details['stop_ids'] != "Unavailable":
            return details
    return False

def get_place_details(place_id, key):
    """
    Using "place_id", parse the JSON response for the URL.
    """
    # Make query to Google Places API for details.
    api_url = 'https://maps.googleapis.com/maps/api/place/details/json'
    params = ({'placeid': place_id, 'key': key})
    r = get(api_url, params=params).json()
    if r['status'] == 'INVALID_REQUEST':
        return {
            'place_id': place_id,
            'name': None, 
            'url': None, 
            'agency': None,
            'website': None
        }

    # Use info gained from place_id query to map to transit agency.
    name = r['result']['name'] or None
    url = r['result']['url'] or None
    website = r['result']['website'] or None
    agency = website_map.get(website, None)
    return {
        'place_id': place_id,
        'name': name, 
        'url': url, 
        'agency': agency,
        'website': website
    }

website_map = {
    "http://pt.berkeley.edu/around/transit/shuttles": 'actransit',
    "http://www.actransit.org/": 'actransit',
    "http://www.sfmta.com/": 'sf-muni',
}

if __name__ == "__main__":
    place_id = 'ChIJIzKCwid8hYARRAV-ixw4n68'
    a = get_stop_id(place_id, key)
