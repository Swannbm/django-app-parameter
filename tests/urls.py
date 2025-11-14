"""URL configuration for tests"""

from django.contrib import admin
from django.urls import path

# Register django_app_parameter with admin
admin.autodiscover()

urlpatterns = [
    path("admin/", admin.site.urls),
]
