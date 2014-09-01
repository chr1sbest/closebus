from requests import get
import bs4
import re

def get_stop_id(place_id, key):
    """
    Scrape URL that corresponds with "place_id" to find bus_stop id.
    """
    details = get_place_details(place_id, key)
    r = get(details['url'])             # GET URL of place to parse
    soup = bs4.BeautifulSoup(r.text)
    try:
        stop_divs = soup.select('div.tppjsc')
        stop_ids = map(lambda div: re.findall('(\d+)', div.text), stop_divs)
        stop_ids = reduce(lambda x, y: x + y, stop_ids)
        details['stop_ids'] = stop_ids
    except:
        details['stop_ids'] = "Unavailable"
    return details

def get_place_details(place_id, key):
    """
    Using "place_id", parse the JSON response for the URL.
    """
    api_url = 'https://maps.googleapis.com/maps/api/place/details/json'
    params = ({'placeid': place_id, 'key': key})
    r = get(api_url, params=params).json()
    name = r['result']['name'] or None
    url = r['result']['url'] or None
    website = r['result']['website'] or None
    return {
        'place_id': place_id,
        'name': name, 
        'url': url, 
        'website': website
    }

if __name__ == "__main__":
    place_id = 'ChIJIzKCwid8hYARRAV-ixw4n68'
    a = get_stop_id(place_id, key)
