

# Django shortcuts for loading pages, redirecting, and finding objects
from django.shortcuts import render, redirect, get_object_or_404
# Used for multi-field OR filtering in the dashboard search
from django.db.models import Q, Count

# Used to generate named URLs
from django.urls import reverse

# Used to send resident confirmation emails
from django.core.mail import send_mail

# Used to validate staff-edited email addresses
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

# Used to keep related database operations together
from django.db import transaction

# Django authentication functions
from django.contrib.auth import authenticate, login, logout

# Protects staff pages from unauthenticated access
from django.contrib.auth.decorators import login_required

# Project utility and forms
from .utils import geocode_address
from .forms import ResidentForm, PotholeReportForm

# Database models used by resident and staff pages
from .models import (
    Resident,
    Staff,
    PotholeReport,
    Photo,
    StatusHistory,
)

# Create your views here.
def submit_report(request):
    if request.method == 'POST':
        resident_form = ResidentForm(request.POST)
        report_form = PotholeReportForm(request.POST, request.FILES)

        if resident_form.is_valid() and report_form.is_valid():

            # Geocode the address using the utility function
            address = report_form.cleaned_data['address']
            coordinates = geocode_address(address)
            
            if coordinates is None:
                report_form.add_error(
                    'address',
                    "We couldn't locate this address. Please check the spelling or provide a more specific location."
                )
            else:
                with transaction.atomic():  # ensure atomicity of the following operations
                    resident, _ = Resident.objects.get_or_create( # checks if resident already exists (avoid duplicates)
                        email=resident_form.cleaned_data['email'],
                            defaults={
                                'name': resident_form.cleaned_data['name'],
                                'phone_number': resident_form.cleaned_data['phone_number']
                            }
                    )

                    report = report_form.save(commit=False)
                    report.resident = resident
                    report.latitude = coordinates['latitude']
                    report.longitude = coordinates['longitude']
                    report.save()
    
                    for photo in request.FILES.getlist('photos')[:5]:
                        Photo.objects.create(report=report, file_path=photo)

                send_mail(
                    subject='Pothole Report Confirmation',
                    message=f'Thank you for reporting the pothole. Your report has been received and is being processed. Your ticket number is {report.ticket_number}.',
                    from_email='noreply@potholesyqr.com',
                    recipient_list=[resident.email],
                    fail_silently=False, # for debugging, will raise an error if email fails to send
                )
                # TODO: create email notification entry in the Notification model for record-keeping
                return redirect('report_confirmation', ticket=report.ticket_number)  # Redirect to a success page after submission
            
    else:
        resident_form = ResidentForm()
        report_form = PotholeReportForm()
            
    return render(request, 'reports/submit_report.html', {
        'resident_form': resident_form,
        'report_form': report_form,
    })
        
def report_confirmation(request, ticket):
    report = get_object_or_404(PotholeReport, ticket_number=ticket) # if pothole report exists, show report. else, return 404 error
    return render(request, 'reports/report_confirmation.html', {'report': report})


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
        return render(request, "reports/staff_login.html", {
            "error": "Invalid staff username or password."
        })

    # If page is opened normally using GET request,
    # simply display the staff login page
    return render(request, "reports/staff_login.html")


# Staff dashboard page
# Staff dashboard page
@login_required(login_url="staff_login")
def staff_dashboard(request):

    # Prevent authenticated non-staff users from opening the dashboard
    if not request.user.is_staff:
        return redirect("staff_login")

    # Load all reports and their connected resident records
    reports = (
        PotholeReport.objects
        .select_related("resident")
        .order_by("-created_date")
    )

    # Count all reports and reports in each status
    report_counts = PotholeReport.objects.aggregate(
        total_reports=Count("id"),

        new_reports=Count(
            "id",
            filter=Q(current_status="new"),
        ),

        approved_reports=Count(
            "id",
            filter=Q(current_status="approved"),
        ),

        rejected_reports=Count(
            "id",
            filter=Q(current_status="rejected"),
        ),

        in_progress_reports=Count(
            "id",
            filter=Q(current_status="in_progress"),
        ),

        pending_reports=Count(
            "id",
            filter=Q(current_status="pending"),
        ),

        closed_reports=Count(
            "id",
            filter=Q(current_status="closed"),
        ),
    )

    # Read dashboard filters from the URL
    search = request.GET.get(
        "search",
        "",
    ).strip()

    status = request.GET.get(
        "status",
        "",
    ).strip()

    submitted_date = request.GET.get(
        "submitted_date",
        "",
    ).strip()

    # Search across ticket, resident, email, phone, and address
    if search:
        reports = reports.filter(
            Q(ticket_number__icontains=search)
            | Q(resident__name__icontains=search)
            | Q(resident__email__icontains=search)
            | Q(resident__phone_number__icontains=search)
            | Q(address__icontains=search)
        )

    # Filter by exact report status
    if status:
        reports = reports.filter(
            current_status=status,
        )

    # Filter by submitted calendar date
    if submitted_date:
        reports = reports.filter(
            created_date__date=submitted_date,
        )

    # Count reports remaining after filters are applied
    filtered_reports = reports.count()

    context = {
        # Filtered report list displayed in the table
        "reports": reports,

        # Number of reports currently shown in the table
        "filtered_reports": filtered_reports,

        # Values used by the status filter
        "status_choices": PotholeReport.STATUS_CHOICES,

        # Preserve the selected filter values
        "filters": {
            "search": search,
            "status": status,
            "submitted_date": submitted_date,
        },

        # Add all report totals to the template
        **report_counts,
    }

    return render(
        request,
        "reports/staff_dashboard.html",
        context,
    )

# Staff report detail page
# Authorized staff can review and update report information
@login_required(login_url="staff_login")
def staff_report_detail(request, ticket):

    # Prevent authenticated non-staff users from accessing the page
    if not request.user.is_staff:
        return redirect("staff_login")

    # Load the report, connected resident, and submitted photos
    report = get_object_or_404(
        PotholeReport.objects
        .select_related("resident")
        .prefetch_related("photo_set"),
        ticket_number=ticket,
    )

    resident = report.resident

    # Get only the valid next statuses for the report's current state.
    allowed_status_choices = report.get_allowed_status_choices()

    # Include the current status so staff can save without changing it.
    status_choices = [
        (
            report.current_status,
            report.get_current_status_display(),
        ),
        *allowed_status_choices,
    ]

    # Severity choices from the model
    severity_choices = PotholeReport.SEVERITY_CHOICES

    # Valid values used for server-side validation
    valid_statuses = {
        value for value, _ in status_choices
    }

    valid_severities = {
        value for value, _ in severity_choices
    }

    # True when at least one next status is available
    has_available_transitions = bool(
        allowed_status_choices
    )

    # Display submitted details in edit mode with ?edit=1
    edit_mode = request.GET.get("edit") == "1"

    update_error = None

    if request.method == "POST":

        # Read resident information
        new_resident_name = request.POST.get(
            "resident_name",
            resident.name,
        ).strip()

        new_resident_email = request.POST.get(
            "resident_email",
            resident.email,
        ).strip()

        new_resident_phone = request.POST.get(
            "resident_phone",
            resident.phone_number,
        ).strip()

        # Read report information
        new_address = request.POST.get(
            "address",
            report.address,
        ).strip()

        new_description = request.POST.get(
            "description",
            report.description,
        ).strip()

        new_status = request.POST.get(
            "current_status",
            report.current_status,
        ).strip()

        new_severity = request.POST.get(
            "severity",
            report.severity,
        ).strip()

        new_staff_notes = request.POST.get(
            "staff_notes",
            report.staff_notes,
        ).strip()

        new_public_notes = request.POST.get(
            "public_notes",
            report.public_notes,
        ).strip()

        new_edit_reason = request.POST.get(
            "edit_reason",
            "",
        ).strip()

        # Basic validation
        if not new_resident_name:
            update_error = "Resident name cannot be empty."

        elif not new_resident_email:
            update_error = "Resident email cannot be empty."

        elif not new_resident_phone:
            update_error = "Resident phone number cannot be empty."

        elif not new_address:
            update_error = "Report address cannot be empty."

        elif not new_description:
            update_error = "Report description cannot be empty."

        elif new_status not in valid_statuses:
            update_error = (
                "The selected status transition is not allowed "
                "from the report's current status."
            )

        elif new_severity not in valid_severities:
            update_error = "The selected severity is invalid."

        else:
            try:
                validate_email(new_resident_email)

            except ValidationError:
                update_error = (
                    "Enter a valid resident email address."
                )

        if update_error is None:

            # Save previous values for comparison and history
            old_resident_name = resident.name
            old_resident_email = resident.email
            old_resident_phone = resident.phone_number

            old_address = report.address
            old_description = report.description
            old_latitude = report.latitude
            old_longitude = report.longitude
            old_status = report.current_status
            old_severity = report.severity
            old_staff_notes = report.staff_notes
            old_public_notes = report.public_notes

            submitted_details_changed = (
                old_resident_name != new_resident_name
                or old_resident_email != new_resident_email
                or old_resident_phone != new_resident_phone
                or old_address != new_address
                or old_description != new_description
            )

            address_changed = (
                old_address != new_address
            )

            new_coordinates = None

            if address_changed:
                new_coordinates = geocode_address(
                    new_address
                )

                if new_coordinates is None:
                    update_error = (
                        "The updated address could not be located. "
                        "Please enter a more specific address."
                    )

            if (
                update_error is None
                and submitted_details_changed
                and not new_edit_reason
            ):
                update_error = (
                    "Enter a reason when changing submitted "
                    "report details."
                )

            if update_error is None:

                change_messages = []

                if old_resident_name != new_resident_name:
                    change_messages.append(
                        f'Resident name changed from '
                        f'"{old_resident_name}" to '
                        f'"{new_resident_name}".'
                    )

                if old_resident_email != new_resident_email:
                    change_messages.append(
                        f'Resident email changed from '
                        f'"{old_resident_email}" to '
                        f'"{new_resident_email}".'
                    )

                if old_resident_phone != new_resident_phone:
                    change_messages.append(
                        f'Resident phone changed from '
                        f'"{old_resident_phone}" to '
                        f'"{new_resident_phone}".'
                    )

                if old_address != new_address:
                    change_messages.append(
                        f'Address changed from '
                        f'"{old_address}" to '
                        f'"{new_address}".'
                    )

                if old_description != new_description:
                    change_messages.append(
                        "Report description was updated."
                    )

                if old_status != new_status:
                    old_status_label = dict(
                        PotholeReport.STATUS_CHOICES
                    ).get(old_status, old_status)

                    new_status_label = dict(
                        PotholeReport.STATUS_CHOICES
                    ).get(new_status, new_status)

                    change_messages.append(
                        f'Status changed from '
                        f'"{old_status_label}" to '
                        f'"{new_status_label}".'
                    )

                if old_severity != new_severity:
                    old_severity_label = dict(
                        PotholeReport.SEVERITY_CHOICES
                    ).get(old_severity, old_severity)

                    new_severity_label = dict(
                        PotholeReport.SEVERITY_CHOICES
                    ).get(new_severity, new_severity)

                    change_messages.append(
                        f'Severity changed from '
                        f'"{old_severity_label}" to '
                        f'"{new_severity_label}".'
                    )

                if old_staff_notes != new_staff_notes:
                    change_messages.append(
                        "Internal staff notes were updated."
                    )

                if old_public_notes != new_public_notes:
                    change_messages.append(
                        "Public resolution notes were updated."
                    )

                if new_edit_reason:
                    change_messages.append(
                        f'Edit reason: "{new_edit_reason}".'
                    )

                changes_made = bool(change_messages)

                detail_url = reverse(
                    "staff_report_detail",
                    kwargs={
                        "ticket": report.ticket_number,
                    },
                )

                if changes_made:

                    try:
                        with transaction.atomic():

                            # Update resident information
                            resident.name = new_resident_name
                            resident.email = new_resident_email
                            resident.phone_number = (
                                new_resident_phone
                            )
                            resident.save()

                            # Update report information other than status
                            report.address = new_address
                            report.description = new_description
                            report.severity = new_severity
                            report.staff_notes = new_staff_notes
                            report.public_notes = new_public_notes

                            if address_changed:
                                report.latitude = (
                                    new_coordinates["latitude"]
                                )
                                report.longitude = (
                                    new_coordinates["longitude"]
                                )

                                change_messages.append(
                                    f"Coordinates recalculated from "
                                    f"{old_latitude}, "
                                    f"{old_longitude} to "
                                    f"{report.latitude}, "
                                    f"{report.longitude}."
                                )

                            # Use the State pattern for status changes
                            if old_status != new_status:
                                report.transition_to(
                                    new_status,
                                    severity=new_severity,
                                )
                            else:
                                report.save()

                            # Find or create staff profile
                            staff_profile, _ = (
                                Staff.objects.get_or_create(
                                    username=(
                                        request.user.username
                                    ),
                                    defaults={
                                        "name": (
                                            request.user
                                            .get_full_name()
                                            or request.user.username
                                        )
                                    },
                                )
                            )

                            # Determine activity category
                            if address_changed:
                                activity_type = (
                                    "location_updated"
                                )

                            elif submitted_details_changed:
                                activity_type = (
                                    "details_updated"
                                )

                            elif old_status != new_status:
                                activity_type = (
                                    "status_updated"
                                )

                            elif old_severity != new_severity:
                                activity_type = (
                                    "severity_updated"
                                )

                            else:
                                activity_type = (
                                    "notes_updated"
                                )

                            StatusHistory.objects.create(
                                report=report,
                                activity_type=activity_type,
                                old_status=old_status,
                                new_status=new_status,
                                changed_by=staff_profile,
                                change_details=" ".join(
                                    change_messages
                                ),
                                staff_notes=new_staff_notes,
                                public_notes=new_public_notes,
                            )

                    except ValueError as error:
                        update_error = str(error)

                    else:
                        return redirect(
                            f"{detail_url}?updated=1"
                        )

                else:
                    return redirect(detail_url)

        if update_error:
            edit_mode = True

    # Load activity history
    status_history = (
        StatusHistory.objects
        .filter(report=report)
        .select_related("changed_by")
        .order_by("-changed_at")
    )

    status_label_map = dict(
        PotholeReport.STATUS_CHOICES
    )

    for entry in status_history:
        entry.display_status = status_label_map.get(
            entry.new_status,
            entry.new_status,
        )

    context = {
        "report": report,
        "status_choices": status_choices,
        "severity_choices": severity_choices,
        "status_history": status_history,
        "update_error": update_error,
        "update_success": (
            request.GET.get("updated") == "1"
        ),
        "edit_mode": edit_mode,
        "has_available_transitions": (
            has_available_transitions
        ),
    }

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