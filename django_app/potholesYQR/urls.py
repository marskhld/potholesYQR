# .py comment
# Course:      CS 476
# Project:     PotholesYQR
# File:        urls.py
# Description: Direct browser to correct location (project-level)
# 
# Authors:
#     Maria Khalid
#     Opinder Kaur
#     Dakshkumar Patel
#     Christopher Taylor
 
"""
URL configuration for potholesYQR project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from reports import views  
from django.urls import include, path

urlpatterns = [
    #Admin site
    path('admin/', admin.site.urls),

    #Map and API
    path('map/', views.map_view, name='map'),
    path('api/potholes/', views.pothole_data, name='pothole_data'),

    #Reports app routes
    path("", include("reports.urls")),  # URLs for reports app - for development side
    path("api/", include("reports.urls")),  # URLs for reports app - for production side
]

# Serve media files during development
urlpatterns += static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)