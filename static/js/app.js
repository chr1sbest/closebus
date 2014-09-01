function initGeolocation(){
  // Get current location if client browser supports geolocation.
  if (navigator) {
    navigator.geolocation.getCurrentPosition(locateSuccess, locateFail);
  }
  else {
    alert("Sorry, this browser does not support geolocation!")
  }
};

function locateSuccess(position){
  // Define the coordinates as a Google Maps LatLng Object
  var coords = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);

  // Define map options
  var mapOptions = {
    zoom: 18,
    center: coords,
    mapTypeControl: false,
    navigationControlOptions: {style: google.maps.NavigationControlStyle.SMALL},
    mapTypeId: google.maps.MapTypeId.ROADMAP
  };

  // Place google map into map_canvas div
  var map = new google.maps.Map(document.getElementById("map_canvas"), mapOptions);

  // Place the initial marker
  var marker = new google.maps.Marker({
    position: coords,
    map: map,
    title: "Your current location!"
  });

  //search for schools within 1500 metres of our current location, and as a marker use school.png
  placesRequest(map, 'Bus Stations', coords, 1000,['bus_station', 'subway_station']);
}

function locateFail(){
  alert("Sorry, We could not retrieve your location at this time!")
}


//Request places from Google
function placesRequest(map, title, latlng, radius, types, icon){
  //Parameters for our places request
  var request = {
    location: latlng,
    radius: radius,
    types: types
  };
  //Make the service call to google
  var callPlaces = new google.maps.places.PlacesService(map);
  callPlaces.search(request, function(results, status){
    //check to see if Google returns an "OK" status
    if (status == google.maps.places.PlacesServiceStatus.OK){
      _.each(results, function(place) {
        var placeLoc = place.geometry.location;
        var thisplace = new google.maps.Marker({
          map: map,
          position: placeLoc,
          icon: icon,
          title: place.name
        });
    })
    };
  });
}

document.onload = initGeolocation()

  
/*
var ListView = Backbone.View.extend({   
    el: $('body')
,   initialize: function(){
        _.bindAll(this, 'render');
        this.render();
    }
,   render: function() {
        $(this.el).append("<ul> <li> hello world </li> </ul>");
    }
});

var listView = new ListView();
*/

