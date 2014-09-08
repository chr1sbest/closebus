var MapView = Backbone.View.extend({
  // This is the main application view. Handles geolocation, building
  // the google map, finding nearby stops, and then delegates to
  // StopViews/RouteViews for realtime information.
  el: $("#app"),
  initialize: function(){
    // Attempt to geolocalize user, then build Google Map accordingly.
    var self = this;
    var currentWindow = null;
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
      styles: mapStyles,
      panControl: false,
      overviewMapControl: false,
      mapTypeControl: false
    };
    this.map = new google.maps.Map(document.getElementById('map_canvas'),
      mapOptions);

    this.buildNavbar();           // Build Navbar
    this.buildDraggable(latlng);  // Draggable center pointer
    this.buildCircle(latlng);     // Cirle around current location
    this.findNearbyStops(latlng); // API query to find nearby stops
  },
  buildNavbar: function() {
    this.NavbarView = new NavbarView({map: this.map, parent: this});
    this.NavbarView.render()
  },
  buildDraggable : function(latlng) {
    // Build a draggable icon at current location.
    var self = this;
    this.draggableMarker = new google.maps.Marker({
     position: latlng,
       map: this.map,
       draggable:true,
       title:""
    });
    google.maps.event.addListener(this.draggableMarker, 'dragend', function(){
      // When icon is dragged to new location, reset circle and nearby stops.
      var position = self.draggableMarker.getPosition();
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
      zIndex: -1000,
      map: this.map,
      center: latlng,
      radius: 275
    }
    this.radius = new google.maps.Circle(circleOptions);
  },
  findNearbyStops : function(latlng) {
    // Query Google Places API for any nearby ['bus_station']
    var self = this;
    var request = {
      location: latlng,
      radius: 250,
      types: ['bus_station']
    };
    var GAPI = new google.maps.places.PlacesService(this.map);
    GAPI.search(request, function(stops, status){
      if (status == google.maps.places.PlacesServiceStatus.OK){
        // Build new backbone StopCollection()
        self.StopCollection = new StopCollection();
        _.each(stops, function(stop) {
          // Request more info for each stop
          var placeRequest = {placeId: stop.place_id};
          GAPI.getDetails(placeRequest, function(place, status){
            // Build models for each place returned by search.
            var NewStopModel = new StopModel({
              id: stop.place_id,
              location: place.geometry.location,
              name: place.name,
              g_url: place.url,
              website: place.website
            })
            self.buildStop(NewStopModel)
            self.StopCollection.add(NewStopModel);
          });
        });
      }
    });
  },
  buildStop : function(model) {
    var self = this;
    var params = {
      url: model.get('g_url'),
      name: model.get('name'),
      website: model.get('website'),
      place_id: model.get('id')
    }
    model.fetch({
      data: params,
      success: function(response) {
        // Only add markers for actransit, and berkeley shuttles. sf-muni next!
        var agencies = ['actransit', 'berkeley', 'sf-muni', 'foothill', 'lametro',
                        'lametro-rail', 'bronx', 'brooklyn', 'staten-island'];
        var icon_urls = {
          "http://pt.berkeley.edu/around/transit/shuttles": 'images/berkeley.png',
          "http://www.actransit.org/": 'images/ac.png',
          "http://www.sfmta.com/": 'images/muni.png',
          "http://www.goldengate.org/": 'images/gold.png'
        }
        if (agencies.indexOf(response.attributes.agency) >= 0 &&
        response.attributes.stop_ids !== 'Unavailable'){
          // Build stop if agency is supported and has stop_ids.
          var busColor = response.attributes.website;
          var busIcon = {
            url: icon_urls[busColor] || 'images/bus.png',
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
  },
  buildWindow: function(stop) {
    // Build Google Maps InfoWindow with real-time estimates.
    var self = this;
    var infowindow = new google.maps.InfoWindow({
        content: "Loading.."
    });
    if (self.currentWindow){
      self.currentWindow.close();
    }
    infowindow.open(self.map, stop);
    self.currentWindow = infowindow;
    self.getTimes(stop, infowindow);
  },
  getTimes: function(stop, infowindow){
    // Instantiate new route views and fetch route information
    var self = this;
    var newStop = new StopView({
      agency: stop.agency,
      stop_ids: stop.stop_ids,
      website: stop.website,
      infowindow: infowindow
    })
    newStop.render();
  },
});

var StopView = Backbone.View.extend({
  // Parent view to hold children of RouteViews. Occasionally, a single
  // stop will hold multiple stop_id's, this view architecture should be
  // flexibile enough to accomodate them.
  el: '#routes',
  websiteTemplate: _.template(templates.website),
  initialize: function(options){
    var self = this;
    this.agency = options.agency;
    this.stop_ids = options.stop_ids;
    this.website = options.website;
    this.infowindow = options.infowindow;
    this.children = options.children || [];
    this.content = this.websiteTemplate(this)

    _.each(this.stop_ids, function(stop_id){
      var newRoute = new RouteView({
        agency: self.agency,
        stop_id: stop_id,
        website: self.website,
        infowindow: self.infowindow,
        parent: self
      });
      newRoute.model.fetch();
      self.children.push(newRoute);
    })
  },
  newContent: function(content) {
    this.content = content + this.content;
    this.infowindow.setContent(this.content);
  }
})

var RouteView = Backbone.View.extend({
  // This view holds bus information on all the routes related to a stop.
  // Also holds a pointer to the infoWindow on the route. Asynchronously
  // updates "Loading..." to populate the window with realtime content.
  routeTemplate: _.template(templates.route),
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
    _.each(this.model.get('busses'), function(bus){
      // Add details for each route into content.
      var rendered = self.routeTemplate(bus);
      self.parent.newContent(rendered);
    });
    return this;
  },
  parse: function(){
    this.render();
  }

});

var WelcomeView = Backbone.Modal.extend({
  // Displays welcome modal with instructions.
  template: _.template(templates.welcome),
  cancelEl: '.bbm-button'
});

var NavbarView = Backbone.View.extend({
  el: $("#navbar"),
  content: templates.navbar,
  initialize: function(options){
    this.map = options.map;
    this.parent = options.parent;
    this.el.innerHTML = templates.navbar;
    this.buildSearchBox();
  },
  buildSearchBox: function(){
    var self = this;
    var input = document.getElementById('pac-input');
    this.map.controls[google.maps.ControlPosition.TOP_CENTER].push(input);
    var search = new google.maps.places.SearchBox(input);
    google.maps.event.addListener(search, 'places_changed', function() {
      var places = search.getPlaces();
      var newLocation = places[0].geometry.location;
      self.parent.draggableMarker.setPosition(newLocation);
      self.parent.buildCircle(newLocation);     
      self.parent.findNearbyStops(newLocation);
      self.map.panTo(newLocation);
    });
  }
})
