var RoutesModel = Backbone.Model.extend({
  // Maps to a single route.
  init: function(options){
    this.agency = options.agency;
    this.stop_id = options.stop_id;
    this.website = options.website;
    this.view = options.view;
  },
  url: function(){
    var baseURL = 'api/v1/departures/';
    return baseURL + this.get('agency') + '/' + this.get('stop_id');
  },
  parse: function(response){
    var self = this;
    // Build bus objects to hold info for each bus in the response.
    var busObjs = _.map(_.keys(response), function(bus) {
      var tmp = {}
      tmp[bus] = {}
      return tmp
    });
    this.set('busses', busObjs);
    _.each(this.get('busses'), function(bus, index){
      var busses = self.get('busses');
      var route = _.keys(busses[index])[0];
      if (Array.isArray(response[route])){
        // Code to handle multiple busses of same name. Rewrite later.
        // For now I'll just take the first value.
        busses[index]['title'] = route;
        busses[index]['direction'] = response[route][0]['@title'];
        busses[index]['predictions'] = response[route][0]['prediction'];
      } else {
      busses[index]['title'] = route;
      busses[index]['direction'] = response[route]['@title'];
      busses[index]['predictions'] = response[route]['prediction'];
      }
    });
    //Render the view now that all the bus data is formatted.
    this.attributes.view.render();
  }
})

var StopModel = Backbone.Model.extend({
  // Model that represents a bus stop and relevant details.
  urlRoot : '/api/v1/stop_id/',
  defaults: {
    id: null,
    name: null,
    stop_ids: null,
    url: null,
    website: null,
    location: null
  }
});

var StopCollection = Backbone.Collection.extend({
  // Collection of bus stops.
  url : '#',
  model : StopModel
});
