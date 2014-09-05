from requests import get
from stop_id_strategies import strategy_crawler, strategy_location_mapper

def get_stop_id(details):
    """
    Use chain-of-command to mine for "stop_id" that corresponds 
    to the specific place.
   
    -Default strategy uses mined data held in json files.
    -Backup strategy scrapes for data.
    """
    chain_of_command = [strategy_location_mapper, strategy_crawler]
    for strategy in chain_of_command:
        details = strategy(details)
        if details['stop_ids'] != "Unavailable":
            return details
    return {'message': "Failed to find stop_id's.", 'details': details}
