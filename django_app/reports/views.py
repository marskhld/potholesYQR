# Django shortcuts for loading pages, redirecting, and finding objects
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import PotholeReport

# Used to generate named URLs
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db import transaction
from django.urls import reverse

from .forms import PotholeReportForm, ResidentForm
from .models import (
    Photo,
    PotholeReport,
    Resident,
    Staff,
    StatusHistory,
)
from .utils import geocode_address

def map_view(request):
    return render(request, 'reports/map.html')
"""
def pothole_data(request):
    potholes = PotholeReport.objects.all().values(
        'id', 'ticket_number', 'created_date', 'updated_date', 'latitude', 'longitude', 'address', 'description', 'severity', 'current_status', 'public_notes'
    )
    return JsonResponse(list(potholes), safe=False)
"""
# load the photos for the map, too
def pothole_data(request):
    data = []
    for report in PotholeReport.objects.all():
        photos = [
            photo.file_path.url
            for photo in Photo.objects.filter(report=report)
        ]
        data.append({
            'id': report.id,
            'ticket_number': report.ticket_number,
            'created_date': report.created_date,
            'updated_date': report.updated_date,
            'latitude': report.latitude,
            'longitude': report.longitude,
            'address': report.address,
            'description': report.description,
            'severity': report.severity,
            'current_status': report.current_status,
            'public_notes': report.public_notes,
            'photos': photos
        })
    return JsonResponse(data, safe=False)

def submit_report(request):
    if request.method == "POST":
        resident_form = ResidentForm(request.POST)
        report_form = PotholeReportForm(request.POST, request.FILES)

        if resident_form.is_valid() and report_form.is_valid():
            # Geocode the address using the utility function
            address = report_form.cleaned_data["address"]
            coordinates = geocode_address(address)

            if coordinates is None:
                report_form.add_error(
                    "address",
                    "We couldn't locate this address. Please check the spelling or provide a more specific location.",
                )
            else:
                with (
                    transaction.atomic()
                ):  # ensure atomicity of the following operations
                    resident, _ = (
                        Resident.objects.get_or_create(  # checks if resident already exists (avoid duplicates)
                            email=resident_form.cleaned_data["email"],
                            defaults={
                                "name": resident_form.cleaned_data["name"],
                                "phone_number": resident_form.cleaned_data[
                                    "phone_number"
                                ],
                            },
                        )
                    )

                    report = report_form.save(commit=False)
                    report.resident = resident
                    report.latitude = coordinates["latitude"]
                    report.longitude = coordinates["longitude"]
                    report.save()

                    for photo in request.FILES.getlist("photos")[:5]:
                        Photo.objects.create(report=report, file_path=photo)

                send_mail(
                    subject="Pothole Report Confirmation",
                    message=f"Thank you for reporting the pothole. Your report has been received and is being processed. Your ticket number is {report.ticket_number}.",
                    from_email="noreply@potholesyqr.com",
                    recipient_list=[resident.email],
                    fail_silently=False,  # for debugging, will raise an error if email fails to send
                )
                # TODO: create email notification entry in the Notification model for record-keeping
                return redirect(
                    "report_confirmation", ticket=report.ticket_number
                )  # Redirect to a success page after submission

    else:
        resident_form = ResidentForm()
        report_form = PotholeReportForm()

    return render(
        request,
        "reports/submit_report.html",
        {
            "resident_form": resident_form,
            "report_form": report_form,
        },
    )

def report_confirmation(request, ticket):
    report = get_object_or_404(
        PotholeReport, ticket_number=ticket
    )  # if pothole report exists, show report. else, return 404 error
    return render(request, "reports/report_confirmation.html", {"report": report})

# Staff login page     DP
def staff_login(request):
    # If the user is already logged in and is a staff user,
    # send them directly to the staff dashboard.
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("staff_dashboard")

    # If the staff login form is submitted
    if request.method == "POST":
        # Get username entered in the login form
        username = request.POST.get("username")

        # Get password entered in the login form
        password = request.POST.get("password")

        # Check if username and password match a Django user
        user = authenticate(request, username=username, password=password)

        # If user exists and is marked as staff, allow login
        if user is not None and user.is_staff:
            # Log the staff user into the session
            login(request, user)

            # Send staff user to dashboard after login
            return redirect("staff_dashboard")

        # If login fails, show error on staff login page
        return render(
            request,
            "reports/staff_login.html",
            {"error": "Invalid staff username or password."},
        )

    # If page is opened normally using GET request,
    # simply display the staff login page
    return render(request, "reports/staff_login.html")

# Staff dashboard page
@login_required(login_url="staff_login")
def staff_dashboard(request):

    # If logged-in user is not staff, send them back to staff login
    if not request.user.is_staff:
        # Redirect non-staff users to staff login page
        return redirect("staff_login")

    # Get all submitted pothole reports from the database
    # select_related("resident") also fetches resident details with each report
    # order_by("-created_date") shows the newest submitted report first
    reports = PotholeReport.objects.select_related("resident").order_by("-created_date")

    # Count total number of submitted pothole reports
    total_reports = reports.count()

    # Prepare data to send from views.py to staff_dashboard.html
    context = {
        # Send all pothole reports to the dashboard template
        "reports": reports,
        # Send total report count to the dashboard template
        "total_reports": total_reports,
    }

    # Load staff_dashboard.html and pass report data to it
    return render(request, "reports/staff_dashboard.html", context)

# Staff report detail page
# Only authenticated staff users can open and update a report
@login_required(login_url="staff_login")
def staff_report_detail(request, ticket):

    # Prevent authenticated non-staff users from accessing the page
    if not request.user.is_staff:
        return redirect("staff_login")

    # Find one report using its unique ticket number
    # select_related gets the connected resident efficiently
    # prefetch_related gets the connected photos efficiently
    report = get_object_or_404(
        PotholeReport.objects.select_related("resident").prefetch_related("photo_set"),
        ticket_number=ticket,
    )

    # Get allowed status options from the model
    status_choices = PotholeReport.STATUS_CHOICES

    # Get allowed severity options from the severity field
    severity_choices = PotholeReport._meta.get_field("severity").choices

    # Create sets of valid database values for validation
    valid_statuses = {value for value, _ in status_choices}

    valid_severities = {value for value, _ in severity_choices}

    # No error is shown when the page first opens
    update_error = None

    if request.method == "POST":
        # Get the selected status from the form
        new_status = request.POST.get(
            "current_status",
            report.current_status,
        )

        # Get the selected severity from the form
        new_severity = request.POST.get(
            "severity",
            report.severity,
        )

        # Get and clean the internal staff notes
        new_staff_notes = request.POST.get(
            "staff_notes",
            "",
        ).strip()

        # Get and clean the public/resolution notes
        new_public_notes = request.POST.get(
            "public_notes",
            "",
        ).strip()

        # Check whether the submitted status is valid
        if new_status not in valid_statuses:
            update_error = "The selected report status is invalid."

        # Check whether the submitted severity is valid
        elif new_severity not in valid_severities:
            update_error = "The selected severity is invalid."

        # Continue when all submitted values are valid
        else:
            # Store the previous values before updating the report
            old_status = report.current_status
            old_severity = report.severity
            old_staff_notes = report.staff_notes
            old_public_notes = report.public_notes

            # Check whether staff changed anything
            changes_made = (
                old_status != new_status
                or old_severity != new_severity
                or old_staff_notes != new_staff_notes
                or old_public_notes != new_public_notes
            )

            # Generate the current detail-page URL
            detail_url = reverse(
                "staff_report_detail",
                kwargs={"ticket": report.ticket_number},
            )

            if changes_made:
                try:
                    # Keep the report update and history record together
                    with transaction.atomic():
                        # state transition machine - for state changes only
                        if old_status != new_status:
                            if new_status == "approved":
                                report.approve(severity=new_severity)
                            elif new_status == "rejected":
                                report.reject()
                            elif new_status == "in_progress":
                                report.start_work()
                            elif new_status == "pending":
                                report.pend()
                            elif new_status == "closed":
                                report.close()
                            elif new_status == "new":
                                report.prevent_transition_to_new()

                        # update & save remaining report info
                        report.severity = new_severity
                        report.staff_notes = new_staff_notes
                        report.public_notes = new_public_notes
                        report.save()

                    # Find or create a Staff profile
                    staff_profile, _ = Staff.objects.get_or_create(
                        username=request.user.username,
                        defaults={
                            "name": (
                                request.user.get_full_name() or request.user.username
                            )
                        },
                    )

                    StatusHistory.objects.create(
                        report=report,
                        old_status=old_status,
                        new_status=new_status,
                        changed_by=staff_profile,
                        staff_notes=new_staff_notes,
                        public_notes=new_public_notes,
                    )

                    return redirect(f"{detail_url}?updated=1")  # successful!

                except ValueError as e:  # catch state transition errors
                    update_error = str(e)

            else:
                return redirect(
                    detail_url
                )  # Return without success message if nothing changed

    # Load all previous staff updates for this report
    status_history = (
        StatusHistory.objects.filter(report=report)
        .select_related("changed_by")
        .order_by("-changed_at")
    )

    # Create a mapping from stored status codes to readable labels
    status_label_map = dict(PotholeReport.STATUS_CHOICES)

    # Add a readable status label to every history record
    for entry in status_history:
        entry.display_status = status_label_map.get(
            entry.new_status,
            entry.new_status,
        )

    # Prepare information for staff_report_detail.html
    context = {
        "report": report,
        "status_choices": status_choices,
        "severity_choices": severity_choices,
        "status_history": status_history,
        "update_error": update_error,
        "update_success": request.GET.get("updated") == "1" and not update_error,
    }

    # Display the staff report detail template
    return render(
        request,
        "reports/staff_report_detail.html",
        context,
    )

# Staff logout function
def staff_logout(request):
    # End current staff login session
    logout(request)

    # Send user back to staff login page
    return redirect("staff_login")
