from json import dumps
from flask import Flask
from flask.ext.restful import Api, Resource, reqparse
from redis_cache import cache_decorator
from closebus.departures.travel_apis import agency_map
from closebus.stop_ids.stop_id_strategies import website_map
from closebus.stop_ids.bus_stops import get_stop_id

app = Flask(__name__, static_url_path='')
api = Api(app)

@app.route('/')
def index():
    """ Serve static index page for single-page app frontend."""
    return app.send_static_file('index.html')

class StopID(Resource):
    @cache_decorator(expire=False)
    def get(self, place_id):
        """
        Retrieve stop_id information given details of a Google Place.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str)
        parser.add_argument('website', type=str)
        parser.add_argument('url', type=str)
        args = parser.parse_args()
        args['place_id'] = place_id
        args['agency'] = website_map.get(args.website, [])
        data = get_stop_id(args)
        return dumps(data)

class Departures(Resource):
    @cache_decorator(expire=True, ttl_seconds=60)
    def get(self, agency, stop_id):
        """
        Retrieve realtime departure data from appropriate agency.
        """
        transport_api = agency_map[agency]()       # Determine agency API
        data = transport_api.get(agency, stop_id)  # Request new data
        return dumps(data)

api.add_resource(StopID, \
    '/api/v1/stop_id/<string:place_id>')

api.add_resource(Departures, \
    '/api/v1/departures/<string:agency>/<string:stop_id>')

if __name__ == "__main__":
    app.run(debug=True)
