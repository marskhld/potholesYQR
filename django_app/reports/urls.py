# Course:      CS 476
# Project:     PotholesYQR
# File:        reports/urls.py
# Description: Direct browser to correct location (application-level)
# 
# Authors:
#     Maria Khalid
#     Opinder Kaur
#     Dakshkumar Patel
#     Christopher Taylor

from django.urls import path   # Import path so Django can create URL routes
from . import views            # Import views.py so each URL can connect to a view function      


# List of all URL routes inside the reports app
urlpatterns = [
    # resident pothole report
    # Browser URL: http://127.0.0.1:8000/report/
    path('report/', views.submit_report, name='submit_report'),

    # report confirmation page
    # Browser URL example: http://127.0.0.1:8000/report/confirmation/YQR-123456/
    path('report/confirmation/<str:ticket>/', views.report_confirmation, name='report_confirmation'),
    path("", views.map_view, name="home"),
    
    # staff login page
    # URL: http://127.0.0.1:8000/staff/login/
    path('staff/login/', views.staff_login, name='staff_login'),

    # staff dashboard page after successful login
    # URL: http://127.0.0.1:8000/staff/dashboard/
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),

    # Staff detail page for one selected report
    # Example: /staff/report/YQR-12345678/
    path(
        "staff/report/<str:ticket>/",
        views.staff_report_detail,
        name="staff_report_detail",
    ),

    # staff logout route
    # URL: http://127.0.0.1:8000/staff/logout/
    path('staff/logout/', views.staff_logout, name='staff_logout'),
]