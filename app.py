from json import loads
from flask import Flask
from flask.ext import restful
from cache import request_cache
from travel_apis import agency_map

app = Flask(__name__)
api = restful.Api(app)

class Departures(restful.Resource):
    @request_cache(ttl_seconds=90)
    def get(self, agency, stop_id):
        """
        Retrieve departure data from proper agency (or from redis cache).
        """
        transport_api = agency_map[agency]()       # Determine Agency API
        data = transport_api.get(agency, stop_id)  # Request new data
        return data

api.add_resource(Departures, \
    '/departures/<string:agency>/<string:stop_id>')

if __name__ == "__main__":
    app.run(debug=True)
