import json
import bs4
import sys
from requests import get

def get_all_agencies():
    """
    Get a list of all agency tags from NextBus.
    """
    url = 'http://webservices.nextbus.com/service/publicXMLFeed?'
    params = {'command': 'agencyList'}
    r = get(url, params=params)
    soup = bs4.BeautifulSoup(r.text)
    agencies = soup.findAll('agency')
    tags = map(lambda x: x['tag'], agencies)
    return tags

def build(agency):
    """
    Build JSON map of {Names: Numbers} and save into a file
    titled (agency).txt
    """
    url = 'http://www.nextbus.com/wirelessConfig/stopNumbers.jsp'
    r = get(url, params={'a': agency})
    soup = bs4.BeautifulSoup(r.text)
    rows = soup.findAll('tr')
    unique_names = list(set(map(lambda x: x.findAll('td')[0].text, rows)))
    unique_dict = {x: [] for x in unique_names}
    for row in rows:
        name = row.findAll('td')[0].text
        number = row.findAll('td')[2].text
        if number != '-' and number not in unique_dict[name]:
            unique_dict[name].append(number)
    json.dump(unique_dict, open(agency + '.json', 'w'))

def add_to_extras(g_addr, stop_ids):
    """
    Add new item to list of extras.
    """
    assert type(stop_ids) == list, 'Stop ids must be list.'
    with open('__extras.json', 'r+') as data:
        stops = json.load(data)
    stops[g_addr] = stop_ids
    json.dump(stops, open('__extras.json', 'w'))

if __name__ == '__main__' :
    pass
    #agencies = get_all_agencies()
    #for agency in agencies:
        #print 'Retrieving info on {0}.'.format(agency)
        #build(agency)
