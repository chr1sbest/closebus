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


var WelcomeView = Backbone.Modal.extend({
  template: _.template(templates.welcome),
    cancelEl: '.bbm-button'
});

var MapView = Backbone.View.extend({
  // Main application view.
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
      var styles = [{
        elementType: "geometry",
        stylers: [{lightness: 40}, {saturation: -80}]
      }];
      var mapOptions = {
        zoom: 17,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        center: latlng,
        styles: styles
      };
      this.map = new google.maps.Map(document.getElementById('map_canvas'),
        mapOptions);

      this.buildDraggable(latlng);  // Draggable center pointer
      this.buildCircle(latlng);     // Cirle around current location
      this.findNearbyStops(latlng); // API query to find nearby stops
    },

    buildDraggable : function(latlng) {
      // Build a draggable icon at current location.
      // When icon is dragged to new location, reset circle and nearby stops.
      var self = this;
      var marker = new google.maps.Marker({
       position: latlng,
         map: this.map,
         draggable:true,
         title:""
      });
       google.maps.event.addListener(marker, 'dragend', function(){
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
            // Only add markers for sf-muni, ac-transit, and Berkeley.
            var agencies = ['sf-muni', 'ac-transit', 'berkeley'];
            var icon_urls = {
              'sf-muni': 'images/muni.png', 
              'ac-transit': 'images/ac.png',
              'berkeley': 'images/berkeley.png'
            }
            if (agencies.indexOf(response.attributes.agency) >= 0 &&
            response.attributes.stop_ids !== 'Unavailable'){
              // The agency is supported and has stop_ids.
              var color
              var busIcon = {
                url: icon_urls[response.attributes.agency],
                scaledSize: new google.maps.Size(20, 25),
                origin: new google.maps.Point(0,0),
                anchor: new google.maps.Point(0, 0)
              }
              var newStop = new google.maps.Marker({
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
                self.displayTimes(newStop);
              });
            }
          },
          error: function(response, error) {
            console.log(response, error);
          }
        });
      });
    },
    displayTimes: function(stop){
      console.log(stop);
    }
});

// Initialize App
var Map = null;
var Welcome = null;

$(function(){
  Map = new MapView();
  Welcome = new WelcomeView();
  $('#modal').html(Welcome.render().el);
});
