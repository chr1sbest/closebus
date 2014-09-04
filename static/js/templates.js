var templates = {}

//Template for route popup
templates.route = "\
  <div>\
    <h2> <%= title %> </h2>\
    <h3> <%= direction %> </h3>\
    <% if (Array.isArray(predictions)) { _.each(predictions, function(value) { %>\
      <li>\
         <ul><%= Math.floor(value['@seconds']/ 60) < 2 ? 'Arriving soon!' : Math.floor(value['@seconds']/60) + ' minutes' %></ul>\
       </li>\
    <% })} else { if (predictions['@seconds'] == null) { %>\
      <p> Bus not in service. </p> \
    <% } else { %>\
      <li>\
         <ul><%= Math.floor(predictions['@seconds']/ 60) < 2 ? 'Arriving soon!' : Math.floor(predictions['@seconds']/60) + ' minutes' %></ul>\
       </li>\
    <%}}; %>\
  </div>\
";

//Template for welcome message
templates.welcome = " \
  <div class='bbm-modal__topbar'> \
      <h3 class='bbm-modal__title'>CloseBus</h3> \
    </div>\
    <div class='bbm-modal__section'>\
      <p>Realtime arrival estimates on nearby busses!</p>\
      <ul>\
        <li>Click on a bus to get details.</li>\
        <li>Help me grow! As you explore, the app will learn new bus stops :)</li>\
      </ul>\
    </div>\
    <div class='bbm-modal__bottombar'>\
      <a href='#' class='bbm-button'>Ok</a>\
  </div>\
";

//Template for website
templates.website = "\
<a target='_blank' href='<%= website %>' >Route Info</a>\
";

//Template for navbar
templates.navbar = "\
<input id='pac-input' class='controls' type='text' placeholder='Search Box'>\
";

