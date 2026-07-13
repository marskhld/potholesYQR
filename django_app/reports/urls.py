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

from django.urls import path
from . import views

urlpatterns = [
    path('report/', views.submit_report, name='submit_report'),
    path('report/confirmation/<str:ticket>/', views.report_confirmation, name='report_confirmation'),
    path("", views.map_view, name="home"),
]