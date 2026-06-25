from django.contrib import admin
from .models import Resident, Staff, PotholeReport, Photo, Notification, StatusHistory

# Register your models here - this sets up Admin interface/panel/dashboard

admin.site.register(Resident)
admin.site.register(Staff)
admin.site.register(PotholeReport)
admin.site.register(Photo)
admin.site.register(Notification)
admin.site.register(StatusHistory)