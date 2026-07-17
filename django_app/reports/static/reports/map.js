/* 
# Course:      CS 476
# Project:     PotholesYQR
# File:        map.js
# Description: This is a javascript code that uses Leaflet.js to show the pothole map and provides the functionality.
#              The functions below are based on the code provided by Leaflet.js.
# Authors:
#     Opinder Kaur
#     Christopher Taylor
*/

const REGINA = [50.4452, -104.6189];
const map = L.map('map').setView(REGINA, 13);

L.tileLayer('https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap France contributors'
}).addTo(map);

//Marker
/* L.marker(REGINA).addTo(map)
    .bindPopup('We got this.')
    .openPopup(); */

//Displaying the coordinates when we click on the map
/* map.on('click', function (e) {
    console.log("Lat:", e.latlng.lat, "Lon:", e.latlng.lng);

    L.popup()
        .setLatLng(e.latlng)
        .setContent(`Lat: ${e.latlng.lat}<br>Lon: ${e.latlng.lng}`)
        .openOn(map);
}); */

//Displaying the coordinates when we click on the map and the nearest address
map.on('click', function (e) {
    const lat = Number(e.latlng.lat.toFixed(6));
    const lon = Number(e.latlng.lng.toFixed(6));

    // Reverse geocoding URL
    const url = `https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lon}&format=json`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            const address = data.display_name || "Address not found";

            L.popup()
                .setLatLng(e.latlng)
                .setContent(`
                    <b>Coordinates</b><br>
                    Lat: ${lat}<br>
                    Lon: ${lon}<br><br>
                    <b>Nearest Address</b><br>
                    ${address}
                `)
                .openOn(map);
        })
        .catch(err => {
            console.error("Reverse geocoding error:", err);

            L.popup()
                .setLatLng(e.latlng)
                .setContent(`
                    <b>Coordinates</b><br>
                    Lat: ${lat}<br>
                    Lon: ${lon}<br><br>
                    <b>Nearest Address</b><br>
                    Error retrieving address
                `)
                .openOn(map);
        });
});

//Loading all current submitted pothole reports 
fetch('/api/potholes/')
    .then(response => response.json())
    .then(data => {
        data.forEach(p => {
            const marker = L.marker([p.latitude, p.longitude]).addTo(map);

            marker.bindPopup(`
                <b>Pothole #${p.id}</b><br>
                Severity: ${p.severity}<br>
                Status: ${p.current_status}<br>
                Description: ${p.description}
            `);
        });
    })
    .catch(err => console.error("Error loading potholes:", err));
