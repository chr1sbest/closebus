import os
import bs4
import re
import json
from requests import get

website_map = {
    'http://pt.berkeley.edu/around/transit/shuttles': \
            ['actransit'],
    'http://www.actransit.org/': \
            ['actransit'],
    'http://www.sfmta.com/': \
            ['sf-muni'], 
    'http://www.goldengate.org/': \
            ['sf-muni'],
    'http://www.metro.net/': \
            ['lametro', 'lametro-rail'],
    'http://www.foothilltransit.org/': \
            ['foothill'],
    'http://www.mta.info/': \
            ['bronx', 'brooklyn', 'staten-island'],
    'http://transitchicago.com/': \
            ['chicago-cta'],
    # If no website is passed in, we will iterate through all supported
    # transit agencies in this order. Google maps stopped including transit
    # agency website on json response.
    None: ['actransit', 'sf-muni', 'lametro', 'lametro-rail', 'foothill',
           'bronx', 'brooklyn', 'staten-island', 'chicago-cta']
}

def strategy_location_mapper(details):
    """
    For each agency that the bus stop might fall under, load up the json
    data for the {stop_address: stop_id's} in an attempt to find stop_ids.
    """
    place = normalize_address(details['name'])
    current = os.path.dirname(__file__)
    for agency in details['agency']:
        path = os.path.join(current, 'NextBusData', agency + '.json')
        with open(path) as data:
            name_2_stop_id = json.load(data)
            stop_ids = name_2_stop_id.get(place, "Unavailable")
            details['stop_ids'] = stop_ids
        if details['stop_ids'] != "Unavailable":
            details['agency'] = agency
            return details
    return details

def normalize_address(address):
    """
    Normalize addresses so they can be appropriately searched for against
    the NextBus data set. Many inconsistencies exist throughout the Nation.

    i.e. 'Park Row/Ann St' -> 'Park Row & Ann St'
    """
    # Fix 'Place/Place' -> 'Place & Place'
    if re.findall(r'[a-zA-Z0-9]/[a-zA-Z0-9]', address):
        address = address.replace('/', ' & ')
    # Fix 'Place:Place' -> 'Place & Place'
    if re.findall(r'[a-zA-Z0-9]:[a-zA-Z0-9]', address):
        address = address.replace(':', ' & ')
    # Fix 'RD' -> 'Rd' & 'PK' -> 'Pk'
    if re.findall(r'[PRSA][KDTV]', address):
        address = re.sub(r'([PRSA][KDTV])', \
            lambda x: x.group(0).title(), address)
    # Fix 'Bl' -> 'Blvd'
    if re.findall(r'(Bl)[\ ]', address):
        address = address.replace('Bl', 'Blvd')
    # Fix 'w 156th' -> 'W 156th'
    if re.findall(r'[^a-zA-Z][wnse][/ ]', address):
        address = re.sub(r'[^a-zA-Z]([wnse])[/ ]', \
            lambda x: x.group(0).upper(), address)
    # Fix '151 St' -> '151st St'
    if re.findall(r'[0-9][\ ][SA][tv]', address):
        address = re.sub(r'[0-9]+', \
                ordinal_conversion, address)
    return address

def ordinal_conversion(value):
    """
    Helper function to format numbered streets properly.

    131 St-> 131st St
    142 Av-> 142nd Av
    153 St-> 153rd St
    9 St -> 9th St
    """
    last_digit = value.group(0)[-1]
    value_map = {'1': 'st', '2':'nd', '3':'rd'}
    if value_map.get(last_digit, False):
        return value.group(0) + value_map[last_digit]
    else:
        return value.group(0) + 'th'

def strategy_crawler(details):
    """
    Scrape URL that corresponds with "place_id" to find bus_stop id.

    If the mapper fails, this strategy scrapes information from the
    URL page to find the STOP ID's.
    """
    try:
        response = get(details['url'])
        soup = bs4.BeautifulSoup(response.text)
        # Regex any div with class 'tppjsc' for a stop_id number
        stop_divs = soup.select('div.tppjsc')
        stop_ids = [re.findall(r'(\d+)', div.text) for div in stop_divs]
        stop_ids = reduce(lambda x, y: x + y, stop_ids)
        details['stop_ids'] = list(set(stop_ids))   # Remove duplicates
        if details['stop_ids'] != 'Unavailable':
            details['agency'] = details['agency'][0]
        return details
    except:
        details['stop_ids'] = "Unavailable"
    return details

def strategy_extras(details):
    """
    Query against the manual __extras.json dataset. Similar to 
    strategy_location_mapper but no normalization of address.
    """
    place = details['name']
    current = os.path.dirname(__file__)
    path = os.path.join(current, 'NextBusData', '__extras.json')
    with open(path) as data:
        name_2_stop_id = json.load(data)
        stop_ids = name_2_stop_id.get(place, "Unavailable")
        if stop_ids != "Unavailable":
            details['stop_ids'] = stop_ids
            details['agency'] = details['agency'][0]
    return details
