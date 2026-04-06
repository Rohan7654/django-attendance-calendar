from django.apps import AppConfig


class AttendanceCalendarConfig(AppConfig):
    """Django app configuration for Attendance Calendar."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "attendance_calendar"
    verbose_name = "Attendance Calendar"
