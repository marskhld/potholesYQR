from django.urls import path
from . import views

urlpatterns = [
    path('report/', views.submit_report, name='submit_report'),
    path('report/confirmation/<str:ticket>/', views.report_confirmation, name='report_confirmation'),
]