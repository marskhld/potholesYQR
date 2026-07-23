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
const map = L.map('map',{minZoom: 13}).setView(REGINA, 13); //Preventing the user from zooming out too far
const potholeReportMarkers = {};
const allPotholeMarkers = [];
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

// Reference: https://github.com/pointhi/leaflet-color-markers
// Obtained different coloured markers for different severity
// Code similar to this is provided at the URL above because
// that is how it works. Adjusted for our project.
const pinSeverityIcons = {
    high: L.icon({
        iconUrl: '/static/images/marker-icon-high_red.png',
        iconRetinaUrl: '/static/images/marker-icon-2x-high_red.png',
        shadowUrl: '/static/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
     }),

    medium: L.icon({
        iconUrl: '/static/images/marker-icon-medium_orange.png',
        iconRetinaUrl: '/static/images/marker-icon-2x-medium_orange.png',
        shadowUrl: '/static/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    }),

    low: L.icon({
        iconUrl: '/static/images/marker-icon-low_yellow.png',
        iconRetinaUrl: '/static/images/marker-icon-2x-low_yellow.png',
        shadowUrl: '/static/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
     })
};

// attribution for the use of OpenStreetMap
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
            const address = data.display_name.replace(/^(\d+\s+)?(.*?),\s*Regina.*$/i, '$1 $2') || "Address not found";

            L.popup()
                .setLatLng(e.latlng)
                .setContent(`
                  <b>Nearest Address: </b>
                    ${address}
                    <div style="text-align: center;" class="button">
                        <a href='/api/report/?lat=${lat}&lon=${lon}'
                        target="_blank">
                        <button type="submit" 
                                style ="width:auto; font-size:12px"> 
                                Submit Pothole Report 
                        </button>
                    </a></div>
                `)
                .openOn(map);
        })
        .catch(err => {
            console.error("Reverse geocoding error:", err);

            L.popup()
                .setLatLng(e.latlng)
                .setContent(`
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
            // DONE: change pin / marker colour based on severity
            // DONE: added filters and moved ticket search inline with filters

           if (p.current_status !== 'new' && p.current_status !== 'closed' && p.current_status !== 'rejected') {
                // load the photos for thumbails in the pop-ups
                const photoThumbnails = (p.photos || [])
                    .map(url => `
                        <a href="${url}" target="_blank">
                            <img src="${url}"
                            style="width:75px;height:75px;object-fit:cover;
                                border:1px solid black;margin:2px;cursor:pointer;
                            ">
                        </a>
                    `)
                .join('');
                //console.log(photoHtml);
                // choose marker colour based on severity
                const markerIcon = pinSeverityIcons[p.severity] || pinSeverityIcons.low;
                // update marker colour based on severity
                const marker = L.marker([p.latitude, p.longitude],{ icon: markerIcon }).addTo(map);
                marker.reportData = p;
                allPotholeMarkers.push(marker);
                console.log(data[0]);
                // Extract the address up to Regina and get rid of the comma after the building number
                //(\d+\s+)? optional street number
                //(.*?) everything up to the first comma
                //Regina.* → remove Regina and everything after
                const trimmedAddress = p.address.replace(/^(\d+\s+)?(.*?),\s*Regina.*$/i, '$1 $2');
                // Format the dates to remove the time so they are yyyy-mm-dd
                const createdDate = p.created_date.split('T')[0];
                const updatedDate = p.updated_date.split('T')[0];
                // set the icon used beside Severity in the popup
                const severityIcon =
                    p.severity === 'high' ? '/static/images/severity_high_red.png' :
                    p.severity === 'medium' ? '/static/images/severity_medium_orange.png' :
                    '/static/images/severity_low_yellow.png';
                //if (p.severity == "high") {severityColour = "RED"}

                // Build the popup HTML
                const popupHTML = `
                    <b>Tracking Number: ${p.ticket_number}</b><br>
                    Address: ${trimmedAddress}<br>
                    Severity: <img src='${severityIcon}' 
                        alt='${severityLabels[p.severity] || p.severity}' 
                        style="border:1px 
                                solid black;
                                border-radius:50%;
                                width:15px;
                                height:15px;
                                vertical-align:text-boTracking Number: Yttom;
                                margin-left:4px;"> ${severityLabels[p.severity] || p.severity}<br>
                    Status: ${statusLabels[p.current_status] || p.current_status}<br>
                    Reported: ${createdDate}<br>
                    Updated: ${updatedDate}<br>
                    Notes: ${p.public_notes}<br>
                    Photos:<br>
                    ${photoThumbnails}
                `;
                // bind the popup HTML to the marker
                marker.bindPopup(popupHTML);
                // keep track of the published tickets on the map
                potholeReportMarkers[p.ticket_number] = marker;
           };
        });
        //console.log(potholeReportMarkers);
    })
    .catch(err => console.error("Error loading potholes:", err));

// Moved this into map.html so the ticket search is inline with the filters
// Build tracking ticket search HTML for the map
/* const SearchControl = L.Control.extend({
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
map.addControl(new SearchControl()); */

// Process the search
document.addEventListener("click", function (e) {
    if (e.target.id === "pothole-Search-Btn") {
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

// add function to filter markers based on Severity
function filterMarkers() {
    const severity = document.getElementById("map-severity-filter").value;
    const status = document.getElementById("map-status-filter").value;
    const createdFromDate = document.getElementById("map-created-from-date").value;
    const createdToDate = document.getElementById("map-created-to-date").value;
    allPotholeMarkers.forEach(marker => {
        const report = marker.reportData;
        const matchSeverity = !severity || report.severity === severity;
        const matchStatus = !status || report.current_status === status;
        const createdDate = report.created_date.split('T')[0];
        const matchCreatedFromDate = !createdFromDate || createdDate >= createdFromDate;
        const matchCreatedToDate = !createdToDate || createdDate <= createdToDate;
        
        if (matchSeverity && matchStatus && matchCreatedFromDate && matchCreatedToDate) {
            marker.addTo(map);
        } else {
            map.removeLayer(marker);
        }
    });
}

// add a listener to update the map immediately if a Severity filter is applied
document.getElementById("map-severity-filter").addEventListener("change", filterMarkers);

// add a listener to update the map immediately if a Status filter is applied
document.getElementById("map-status-filter").addEventListener("change", filterMarkers);

// add a listener to update the map immediately if a Created From Date filter is applied
document.getElementById("map-created-from-date").addEventListener("change", filterMarkers);

// add a listener to update the map immediately if a Created To Date filter is applied
document.getElementById("map-created-to-date").addEventListener("change", filterMarkers);

// add a Clear Filters button to clear the Severity, Status and Created Date filters
document.getElementById("map-clear-filters").addEventListener("click", () => {
    document.getElementById("map-severity-filter").value = "";
    document.getElementById("map-status-filter").value = "";
    document.getElementById("map-created-from-date").value = "";
    document.getElementById("map-created-to-date").value = "";
    document.getElementById("potholeSearch").value = "";
    filterMarkers();
});
