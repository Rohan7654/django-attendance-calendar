"""
URL configuration for example project.
"""

from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.calendar_demo, name="calendar_demo"),
    path("dark/", views.calendar_dark, name="calendar_dark"),
    path("dashboard/", views.dashboard_demo, name="dashboard_demo"),
    path("all-features/", views.all_features, name="all_features"),
    path("screenshots/", views.screenshots, name="screenshots"),
]
