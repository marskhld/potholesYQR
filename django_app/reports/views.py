from django.shortcuts import render, redirect, get_object_or_404 # Used to check username and password for staff login -DP 
from .utils import geocode_address
from .forms import ResidentForm, PotholeReportForm
from .models import Resident, PotholeReport, Photo
from django.core.mail import send_mail
from django.db import transaction

from django.contrib.auth import authenticate

# Used to log in staff users after successful authentication
from django.contrib.auth import login

# Used to log out staff users
from django.contrib.auth import logout

# Used to protect staff dashboard so only logged-in users can access it
from django.contrib.auth.decorators import login_required

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
@login_required(login_url="staff_login")
def staff_dashboard(request):

    # If logged-in user is not staff, send them back to staff login
    if not request.user.is_staff:

        # Redirect non-staff users to staff login page
        return redirect("staff_login")

    # Get all submitted pothole reports from the database
    # select_related("resident") also fetches resident details with each report
    # order_by("-created_date") shows the newest submitted report first
    reports = PotholeReport.objects.select_related("resident").all().order_by("-created_date")

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

# Staff logout function
def staff_logout(request):
    # End current staff login session
    logout(request)

    # Send user back to staff login page
    return redirect("staff_login")