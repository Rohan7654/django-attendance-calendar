"""
Demo views for attendance calendar examples.
"""

from django.shortcuts import render
from datetime import date, timedelta
import random


def get_sample_attendance():
    """Generate sample attendance data for the current month."""
    today = date.today()
    year = today.year
    month = today.month

    data = {}
    statuses = [
        "present",
        "present",
        "present",
        "present",
        "absent",
        "late",
        "half_day",
        "leave",
    ]

    for day in range(1, 29):
        date_str = f"{year}-{month:02d}-{day:02d}"
        data[date_str] = random.choice(statuses)

    return data


def get_sample_dashboard():
    """Generate sample dashboard data with multiple employees."""
    employees = [
        {"id": "1", "name": "John Doe", "department": "Engineering"},
        {"id": "2", "name": "Jane Smith", "department": "Design"},
        {"id": "3", "name": "Mike Johnson", "department": "Engineering"},
        {"id": "4", "name": "Sarah Wilson", "department": "Marketing"},
        {"id": "5", "name": "Tom Brown", "department": "Design"},
        {"id": "6", "name": "Emily Davis", "department": "Engineering"},
    ]

    for emp in employees:
        emp["attendance"] = get_sample_attendance()

    return {"employees": employees}


def calendar_demo(request):
    """Basic calendar demo - light theme."""
    attendance_data = get_sample_attendance()

    return render(
        request,
        "demo/calendar_demo.html",
        {
            "attendance_data": attendance_data,
        },
    )


def calendar_dark(request):
    """Calendar demo - dark theme."""
    attendance_data = get_sample_attendance()

    return render(
        request,
        "demo/calendar_dark.html",
        {
            "attendance_data": attendance_data,
        },
    )


def dashboard_demo(request):
    """Multi-person dashboard demo."""
    dashboard_data = get_sample_dashboard()

    return render(
        request,
        "demo/dashboard_demo.html",
        {
            "dashboard_data": dashboard_data,
        },
    )


def all_features(request):
    """Demo showcasing all features."""
    # Sample avatar URL (using placeholder service)
    avatar_url = "https://i.pravatar.cc/150?img=12"

    attendance_data = {
        "2024-10-01": {"status": "present", "note": "On time", "avatar": avatar_url},
        "2024-10-02": {"status": "present", "note": "On time", "avatar": avatar_url},
        "2024-10-03": {"status": "late", "note": "30 min late", "avatar": avatar_url},
        "2024-10-04": {"status": "present", "note": "On time", "avatar": avatar_url},
        "2024-10-05": {"status": "holiday", "note": "National Holiday"},
        "2024-10-06": {"status": "holiday", "note": "Weekend"},
        "2024-10-07": {"status": "present", "note": "On time", "avatar": avatar_url},
        "2024-10-08": {"status": "absent", "note": "Sick leave", "avatar": avatar_url},
        "2024-10-09": {"status": "absent", "note": "Sick leave", "avatar": avatar_url},
        "2024-10-10": {"status": "present", "note": "On time", "avatar": avatar_url},
        "2024-10-11": {
            "status": "half_day",
            "note": "Left early",
            "avatar": avatar_url,
        },
        "2024-10-12": {
            "status": "leave",
            "note": "Personal leave",
            "avatar": avatar_url,
        },
        "2024-10-13": {"status": "holiday", "note": "Weekend"},
        "2024-10-14": {"status": "present", "note": "On time", "avatar": avatar_url},
        "2024-10-15": {"status": "present", "note": "On time", "avatar": avatar_url},
    }

    # Avatar-only data for specific demo
    avatar_data = {
        "2024-10-01": {
            "status": "present",
            "avatar": "https://i.pravatar.cc/150?img=1",
        },
        "2024-10-02": {
            "status": "present",
            "avatar": "https://i.pravatar.cc/150?img=2",
        },
        "2024-10-03": {"status": "late", "avatar": "https://i.pravatar.cc/150?img=3"},
        "2024-10-04": {
            "status": "present",
            "avatar": "https://i.pravatar.cc/150?img=4",
        },
        "2024-10-05": {"status": "holiday"},
        "2024-10-06": {"status": "holiday"},
        "2024-10-07": {
            "status": "present",
            "avatar": "https://i.pravatar.cc/150?img=5",
        },
        "2024-10-08": {"status": "absent", "avatar": "https://i.pravatar.cc/150?img=6"},
        "2024-10-09": {"status": "absent", "avatar": "https://i.pravatar.cc/150?img=7"},
        "2024-10-10": {
            "status": "present",
            "avatar": "https://i.pravatar.cc/150?img=8",
        },
        "2024-10-11": {
            "status": "half_day",
            "avatar": "https://i.pravatar.cc/150?img=9",
        },
        "2024-10-12": {"status": "leave", "avatar": "https://i.pravatar.cc/150?img=10"},
        "2024-10-13": {"status": "holiday"},
        "2024-10-14": {
            "status": "present",
            "avatar": "https://i.pravatar.cc/150?img=11",
        },
        "2024-10-15": {
            "status": "present",
            "avatar": "https://i.pravatar.cc/150?img=12",
        },
    }

    custom_statuses = {
        "wfh": {"color": "#10b981", "label": "Work From Home"},
        "training": {"color": "#06b6d4", "label": "Training Day"},
    }

    return render(
        request,
        "demo/all_features.html",
        {
            "attendance_data": attendance_data,
            "avatar_data": avatar_data,
            "custom_statuses": custom_statuses,
        },
    )


def screenshots(request):
    """Screenshot-ready page with organized sections."""
    # Use fixed October 2024 data for consistent screenshots
    attendance_data = {
        "2024-10-01": "present",
        "2024-10-02": "present",
        "2024-10-03": "late",
        "2024-10-04": "present",
        "2024-10-05": "holiday",
        "2024-10-06": "holiday",
        "2024-10-07": "present",
        "2024-10-08": "absent",
        "2024-10-09": "present",
        "2024-10-10": "half_day",
        "2024-10-11": "present",
        "2024-10-12": "leave",
        "2024-10-13": "holiday",
        "2024-10-14": "present",
        "2024-10-15": "present",
    }
    dashboard_data = get_sample_dashboard()

    return render(
        request,
        "demo/screenshots.html",
        {
            "attendance_data": attendance_data,
            "dashboard_data": dashboard_data,
        },
    )
