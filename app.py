from flask import Flask
from flask.ext import restful
from requests import get as rget
import xmltodict, json

app = Flask(__name__)
api = restful.Api(app)

class Departures(restful.Resource):
    api_url = 'http://webservices.nextbus.com/service/publicXMLFeed'
    params = {'command': 'predictions'}

    def get(self, agency, stop_id):
        """
        Retrieve departure data from cache or GET NextBus data.
        """
        self.params['stopId'] =  stop_id
        self.params['a'] = agency
        response = rget(self.api_url, params=self.params)
        if response.status_code == 200:
            return self.parse(response), 200
        return response

    def parse(self, response):
        """ 
        Format XML response into JSON object with relevant info.
        """
        json_obj = xmltodict.parse(response.content)
        predictions = json_obj['body']['predictions']
        next_busses = filter(lambda x: x.has_key('direction'), predictions)
        routes = map(lambda bus: bus['@routeTitle'], next_busses)
        predictions = map(lambda bus: bus['direction'], next_busses)
        return dict(zip(routes, predictions))

api.add_resource(Departures, \
    '/departures/<string:agency>/<string:stop_id>')

if __name__ == "__main__":
    app.run(debug=True)
