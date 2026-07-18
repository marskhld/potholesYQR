
/* 
# Course:      CS 476
# Project:     PotholesYQR
# File:        report_map.js
# Description: This is a javascript code that uses Leaflet.js to show the pothole map and provides the functionality.
#              The functions below are based on the code provided by Leaflet.js.
# Authors:
#     Opinder Kaur
#     Christopher Taylor
*/

const REGINA = [50.4452, -104.6189];
const map = L.map('report-map').setView(REGINA, 13);

L.tileLayer('https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap France contributors'
}).addTo(map);

let marker = null;

map.on("click", async function(e) {

    const lat = Number(e.latlng.lat.toFixed(6));
    const lng = Number(e.latlng.lng.toFixed(6));

    // Save coordinates to hidden form fields
    document.getElementById("id_latitude").value = lat;
    document.getElementById("id_longitude").value = lng;

    if (marker === null) {
        marker = L.marker([lat, lng]).addTo(map);
    } else {
        marker.setLatLng([lat, lng]);
    }

    try {
        const response = await fetch(
            `https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${lat}&lon=${lng}`
        );

        const data = await response.json();

        if (data.display_name) {
            document.getElementById("id_address").value = data.display_name;
            marker.bindPopup(data.display_name).openPopup();
        }

    }  catch (error) {
/*         console.error("Reverse geocoding failed:", error);
        alert("Unable to determine the address. Please enter it manually."); */
    } 
});