"""
URL configuration for demo_project project.
"""
from django.contrib import admin
from django.urls import path

from demo_project.views import HomeView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
]
