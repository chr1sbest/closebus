from requests import get
import bs4
import re

def get_stop_id(place_id, key):
    """
    Scrape URL that corresponds with "place_id" to find bus_stop id.
    """
    url = get_url(place_id, key)
    r = get(url)
    soup = bs4.BeautifulSoup(r.text)
    try:
        stop_div = soup.select('div.tppjsc')[0].text
        stop_id = re.findall('(\d+)', stop_div)[0]
        return stop_id
    except:
        return "Stop Details Unavailable!"

def get_url(place_id, key):
    """
    Using "place_id", parse the JSON response for the URL.
    """
    url = 'https://maps.googleapis.com/maps/api/place/details/json'
    params = ({'placeid': place_id, 'key': key})
    r = get(url, params=params)
    return r.json()['result']['url']

if __name__ == "__main__":
    place_id = 'ChIJIzKCwid8hYARRAV-ixw4n68'
    a = get_stop_id(place_id, key)
