
/* 
# Course:      CS 476
# Project:     PotholesYQR
# File:        report_map.js
# Description: This is javascript code that uses Leaflet.js to show the pothole map and provides the functionality for submitting a pothole report.
#              The functions below are based on the code provided by Leaflet.js.
# Authors:
#     Opinder Kaur
#     Christopher Taylor
*/

const REGINA = [50.4452, -104.6189];
const reginaBounds = L.latLngBounds(
    [50.3500, -104.7800], // Southwest corner
    [50.5500, -104.4500]  // Northeast corner 
);
const map = L.map('report-map',{minZoom: 11, maxBounds: reginaBounds, maxBoundsViscosity: 1.0}).setView(REGINA, 11);

L.tileLayer('https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap France contributors'
}).addTo(map);

let marker = null;

//this section populates the address latitude and logitude on the report form. It comes from the Submit Report.

const addressField = document.getElementById("id_address");
const params = new URLSearchParams(window.location.search);
const lat = parseFloat(params.get("lat"));
const lon = parseFloat(params.get("lon"));
const address = params.get("address");

if (address) {
    document.getElementById("id_address").value = address;
}

if (!isNaN(lat) && !isNaN(lon)) {
    map.setView([lat, lon], 18);
    marker = L.marker([lat, lon]).addTo(map);
    document.getElementById("id_latitude").value = lat;
    document.getElementById("id_longitude").value = lon;
}

// When a resident clicks on the map, the closest address is loaded into the address field.

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

        if (data.display_name || data.address) {
            // Get full address
            const rawAddress = data.display_name || data.address.road || "";
            //Remove the comma (,) after the house number
            const trimmedAddress = rawAddress.replace(/^(?:(\d+),\s*)?(.*?),\s*Regina.*$/i,(_, number, street) => number ? `${number} ${street}` : street);
            document.getElementById("id_address").value = trimmedAddress;
            marker.bindPopup(trimmedAddress).openPopup();
        }

    }  catch (error) {
            console.error("Reverse geocoding failed:", error);
            alert("Unable to determine the address. Please enter it manually.");
        } 
});

// the following section is for suggesting an address based on resident input using Nominatim.


const suggestionsBox = document.getElementById("address-suggestions");
let lookupTimer;
 
addressField.addEventListener("input", () => {
 
    clearTimeout(lookupTimer);
    suggestionsBox.innerHTML = "";
    lookupTimer = setTimeout(searchAddresses, 1000);
 
});

async function searchAddresses() {
    const query = addressField.value.trim();
    if (query.length < 3) {
        suggestionsBox.innerHTML = "";
        return;
    }
 
    try {
        const response = await fetch(
            `https://nominatim.openstreetmap.org/search?format=jsonv2&q=${encodeURIComponent(query)}&viewbox=-104.75,50.52,-104.45,50.35&bounded=1&limit=5`);
 
        const results = await response.json();
        suggestionsBox.innerHTML = "";
        results.forEach(result => {
 
            const item = document.createElement("div");
            item.className = "address-suggestion"; 
            item.textContent = result.display_name;
            item.addEventListener("click", () => {
                selectAddress(result);
            });
            suggestionsBox.appendChild(item);
        });
 
    } catch (error) {
        console.error("Address lookup failed:", error);
    }
}

function selectAddress(result) {
 
    const lat = Number(parseFloat(result.lat).toFixed(6));
    const lng = Number(parseFloat(result.lon).toFixed(6));
 
    // Populate form fields
    document.getElementById("id_address").value =
        result.display_name;
    document.getElementById("id_latitude").value = lat;
    document.getElementById("id_longitude").value = lng;
 
    // Clear suggestions
    suggestionsBox.innerHTML = "";
 
    // Place or move marker
    if (marker === null) {
        marker = L.marker([lat, lng]).addTo(map);
 
    } else {
        marker.setLatLng([lat, lng]);
    }
    // Zoom to location
    map.setView([lat, lng], 18);
 
}

// add a Reset Map button to reset the map
/* document.getElementById("reset-map-btn").addEventListener("click", () => {
    map.closePopup(); //closes the popup if it is open when the filters are cleared
    map.setView(REGINA, 11); // reset the map view to Regina when filters are cleared
}); */

document.getElementById("reset-map-btn")
    .addEventListener("click", function (event) {
        event.preventDefault();
        event.stopPropagation();
        // Remove marker
        if (marker !== null) {
            map.removeLayer(marker);
            marker = null;
        }

        // Clear form fields
        document.getElementById("id_address").value = "";
        document.getElementById("id_latitude").value = "";
        document.getElementById("id_longitude").value = "";

        // Clear autocomplete suggestions

        const suggestions =
            document.getElementById("address-suggestions");
        if (suggestions) {
            suggestions.innerHTML = "";
        }

        // Reset map view
        map.setView(REGINA, 11);

    });