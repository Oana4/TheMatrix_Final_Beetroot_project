var start_lat;
var start_lon;
var end_lat;
var end_lon;
var is_passenger = false;
var startSvgMarker;
var stopSvgMarker;
var startSvgMarkerConfig;
var stopSvgMarkerConfig;
var passengerSvgMarker;

const end_marker_id = "id_end_location"
const start_marker_id = "id_start_location"

var marker = end_marker_id;

const startPath = "M -2 12 l 6 -5 l -6 -4 z M 0 0 q 2.906 0 4.945 2.039 t 2.039 4.945 q 0 1.453 -0.727 3.328 t -1.758 3.516 t -2.039 3.07 t -1.711 2.273 l -0.75 0.797 q -0.281 -0.328 -0.75 -0.867 t -1.688 -2.156 t -2.133 -3.141 t -1.664 -3.445 t -0.75 -3.375 q 0 -2.906 2.039 -4.945 t 4.945 -2.039 z";
const stopPath = "M -3 10 l 6 0 l 0 -6 L -3 4 z M 0 0 q 2.906 0 4.945 2.039 t 2.039 4.945 q 0 1.453 -0.727 3.328 t -1.758 3.516 t -2.039 3.07 t -1.711 2.273 l -0.75 0.797 q -0.281 -0.328 -0.75 -0.867 t -1.688 -2.156 t -2.133 -3.141 t -1.664 -3.445 t -0.75 -3.375 q 0 -2.906 2.039 -4.945 t 4.945 -2.039 z";
const passengerPath = "M -4 11 l 8 0 l 0 -2 C 4 8 3 7 1 7 C 3 5 2 3 0 3 C -2 3 -3 5 -1 7 C -3 7 -4 8 -4 9 z M 0 0 q 2.906 0 4.945 2.039 t 2.039 4.945 q 0 1.453 -0.727 3.328 t -1.758 3.516 t -2.039 3.07 t -1.711 2.273 l -0.75 0.797 q -0.281 -0.328 -0.75 -0.867 t -1.688 -2.156 t -2.133 -3.141 t -1.664 -3.445 t -0.75 -3.375 q 0 -2.906 2.039 -4.945 t 4.945 -2.039 z";
const vehiclePath = "M -4 11 l 2 0 L -2 10 L 2 10 L 2 11 L 4 11 l 0 -2 C 4 8 3 7 3 6 C 3 4 3 4 1 4 L 1 3 L -1 3 L -1 4 C -3 4 -3 4 -3 6 C -3 7 -4 8 -4 9 z M 0 0 q 2.906 0 4.945 2.039 t 2.039 4.945 q 0 1.453 -0.727 3.328 t -1.758 3.516 t -2.039 3.07 t -1.711 2.273 l -0.75 0.797 q -0.281 -0.328 -0.75 -0.867 t -1.688 -2.156 t -2.133 -3.141 t -1.664 -3.445 t -0.75 -3.375 q 0 -2.906 2.039 -4.945 t 4.945 -2.039 z";

function setup(start_lat, start_lon, end_lat, end_lon, is_passenger) {
    console.log("SETUP");
    console.log(start_lat);
    console.log(start_lon);
    console.log(end_lat);
    console.log(end_lon);
    console.log(is_passenger ? 'Passenger' : 'Driver');
    this.start_lat = start_lat;
    this.start_lon = start_lon;
    this.end_lat = end_lat;
    this.end_lon = end_lon;
    this.is_passenger = is_passenger;
    if (this.startSvgMarker) {
      this.startSvgMarker.setPosition({lat: this.start_lat, lng: this.start_lon});
    }
    if (this.stopSvgMarker) {
      this.stopSvgMarker.setPosition({lat: this.end_lat, lng: this.end_lon});
    }
}

function initMap() {
    const myLatLng = { lat: 44.432642242882416, lng: 26.10316865576961 };
    var bounds = new google.maps.LatLngBounds();
    console.log(myLatLng.lat, myLatLng.lng);

    const map = new google.maps.Map(document.getElementById("map"), {
      zoom: 12,
      center: myLatLng,
    });  // there, we can specify the centering

    // Try HTML5 geolocation.
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
          (position) => {
            const pos = {
              lat: position.coords.latitude,
              lng: position.coords.longitude,
            };
            bounds.extend(pos);
            map.fitBounds(bounds);
            config = {
              path: (is_passenger ? passengerPath : vehiclePath),
              fillColor: "purple",
              fillOpacity: 0.8,
              strokeWeight: 0,
              rotation: 0,
              scale: 2,
              anchor: new google.maps.Point(0, 20),
            };
            this.passengerSvgMarker = addPin(pos, map, config);            
          },
          () => {
            // handleLocationError(true, infoWindow, map.getCenter());
          }
      );
    } else {
        // Browser doesn't support Geolocation
        // handleLocationError(false, infoWindow, map.getCenter());
    }

    console.log("ADD PINS");

    this.startSvgMarkerConfig = {
        path: startPath,
        fillColor: "green",
        fillOpacity: 0.8,
        strokeWeight: 0,
        rotation: 0,
        scale: 2,
        anchor: new google.maps.Point(0, 20),
      };
    this.stopSvgMarkerConfig = {
        path: stopPath,
        fillColor: "red",
        fillOpacity: 0.8,
        strokeWeight: 0,
        rotation: 0,
        scale: 2,
        anchor: new google.maps.Point(0, 20),
      };
    
    if ( this.start_lat ) {
      const start = {lat: this.start_lat, lng: this.start_lon};
      console.log("  -> start: ", start);
      const end = {lat: this.end_lat, lng: this.end_lon};
      console.log("  -> stop:  ", end);

      bounds.extend(start);
      bounds.extend(end);

      this.startSvgMarker = addPin(start, map, startSvgMarkerConfig);
      this.stopSvgMarker = addPin(end, map, stopSvgMarkerConfig);
      this.marker = end_marker_id;
      map.fitBounds(bounds);
    }
    google.maps.event.addListener(map, 'click', function(event) {
      if ( is_passenger ) {
        placeMarker(event.latLng, map);
      }
    });

    var stm = document.getElementById(start_marker_id);
    if (stm) {
        stm.readOnly = true;
    }
    var enm = document.getElementById(end_marker_id);
    if (enm) {
        enm.readOnly = true;
    }
}

function placeMarker(location, map) {
  if ( this.marker === end_marker_id) {
    if ( this.stopSvgMarker ) {
      this.stopSvgMarker.setPosition(location);
    } else {
      this.stopSvgMarker = addPin(location, map, stopSvgMarkerConfig);
    }
    $("#id_end_location").val(location);
  } else if ( this.marker === start_marker_id) {
    if ( this.startSvgMarker ) {
      this.startSvgMarker.setPosition(location);
    } else {
      this.startSvgMarker = addPin(location, map, startSvgMarkerConfig);
    }
    $("#id_start_location").val(location);
  } else {
    console.log("WTF! We don't have any location marker...");
  }
}

function select_pin(field) {
    switch (field.id) {
        case start_marker_id:
            console.log("START LOCATION SELECTED");
        break;
        default:
            console.log("STOP LOCATION SELECTED");
    }
    this.marker = field.id;
}

function addPin(location, map, icon) {
    console.log("  ->  -> added pin on map: ", location);
    var marker = new google.maps.Marker({
        position: location,
        icon: icon,
        map: map
     });
     return marker;
}
  
window.initMap = initMap;