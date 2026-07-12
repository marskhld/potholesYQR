from django.shortcuts import render
from django.http import JsonResponse
from .models import PotholeReport

def map_view(request):
    return render(request, 'reports/map.html')

def pothole_data(request):
    potholes = PotholeReport.objects.all().values(
        'id', 'latitude', 'longitude', 'description', 'severity', 'current_status'
    )
    return JsonResponse(list(potholes), safe=False)
