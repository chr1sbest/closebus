import json
import bs4
import sys
from requests import get

def build(agency):
    """
    Build JSON map of {Names: Numbers} and save into a file
    titled (agency).txt
    """
    url = 'http://www.nextbus.com/wirelessConfig/stopNumbers.jsp'
    r = get(url, params={'a': agency})
    soup = bs4.BeautifulSoup(r.text)
    rows = soup.findAll('tr')
    name = map(lambda x: x.findAll('td')[0].text, rows)
    numbers = map(lambda x: x.findAll('td')[2].text, rows)
    mapped = dict(zip(name, numbers))
    json.dump(mapped, open(agency + '.txt', 'w'))

if __name__ == '__main__' :
    agency = sys.argv[1]
    print 'Finding details on ' + agency
    build(agency)
    print 'File saved to ' + agency + '.txt'

