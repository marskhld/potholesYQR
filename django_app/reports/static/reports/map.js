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
const potholeReportMarkers = {};
const statusLabels = {
    new: 'New',
    approved: 'Approved',
    rejected: 'Rejected',
    in_progress: 'In Progress',
    pending: 'Pending',
    closed: 'Closed'
};

const severityLabels = {
    high: 'High',
    medium: 'Medium',
    low: 'Low'
};

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
            // These are used in the browser developer tools to monitor what data is retrieved.
            //console.log(p);
            //console.log("ID:", p.id);
            //console.log("Ticket:", p.ticket_number);
            //console.log(potholeReportMarkers);

            // DONE: need to filter out new, rejected, and closed tickets
            //                 <b>Pothole #${p.id}</b><br>
            //                 Description: ${p.description}<br>

            // DONE: add 'created_date', 'updated_date',

           if (p.current_status !== 'new' && p.current_status !== 'closed' && p.current_status !== 'rejected') {
                const marker = L.marker([p.latitude, p.longitude]).addTo(map);
                const severityColour = {};
                const severityIcon =
                    p.severity === 'high' ? '/static/images/severity_high_red.png' :
                    p.severity === 'medium' ? '/static/images/severity_medium_orange.png' :
                    '/static/images/severity_low_yellow.png';
                //if (p.severity == "high") {severityColour = "RED"}

                marker.bindPopup(`
                    <b>Tracking Number: ${p.ticket_number}</b><br>
                    Address: ${p.address.replace(/^(\d+),\s*(.*?),\s*Regina.*$/i, '$1 $2')}<br>
                    Severity: <img src='${severityIcon}' alt='${severityLabels[p.severity] || p.severity}' style="border:1px solid black;border-radius:50%;width:15px;height:15px;vertical-align:text-bottom;margin-left:4px;"> ${severityLabels[p.severity] || p.severity}<br>
                    Status: ${statusLabels[p.current_status] || p.current_status}<br>
                    Reported: ${p.created_date.split('T')[0]}<br>
                    Updated: ${p.updated_date.split('T')[0]}<br>
                    Notes: ${p.public_notes}<br>
                `);
            potholeReportMarkers[p.ticket_number] = marker;
           };
        });
        //console.log(potholeReportMarkers);
    })
    .catch(err => console.error("Error loading potholes:", err));

// Build tracking ticket search HTML for the map
const SearchControl = L.Control.extend({
    options: {
        position: 'topright'
    },
    onAdd: function () {
        const div = L.DomUtil.create('div', 'pothole-search');
        div.innerHTML = `
                <input type="text"
                    id="potholeSearch"
                    title="Type a Pothole Report Ticket # to locate it on the map"
                    placeholder="Pothole Report Ticket #">
                <button id="potholeSearchBtn" type="button">
                    Search
                </button>
            </form>
        `;
        L.DomEvent.disableClickPropagation(div);
        return div;
    }
});

// Add the search control to the map
map.addControl(new SearchControl());

// Process the search
document.addEventListener("click", function (e) {
    if (e.target.id === "potholeSearchBtn") {
        const ticketNumber =
            document.getElementById("potholeSearch").value.trim();
        const marker = potholeReportMarkers[ticketNumber];
        if (marker) {
            // Set the map view to the selected pothole
            map.setView(marker.getLatLng(), 18);
            // Pop up pothole information
            marker.openPopup();
        } else {
            alert(`Pothole Report Ticket #${ticketNumber} was not found.`);
        }
    }
});
