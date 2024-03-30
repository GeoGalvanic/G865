document.addEventListener('DOMContentLoaded', init);

function init() {
    // create map and set center and zoom level
    var map = new L.map('mapid');
    map.setView([47.000,-120.554],13);
    
    var mapboxTileUrl = 'https://api.mapbox.com/styles/v1/geogalvanic/ckzc60u1h000l15p898jo1fft/tiles/256/{z}/{x}/{y}@2x?access_token=pk.eyJ1IjoiZ2VvZ2FsdmFuaWMiLCJhIjoiY2t6ODFrYXNwMWcwdTMxbzJwcnEwYWJmMiJ9.PZKvpr8VU90RLA0Lo1i9fg';
    
    L.tileLayer(mapboxTileUrl, {
        attribution: 'Background map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors'
    }).addTo(map);         
}