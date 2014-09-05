from requests import get
from stop_id_strategies import strategy_crawler, \
        strategy_location_mapper, website_map

def get_stop_id(place_id, key):
    """
    Use chain-of-command to mine for "stop_id" that corresponds 
    to the specific place.
   
    -Default strategy uses mined data held in json files.
    -Backup strategy scrapes for data.
    """
    chain_of_command = [strategy_location_mapper, strategy_crawler]
    details = get_place_details(place_id, key)
    if details['places_status'] != 'OK':
        return {'message': "Failed Place Search", 'details': details}
    for strategy in chain_of_command:
        details = strategy(details)
        # If strategy is successful, stop_id's will be populated.
        if details['stop_ids'] != "Unavailable":
            return details
    return {'message': "Failed to find stop_id's.", 'details': details}

def get_place_details(place_id, key):
    """
    Using the place_id, request more information from the Google Places
    API. Parse and return the relevant details.
    """
    response_template = {
        'place_id': place_id,
        'name': None, 
        'url': None, 
        'agency': None,
        'website': None,
        'places_status': None
    }
    # Make query to Google Places API for details.
    api_url = 'https://maps.googleapis.com/maps/api/place/details/json'
    params = ({'placeid': place_id, 'key': key})
    r = get(api_url, params=params).json()
    # Handle response
    response_template['places_status'] = r['status']
    if r['status'] != 'OK':
        return response_template
    # Overwrite with response information
    response_template['name'] = r['result']['name'] or None
    response_template['url'] = r['result']['url'] or None
    response_template['website'] = r['result']['website'] or None
    response_template['agency'] = website_map.get(website, None)
    return response_template
