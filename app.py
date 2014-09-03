from json import dumps
from flask import Flask 
from flask.ext import restful
from settings import API_KEY
from backend.redis_cache import cache_decorator
from backend.travel_apis import agency_map
from backend.bus_stops import get_stop_id

app = Flask(__name__, static_url_path='')
api = restful.Api(app)

@app.route('/')
def index():
    """ Serve static index page for single-page app frontend."""
    return app.send_static_file('index.html')

class StopID(restful.Resource):
    @cache_decorator(expire=False)
    def get(self, place_id):
        """
        Retrieve StopID using BeautifulSoup and Google Places API
        (or from redis cache).
        """
        data = get_stop_id(place_id, API_KEY)
        return dumps(data)

class Departures(restful.Resource):
    @cache_decorator(expire=True, ttl_seconds=60)
    def get(self, agency, stop_id):
        """
        Retrieve realtime departure data from proper agency 
        (or from redis cache).
        """
        transport_api = agency_map[agency]()       # Determine agency API
        data = transport_api.get(agency, stop_id)  # Request new data
        if data:
            return dumps(data)
        else:
            return {
                'status': 400, 
                'message': 'stop_id could not be found.'
            }

api.add_resource(StopID, \
    '/api/v1/stop_id/<string:place_id>')

api.add_resource(Departures, \
    '/api/v1/departures/<string:agency>/<string:stop_id>')

if __name__ == "__main__":
    app.run()
