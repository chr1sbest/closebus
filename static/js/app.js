var StopModel = Backbone.Model.extend({
  urlRoot : '/api/v1/stop_id/',
  defaults: {
    id: null,
    stop_id: null
  }
});

var StopCollection = Backbone.Collection.extend({
  url : '#',
  model : StopModel
});


var AppView = Backbone.View.extend({
    el: $("#app"),

    events: {},

    initialize: function(){
      var self = this;
      if ("geolocation" in navigator) {
        navigator.geolocation.getCurrentPosition(success, fail);
      }

      function success(position){
        var latitude = position.coords.latitude;
        var longitude = position.coords.longitude;
        var current = new google.maps.LatLng(latitude, longitude);
        self.buildMap(current);
      };
      function fail(){
        var current = new google.maps.LatLng(37.8717775, -122.2676512);
        self.buildMap(current);
      }
    },

    buildMap : function(latlng) {
      var styles = [
        {
          elementType: "geometry",
          stylers: [
            {lightness: 40},
            {saturation: -80}
          ]
        }
      ];
      var mapOptions = {
          zoom: 17,
          mapTypeId: google.maps.MapTypeId.ROADMAP,
          center: latlng,
          styles: styles
      };
      this.map = new google.maps.Map(document.getElementById('map_canvas'),
        mapOptions);

      //Find nearby stops
      this.buildCircle(latlng);
      this.findNearbyStops(latlng);
    },

    buildCircle : function(latlng){
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
      var self = this;
      var request = {
        location: latlng,
        radius: 200,
        types: ['bus_station', 'subway_station']
      };
      var nearby = new google.maps.places.PlacesService(this.map);
      nearby.search(request, function(stops, status){
        //check to see if Google returns an "OK" status
        if (status == google.maps.places.PlacesServiceStatus.OK){
          self.StopCollection = new StopCollection();
          _.each(stops, function(stop) {
            var new_stop = self.buildStop(stop);
            self.StopCollection.add(new_stop);
          })
        };
      })
    },

    buildStop : function(stop) {
      var NewStopModel = new StopModel({id: stop.place_id});
      NewStopModel.fetch({
        success: function(response) {
          testing = response.get('stop_id')
        },
        error: function(response) {
          console.log(response);
        }
      });
      var location = stop.geometry.location;
      var busIcon = {
        url: "bus.png",
        scaledSize: new google.maps.Size(20, 25),
        origin: new google.maps.Point(0,0),
        anchor: new google.maps.Point(0, 0)
      }
      var newStop = new google.maps.Marker({
        map: this.map,
        position: location,
        icon: busIcon,
        zIndex: 1,
        title: stop.name
      });
      google.maps.event.addListener(newStop, 'click', function() {
        var latitude = this.position.lat();
        var longitude = this.position.lng();
      });
      return NewStopModel;
    },
});

// Load the application once the DOM is ready, using `jQuery.ready`:
var App = null;
$(function(){
  App = new AppView();
});
