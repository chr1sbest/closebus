var StopModel = Backbone.Model.extend({
  urlRoot : '/api/v1/stop_id/',
  defaults: {
    id: null,
    stop_id: null,
    location: null
  }
});

var StopCollection = Backbone.Collection.extend({
  url : '#',
  model : StopModel
});

var AppView = Backbone.View.extend({
    el: $("#app"),
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
      this.buildDraggable(latlng);
      this.buildCircle(latlng);
      this.findNearbyStops(latlng);
    },

    buildDraggable : function(latlng) {
      var self = this;
      var marker = new google.maps.Marker({
       position: latlng,
         map: this.map,
         draggable:true,
         title:"Drag me!"
      });
       google.maps.event.addListener(marker, 'dragend', function(){
         var position = marker.getPosition();
         self.buildCircle(position);
         self.findNearbyStops(position);
         self.map.panTo(position);  
       });

    },
    buildCircle : function(latlng){
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
            var NewStopModel = new StopModel({
              id: stop.place_id,
              location: stop.geometry.location
            })
            self.StopCollection.add(NewStopModel);
          })
        };
        self.buildStops();
      })
    },

    buildStops : function() {
      var self = this;
      self.StopCollection.each(function(model){
        model.fetch({
          success: function(response) {
            var busIcon = {
              url: "bus.png",
              scaledSize: new google.maps.Size(20, 25),
              origin: new google.maps.Point(0,0),
              anchor: new google.maps.Point(0, 0)
            }
            var newStop = new google.maps.Marker({
              map: self.map,
              position: response.attributes.location,
              icon: busIcon,
              zIndex: 1,
              title: response.attributes.stop_id
            });
            google.maps.event.addListener(newStop, 'click', function() {
              var latitude = this.position.lat();
              var longitude = this.position.lng();
              console.log(this.title);
            });
          },
          error: function(response) {
            console.log(response);
          }
        });
      });
    }
});

// Load the application once the DOM is ready, using `jQuery.ready`:
var App = null;
$(function(){
  App = new AppView();
});
