document.addEventListener('DOMContentLoaded', init);

function init() {
    mapboxgl.accessToken = 'pk.eyJ1IjoiZ2VvZ2FsdmFuaWMiLCJhIjoiY2t6ODFrYXNwMWcwdTMxbzJwcnEwYWJmMiJ9.PZKvpr8VU90RLA0Lo1i9fg'
    const map = new mapboxgl.Map({
        container: 'map', // container ID
        style: 'mapbox://styles/geogalvanic/ckzc8lumb000n15qgt6woq85r', // style URL
        center: [-103.2, 44.07], // starting position [lng, lat]
        zoom: 10 // starting zoom
    });

    map.on( 'load', () => { 
        map.addSource('RC_Boundaries', {
            type: 'vector',
            url: 'mapbox://geogalvanic.ckzdbeidb11oe21r2r6fka2io-8zy4j'
        });
        map.addLayer({
            'id': 'RC_BoundaryLayer',
            'type': 'fill',
            'source': 'RC_Boundaries',
            'source-layer': 'RC_Boundaries',
            'paint': {
                'fill-color': [
                    'rgb',
                    [ '/', ['get', 'Bandwidth'], 4],
                    ['-', 255, [ '/', ['get', 'Bandwidth'],  4 ] ],
                    40
                ],
                'fill-opacity': ['+', 0.15, ['/', ['get', 'Bandwidth'], 2000] ],
                'fill-outline-color': '#000000',
            }           
        })

        // When a click event occurs on a feature in the places layer, open a popup at the
        // location of the feature, with description HTML from its properties.
        map.on('click', 'RC_BoundaryLayer', (e) => {
            // Copy coordinates array.
            e.features.sort( (a,b) => b.properties.Bandwidth - a.properties.Bandwidth)
            const lon = e.features[0].geometry.coordinates[0][0][0];
            const lat = e.features[0].geometry.coordinates[0][0][1];
            const coordinates = {lon: lon, lat: lat}
            console.log(coordinates)
            console.log(e.features[0])
            const description = e.features[0].properties.Bandwidth;
            
            // Ensure that if the map is zoomed out such that multiple
            // copies of the feature are visible, the popup appears
            // over the copy being pointed to.
            //while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
            //coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
            //}
            
            new mapboxgl.Popup()
            .setLngLat(coordinates)
            .setHTML(description)
            .addTo(map);
            });
            
            // Change the cursor to a pointer when the mouse is over the places layer.
            map.on('mouseenter', 'RC_BoundaryLayer', () => {
            map.getCanvas().style.cursor = 'pointer';
            });
            
            // Change it back to a pointer when it leaves.
            map.on('mouseleave', 'RC_BoundaryLayer', () => {
            map.getCanvas().style.cursor = '';
            });
    })
}