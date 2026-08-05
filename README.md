<p align="center">
<img src="README-assets/README-logo-light.png#gh-light-mode-only" alt="potholesYQR Logo" width="450">
<img src="README-assets/README-logo.png#gh-dark-mode-only" alt="potholesYQR Logo" width="450">
</p>

# potholesYQR

#### SPOT IT. REPORT IT. FIX IT.

potholesYQR is an enhanced pothole reporting web application for residents of the City of Regina. potholesYQR relies on OpenStreetMaps and the Leaflet.js scripts to provide a visual interface for locating and reporting potholes. The intention is to provide a transparent process for residents to be involved in the reporting and tracking of potholes.

## Screenshots

| Screenshot | Description | Screenshot | Description |
|------------|-------------|------------|-------------|
| <a href="README-assets/potholesYQR-screenshot-Map.png"><img src="README-assets/potholesYQR-screenshot-Map.png" alt="potholesYQR Pothole Map" width="100"></a> | View and search pothole locations | <a href="README-assets/potholesYQR-screenshot-Map-popup.png"><img src="README-assets/potholesYQR-screenshot-Map-popup.png" alt="potholesYQR Pothole Popup" width="100"></a> | Pothole Report Popup |
| <a href="README-assets/potholesYQR-screenshot-Map-Report.png"><img src="README-assets/potholesYQR-screenshot-Map-Report.png" alt="potholesYQR Submit Pothole" width="100"></a> | Submit Pothole Report from Map | <a href="README-assets/potholesYQR-screenshot-Report1.png"><img src="README-assets/potholesYQR-screenshot-Report1.png" alt="potholesYQR New Pothole Report Form 1" width="100"></a> | New Pothole Report Form 1 |
| <a href="README-assets/potholesYQR-screenshot-Report2.png"><img src="README-assets/potholesYQR-screenshot-Report2.png" alt="potholesYQR New Pothole Report Form 2" width="100"></a> | New Pothole Report Form 2 | <a href="README-assets/potholesYQR-screenshot-Report3.png"><img src="README-assets/potholesYQR-screenshot-Report3.png" alt="potholesYQR Data Entry" width="100"></a> | Pothole Report Form Data Entry |
| <a href="README-assets/potholesYQR-screenshot-Report4.png"><img src="README-assets/potholesYQR-screenshot-Report4.png" alt="potholesYQR Photo Upload" width="100"></a> | Photo Upload | <a href="README-assets/potholesYQR-screenshot-Report-Confirmation.png"><img src="README-assets/potholesYQR-screenshot-Report-Confirmation.png" alt="potholesYQR Confirmation" width="100"></a> | Confirmation |
| <a href="README-assets/potholesYQR-screenshot-Staff-Login.png"><img src="README-assets/potholesYQR-screenshot-Staff-Login.png" alt="potholesYQR Staff Login" width="100"></a> | Staff Login | <a href="README-assets/potholesYQR-screenshot-Staff-Dashboard1.png"><img src="README-assets/potholesYQR-screenshot-Staff-Dashboard1.png" alt="potholesYQR Staff Dashboard 1" width="100"></a> | Staff Dashboard |
| <a href="README-assets/potholesYQR-screenshot-Report-Review.png"><img src="README-assets/potholesYQR-screenshot-Report-Review.png" alt="potholesYQR Staff Report Review" width="100"></a> | Staff Report Review | <a href="README-assets/potholesYQR-screenshot-Report-Approved.png"><img src="README-assets/potholesYQR-screenshot-Report-Approved.png" alt="potholesYQR Staff Approval" width="100"></a> | Staff Approval |
| <a href="README-assets/potholesYQR-screenshot-Staff-Dashboard-Search.png"><img src="README-assets/potholesYQR-screenshot-Staff-Dashboard-Search.png" alt="potholesYQR Staff Dashboard Search and Status Buttons" width="100"></a> | Staff Search and Status Buttons | | |

## Features

| Feature | Description |
|----------|-------------|
| Interactive Map | View and search pothole locations |
| Report Submission | Residents can submit pothole reports |
| Staff Dashboard | Manage report statuses |

The main web page is a resident facing map that allows residents to review the current potholes in the City of Regina. Potholes are shown with different colour pins depending on their status (Approved, In Progress, Pending). Residents are also able to search existing potholes by Report Number, Status, Severity, and date range.

Residents can also use the main interface to initiate new pothole reports. Once they pinpoint the pothole location and provide their contact details along with optional pothole photos, they receive a confirmation message in the browser as well as an email message when the status changes to Approved beyond.

City staff are able to logon to the Staff Dashboard where they can review all current pothole reports. There is a similar search and filter ability along with a map and table of all pothole reports. From this interface, staff are able to create their own pothole reports as well as update existing reports.

## Technology Stack

- [![Ubuntu](https://img.shields.io/badge/Ubuntu-Linux-red)](https://ubuntu.com/) virtual machine hosted by the [Department of Computer Science](https://www.uregina.ca/academics/programs/science/computer-science.html) at the [University of Regina](https://www.uregina.ca)
- [![Django 5](https://img.shields.io/badge/Django-5-green)](https://www.djangoproject.com/)
- [![Python 3.12](https://img.shields.io/badge/Python-3.12-green)](https://www.python.org/)
- [![MySQL](https://img.shields.io/badge/MySQL-Database-blue)](https://www.mysql.com/)
- [![Leaflet.js](https://img.shields.io/badge/Leaflet.js-Maps-brightgreen)](https://leafletjs.com/)
- [![HTML5](https://img.shields.io/badge/HTML-5-red)](https://html.spec.whatwg.org/multipage/) [![CSS3](https://img.shields.io/badge/CSS-3-purple)](https://www.w3.org/TR/css/#css) [![JavaScript](https://img.shields.io/badge/JavaScript-TC39-orange)](https://ecma-international.org/publications-and-standards/standards/ecma-262/)

We have used the Django Model-View-Template (MVT) which is the Django version of the Model-View-Controller (MVC) architecture. The following table illustrates how MVC maps to MVT for the potholesYQR website application:

| MVC | MVT | potholesYQR |
|-----|-----|-------------|
| Model | Model | models.py classes PotholeReport, Photo, Notification, StatusHistory |
| View | Template | Leaflet.js map, staff_dashboard.html, submit_report.html |
| Controller | View | views.py functions submit_report(), staff_login(), staff_dashboard(), etc |

## Installation

We built this project using VS Code and pushed our changes to Github. Once we were satisfied with the code we pulled the repository onto our production web server.

The website can be reached at http://www.student01.cs.uregina.ca/api while connected to the University of Regina's network. Off-campus access requires a [VPN connection](https://www.uregina.ca/is/tech-notes/technote569.html).

The Staff Login is accessed at http://www.student01.cs.uregina.ca/api/staff/login/ (credentials will be provided to the instructor) and once logged in, the Staff Dashboard is accessed at http://www.student01.cs.uregina.ca/api/staff/dashboard.

## Team Members

- [Maria Khalid](https://github.com/marskhld)
- [Dakshkumar Patel](https://github.com/Daksh2429)
- [Opinder Kaur](https://github.com/O-Kaur)
- [Christopher Taylor](https://github.com/taylorc-git)

## Thanks

Thank you to [Brent Zeiben](https://www.uregina.ca/science/computer-science/directory/zeiben-brent.html) of the [RITS](https://www.uregina.ca/is/research-it.html) team at the [University of Regina](https://www.uregina.ca) for all his help with the server setup and willingness to fix things that needed fixing along the way.
