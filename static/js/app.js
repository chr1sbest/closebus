// Initialize App
var Map = null;
var Welcome = null;

$(function(){
  Map = new MapView();
  Welcome = new WelcomeView();
  $('#modal').html(Welcome.render().el);
});
