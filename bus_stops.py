from requests import get
import bs4
import re

def get_stop_id(place_id, key):
    """
    Scrape URL that corresponds with "place_id" to find bus_stop id.

    Google Places unfortunately does not return stop_id, a vital
    component for our realtime NextBus query. Fortunately, they do give
    us details for a URL which maps to a page that contains details on
    "stop_id"!
    """
    # Get the details and url from Google Places API
    details = get_place_details(place_id, key)
    r = get(details['url'])
    soup = bs4.BeautifulSoup(r.text)
    try:
        # Regex any div with class 'tppjsc' for a stop_id number
        stop_divs = soup.select('div.tppjsc')
        stop_ids = map(lambda div: re.findall('(\d+)', div.text), stop_divs)
        stop_ids = reduce(lambda x, y: x + y, stop_ids)
        details['stop_ids'] = list(set(stop_ids))   # Remove duplicates
    except:
        details['stop_ids'] = "Unavailable"
    return details

def get_place_details(place_id, key):
    """
    Using "place_id", parse the JSON response for the URL.
    """
    # Make query to Google Places API for details.
    api_url = 'https://maps.googleapis.com/maps/api/place/details/json'
    params = ({'placeid': place_id, 'key': key})
    r = get(api_url, params=params).json()

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
