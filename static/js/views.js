var MapView = Backbone.View.extend({
  // This is the main application view. Handles geolocation, building
  // the google map, finding nearby stops, and then delegates to
  // RouteViews for realtime information.
  el: $("#app"),
  initialize: function(){
    // Attempt to geolocalize user, then build Google Map accordingly.
    var self = this;
    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(success, fail);
    }

    function success(position){
      // Build map around current location if geolocation succeeds.
      var latitude = position.coords.latitude;
      var longitude = position.coords.longitude;
      var coords = new google.maps.LatLng(latitude, longitude);
      self.buildMap(coords);
    };
    function fail(){
      // Build map around Berkeley location if geolocation fails.
      var coords = new google.maps.LatLng(37.8717775, -122.2676512);
      self.buildMap(coords);
    }
  },
  buildMap : function(latlng) {
    // Define styles for Google Map Interface.
    // Initialize location-related methods.
    var mapStyles = [{
      elementType: "geometry",
      stylers: [{lightness: 40}, {saturation: -80}]
    }];
    var mapOptions = {
      zoom: 17,
      mapTypeId: google.maps.MapTypeId.ROADMAP,
      center: latlng,
      styles: mapStyles
    };
    this.map = new google.maps.Map(document.getElementById('map_canvas'),
      mapOptions);

    this.buildDraggable(latlng);  // Draggable center pointer
    this.buildCircle(latlng);     // Cirle around current location
    this.findNearbyStops(latlng); // API query to find nearby stops
  },
  buildDraggable : function(latlng) {
    // Build a draggable icon at current location.
    var self = this;
    var marker = new google.maps.Marker({
     position: latlng,
       map: this.map,
       draggable:true,
       title:""
    });
    google.maps.event.addListener(marker, 'dragend', function(){
      // When icon is dragged to new location, reset circle and nearby stops.
      var position = marker.getPosition();
      self.buildCircle(position);
      self.findNearbyStops(position);
      self.map.panTo(position);  
    });
  },
  buildCircle : function(latlng){
    // Draw a circle around current lat/lng on Google Map.
    if (this.radius) {this.radius.setMap(null);}
    var circleOptions = {
      strokeColor: '#FFFFFF',
      strokeOpacity: 0.8,
      strokeWeight: 2,
      fillColor: '#FFFFFF',
      fillOpacity: 0.35,
      zIndex: -2,
      map: this.map,
      center: latlng,
      radius: 200
    }
    this.radius = new google.maps.Circle(circleOptions);
  },
  findNearbyStops : function(latlng) {
    // Query Goole API for nearby bus_stations.
    var self = this;
    var request = {
      location: latlng,
      radius: 200,
      types: ['bus_station']
    };
    var nearby = new google.maps.places.PlacesService(this.map);
    nearby.search(request, function(stops, status){
      if (status == google.maps.places.PlacesServiceStatus.OK){
        // Build new backbone StopCollection()
        self.StopCollection = new StopCollection();
        _.each(stops, function(stop) {
          // Add each stop returned by GAPI to the StopCollection()
          var NewStopModel = new StopModel({
            id: stop.place_id,
            location: stop.geometry.location
          })
          self.StopCollection.add(NewStopModel);
        })
      };
      // Initialize the stop building methods.
      self.buildStops();
    })
  },
  buildStops : function() {
    var self = this;
    self.StopCollection.each(function(model){
      model.fetch({
        success: function(response) {
          // Only add markers for actransit, and berkeley shuttles. sf-muni next!
          var agencies = ['actransit', 'berkeley', 'sf-muni'];
          var icon_urls = {
            "http://pt.berkeley.edu/around/transit/shuttles": 'images/berkeley.png',
            "http://www.actransit.org/": 'images/ac.png',
            "http://www.sfmta.com/": 'images/muni.png',
            "http://www.goldengate.org/": 'images/gold.png'
          }
          if (agencies.indexOf(response.attributes.agency) >= 0 &&
          response.attributes.stop_ids !== 'Unavailable'){
            // Build stop if agency is supported and has stop_ids.
            var color
            var busIcon = {
              url: icon_urls[response.attributes.website],
              scaledSize: new google.maps.Size(24, 32),
              origin: new google.maps.Point(0,0),
              anchor: new google.maps.Point(0, 0)
            }
            var newStop = new google.maps.Marker({
              //Build new marker on map
              map: self.map,
              position: response.attributes.location,
              icon: busIcon,
              zIndex: 1,
              title: response.attributes.name,
              stop_ids: response.attributes.stop_ids,
              website: response.attributes.website,
              agency: response.attributes.agency
            });
            google.maps.event.addListener(newStop, 'click', function() {
              self.buildWindow(newStop)
            });
          }
        },
        error: function(response, error) {
          // Handle fetch error to our API. Currently, the error is handled
          // by simply not building the new stop marker on the map.
          console.log(response, error);
        }
      });
    });
  },
  buildWindow: function(stop) {
    // Build Google Maps InfoWindow with real-time estimates.
    var self = this;
    var infowindow = new google.maps.InfoWindow({
        content: "Loading.."
    });
    infowindow.open(self.map, stop);
    self.getTimes(stop, infowindow);
  },
  getTimes: function(stop, infowindow){
    // Instantiate new route views and fetch route information
    var self = this;
    var newRoute = new RouteView({
      agency: stop.agency,
      stop_id: stop.stop_ids[0],
      website: stop.website,
      infowindow: infowindow
    })
    newRoute.model.fetch();
  },
  renderResponse: function(response){
    _.each(response, function(value, key) {
      var test = new RouteView({
        title: value['@title'], 
        predictions: value['prediction'],
        parent: null
      });
    });
  }
});

var StopView = Backbone.View.extend({
  // Parent view to hold children of RouteViews. Occasionally, a single
  // stop will hold multiple stop_id's, this view structure should be
  // flexibile enough to accomodate them.
  el: '#routes',
  template: _.template(""),
  initialize: function(options){
    this.children = options.children || null;
    this.title = options.title || null;
  },
  render: function(){
    this.template
  }
})

var RouteView = Backbone.View.extend({
  // This view holds bus information on all the routes related to a stop.
  // Also holds a pointer to the infoWindow on the route. Asynchronously
  // updates "Loading..." to populate the window with realtime content.
  el: $('#sup')[0],
  routeTemplate: _.template(templates.route),
  websiteTemplate: _.template(templates.website),
  initialize: function(options){
    this.parent = options.parent;
    this.infowindow = options.infowindow;
    this.model = new RoutesModel({
      title: options.title,
      agency: options.agency,
      stop_id: options.stop_id,
      predictions: options.predictions,
      website: options.website,
      view: this
    })
  },
  render: function(){
    var self = this;
    var content = ""
    _.each(this.model.get('busses'), function(bus){
      // Add details for each route into content.
      var rendered = self.routeTemplate(bus);
      content += rendered;
    });
    // Add "Route Info" link at the bottom.
    content += self.websiteTemplate(this.model.attributes);
    this.infowindow.setContent(content);
    return this;
  }
});

var WelcomeView = Backbone.Modal.extend({
  // Displays welcome modal with instructions.
  template: _.template(templates.welcome),
  cancelEl: '.bbm-button'
});
