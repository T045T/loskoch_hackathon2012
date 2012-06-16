var map;
var infowindow;

function callback(results, status) {
  if (status == google.maps.places.PlacesServiceStatus.OK) {
    for (var i = 0; i < results.length; i++) {
      createMarker(results[i]);
    }
  }
}

function createMarker(place) {
  var placeLoc = place.geometry.location;
  var marker = new google.maps.Marker({
    map: map,
    position: place.geometry.location
  });

  google.maps.event.addListener(marker, 'click', function() {
    infowindow.setContent(place.name);
    infowindow.open(map, this);
  });
}

google.maps.event.addDomListener(window, 'load', initialize);

var placeSearch,autocomplete;
var component_form = {
  'street_number': 'short_name',
  'route': 'long_name',
  'locality': 'long_name',
  'administrative_area_level_1': 'short_name',
  'country': 'long_name',
  'postal_code': 'short_name'
};

function wktToLatLng(POINT) {
  var res = /POINT \(([0-9\.]+) ([0-9\.]+)\)/.exec(POINT);
  return new google.maps.LatLng(res[1], res[2]);
}

function initialize() {
  var karlsruhe = new google.maps.LatLng(49.009148,8.379944);
  var defaultCenter = (document.getElementById('id_location').value
  ? wktToLatLng(document.getElementById('id_location').value)
  : karlsruhe);

  map = new google.maps.Map(document.getElementById('map'), {
    mapTypeId: google.maps.MapTypeId.ROADMAP,
    center: defaultCenter,
    zoom: 15
  });
  infowindow = new google.maps.InfoWindow();
  var service = new google.maps.places.PlacesService(map);

  autocomplete = new google.maps.places.Autocomplete(document.getElementById('id_address'), { types: [ 'geocode' ] });
  google.maps.event.addListener(autocomplete, 'place_changed', function(event) {
    markResult();
  });
}

function markResult() {
  var place = autocomplete.getPlace();
  if (place && place.geometry) {
    if (place.geometry.viewport) {
      map.fitBounds(place.geometry.viewport);
    } else {
      map.setCenter(place.geometry.location);
      map.setZoom(17);
    }
    createMarker(place);

    document.getElementById("id_location").value =
    "POINT (" + place.geometry.location.ab + ' ' + place.geometry.location.cb + ")";
  } else {

  }
}

function fillInAddress() {
  var place = autocomplete.getPlace();

  for (var component in component_form) {
    document.getElementById(component).value = "";
    document.getElementById(component).disabled = false;
  }

  for (var j = 0; j < place.address_components.length; j++) {
    var att = place.address_components[j].types[0];
    if (component_form[att]) {
      var val = place.address_components[j][component_form[att]];
      document.getElementById(att).value = val;
    }
  }
}

function geolocate() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(function(position) {
      var geolocation = new google.maps.LatLng(position.coords.latitude,position.coords.longitude);
      autocomplete.setBounds(new google.maps.LatLngBounds(geolocation, geolocation));
    });
  }
}
