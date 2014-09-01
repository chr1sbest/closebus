var templates = {}
templates.welcome = " \
  <div class='bbm-modal__topbar'> \
      <h3 class='bbm-modal__title'>CloseBus</h3> \
    </div>\
    <div class='bbm-modal__section'>\
      <p>Realtime arrival estimates on nearby busses!</p>\
      <ul>\
        <li>Click on a bus for realtime arrival estimates via NextBus API.</li>\
        <li>Drag the red marker to update your location.</li>\
        <li>Help me grow! Feel free to play around -- as you explore, the app will learn new bus stops :)</li>\
      </ul>\
    </div>\
    <div class='bbm-modal__bottombar'>\
      <span style='float-left'>&copy; Chris Best 2014</span>\
      <a href='#' class='bbm-button'>Close</a>\
  </div>\
"

templates.arrivals = " \
  <div class='bbm-modal__topbar'> \
      <h3 class='bbm-modal__title'> <%= title =%> </h3> \
    </div>\
    <div class='bbm-modal__section'>\
      <p>Arrival Times</p>\
      <ul>\
      </ul>\
    </div>\
  </div>\
"
