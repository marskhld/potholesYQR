/* 
# Course:      CS 476
# Project:     PotholesYQR
# File:        staff_map.js
# Description: This is javascript code that uses Leaflet.js to show the pothole map with total reports.
#              The functions below are based on the code provided by Leaflet.js.
#              This file is based on map.js.
# Authors:
#     Opinder Kaur
#     Christopher Taylor
*/

const REGINA = [50.4452, -104.6189];
const reginaBounds = L.latLngBounds(
    [50.3500, -104.7800], // Southwest corner
    [50.5500, -104.4500]  // Northeast corner 
);
const map = L.map('staff-map', {minZoom: 11, maxBounds: reginaBounds, maxBoundsViscosity: 1.0}).setView(REGINA, 11);
const allStaffMarkers = [];
const staffMarkersByTicket = {};
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

/* // Severity icons
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
}; */

// Define Status marker pin icons
const pinStatusIcons = {
    approved: L.icon({
        iconUrl: '/static/images/marker-icon-approved-green.png',
        iconRetinaUrl: '/static/images/marker-icon-2x-approved-green.png',
        shadowUrl: '/static/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
     }),

    in_progress: L.icon({
        iconUrl: '/static/images/marker-icon-in_progress-orange.png',
        iconRetinaUrl: '/static/images/marker-icon-2x-in_progress-orange.png',
        shadowUrl: '/static/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    }),

    pending: L.icon({
        iconUrl: '/static/images/marker-icon-pending-yellow.png',
        iconRetinaUrl: '/static/images/marker-icon-2x-pending-yellow.png',
        shadowUrl: '/static/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    }),

    new: L.icon({
        iconUrl: '/static/images/marker-icon-new-blue.png',
        iconRetinaUrl: '/static/images/marker-icon-2x-new-blue.png',
        shadowUrl: '/static/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
     }),

    rejected: L.icon({
        iconUrl: '/static/images/marker-icon-rejected-red.png',
        iconRetinaUrl: '/static/images/marker-icon-2x-rejected-red.png',
        shadowUrl: '/static/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
     }),

    closed: L.icon({
        iconUrl: '/static/images/marker-icon-closed-grey.png',
        iconRetinaUrl: '/static/images/marker-icon-2x-closed-grey.png',
        shadowUrl: '/static/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
     }),
};

// Tile layer 
L.tileLayer('https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap France contributors'
}).addTo(map);

//Displaying the address when user clicks on the map
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
                  <b>Nearest Address: </b>
                    ${address}
                    <p>
                    </p>
                    <div style="text-align: center;" class="button">
                        <a href='/api/report/?lat=${lat}&lon=${lon}'
                        target="_blank">
                        <button id="submit-report-btn"
                                type="submit" 
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
                    <b>Address</b><br>
                    Error retrieving address
                `)
                .openOn(map);
        });

});

// Load pothole reports
fetch('/api/potholes/')
    .then(response => response.json())
    .then(data => {
        data.forEach(p => {

            // Choose marker color based on severity
            const markerIcon = pinStatusIcons[p.current_status] || pinStatusIcons.pending;

            const marker = L.marker([p.latitude, p.longitude], { icon: markerIcon }).addTo(map);

            marker.reportData = p;                          // store full report
            allStaffMarkers.push(marker);                   // store marker for filters
            staffMarkersByTicket[p.ticket_number] = marker; // store marker for search

            // Trim address 
            const trimmedAddress = p.address.replace(/^(\d+),\s*(.*?),\s*Regina.*$/i, '$1 $2');

            // Format dates
            const createdDate = p.created_date.split('T')[0];
            const updatedDate = p.updated_date.split('T')[0];

            // Severity icon inside popup
            const statusIcon =
                p.current_status === 'approved' ? '/static/images/status_approved_green.png' :
                p.current_status === 'in_progress' ? '/static/images/status_in_progress_orange.png' :
                p.current_status === 'pending' ? '/static/images/status_pending_yellow.png' :
                p.current_status === 'new' ? '/static/images/status_new_blue.png' :
                p.current_status === 'rejected' ? '/static/images/status_rejected_red.png' :
                '/static/images/status_closed_grey.png';

            // Photo thumbnails
            const photoThumbnails = (p.photos || [])
                .map(url => `
                    <a href="${url}" target="_blank">
                        <img src="${url}"
                        style="width:75px;height:75px;object-fit:cover;
                               border:1px solid black;margin:2px;">
                    </a>
                `)
                .join('');

            // Build the popup HTML
            const popupHTML = `
                <b> <a href="/staff/report/${p.ticket_number}/" 
                    class="ticket-link"
                    style="color:#1976d2; text-decoration:underline;">
                    ${p.ticket_number}
                    </a>
                </b><br>
                Address: ${trimmedAddress}<br>
                Status: <img src='${statusIcon}' 
                    alt='${statusLabels[p.current_status] || p.current_status}' 
                    style="border:1px 
                            solid black;
                            border-radius:50%;
                            width:15px;
                            height:15px;
                            vertical-align:text-bottom;
                            margin-left:4px;"> ${statusLabels[p.current_status] || p.current_status}<br>
                Severity: ${severityLabels[p.severity] || p.severity}<br>
                Reported: ${createdDate}<br>
                Updated: ${updatedDate}<br>
                Notes: ${p.public_notes}<br>
                Photos:<br>
                ${photoThumbnails}
            `;
            marker.bindPopup(popupHTML);
            marker.on("click", function () {
                map.panTo(marker.getLatLng());
            });
        });
    }) 

    .catch(err => console.error("Error loading potholes:", err));

// the following section applies filters on map based on selected status from the tiles below the map

function filterStaffMarkers(statusValue) {
    const visibleMarkers = [];
    allStaffMarkers.forEach(marker => {
        const report = marker.reportData;
        const matchStatus = !statusValue || statusValue === 'all' || report.current_status === statusValue;
        if (matchStatus) {
            marker.addTo(map);
            visibleMarkers.push(marker);
        } else {
            map.removeLayer(marker);
        }
    });

    if (visibleMarkers.length > 0) {
        const group = L.featureGroup(visibleMarkers);
        map.fitBounds(group.getBounds(), { padding: [50, 50] });
    } else {
        map.setView(REGINA, 11);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.summary-card').forEach(card => {
        card.addEventListener('click', () => {
            const selectedStatus = card.dataset.status;
            document.querySelectorAll('.summary-card')
                .forEach(c => c.classList.remove('active'));
            card.classList.add('active');
            filterStaffMarkers(selectedStatus);
        });
    });
});