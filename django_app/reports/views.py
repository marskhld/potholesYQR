from django.shortcuts import render, redirect
from .utils import geocode_address
from .forms import ResidentForm, PotholeReportForm
from .models import Resident, PotholeReport, Photo
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import get_object_or_404

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