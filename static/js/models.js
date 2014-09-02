var RouteModel = Backbone.Model.extend({
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
    this.set('title', _.keys(response)[0]);
    if (Array.isArray(_.values(response)[0])){
      this.set('direction', _.values(response)[0][0]['@title']);
      this.set('predictions', _.values(response)[0][0]['prediction']);
    } else if(_.values(response)[0] == null){
      this.set('direction', "Not in service");
    } else {
      this.set('direction', _.values(response)[0]['@title'] || null);
      this.set('predictions', _.values(response)[0]['prediction'] || null);
    }
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
