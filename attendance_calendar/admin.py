"""
Django Attendance Calendar - Admin Integration

Provides admin mixins and widgets for attendance management.
"""

from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional, Sequence

from django.contrib import admin
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.utils.html import format_html


class AttendanceCalendarMixin:
    """
    Mixin to add attendance calendar functionality to ModelAdmin.

    Subclasses *must* implement ``get_attendance_data(obj)`` to return
    a dict mapping date-strings (``"YYYY-MM-DD"``) to status strings
    (e.g. ``"present"``, ``"absent"``, ``"late"``).

    Usage::

        @admin.register(Employee)
        class EmployeeAdmin(AttendanceCalendarMixin, admin.ModelAdmin):
            attendance_calendar_inline = True

            def get_attendance_data(self, obj):
                return {
                    record.date.isoformat(): record.status
                    for record in obj.attendance_set.filter(
                        date__month=date.today().month,
                        date__year=date.today().year,
                    )
                }
    """

    attendance_calendar_inline: bool = False
    attendance_field: str = "attendance"
    attendance_theme: str = "light"
    attendance_color_scheme: str = "default"

    # ------------------------------------------------------------------
    # Override this in your subclass
    # ------------------------------------------------------------------
    def get_attendance_data(self, obj: Any) -> Dict[str, str]:
        """
        Return attendance data for *obj*.

        Must return a dict mapping ``"YYYY-MM-DD"`` strings to status
        strings such as ``"present"``, ``"absent"``, ``"late"``, etc.

        Override this method in your ModelAdmin subclass.
        """
        return {}

    # ------------------------------------------------------------------
    # List-view column
    # ------------------------------------------------------------------
    def attendance_summary(self, obj: Any) -> str:
        """Display a mini attendance summary in list view."""
        data = self.get_attendance_data(obj)
        if not data:
            return format_html('<span style="color:#94a3b8;">No data</span>')

        present = sum(1 for s in data.values() if s == "present")
        absent = sum(1 for s in data.values() if s == "absent")
        total = len(data)

        return format_html(
            '<span style="color:#22c55e;" title="Present">{}</span> / '
            '<span style="color:#ef4444;" title="Absent">{}</span> / '
            '<span style="color:#64748b;" title="Total">{}</span>',
            present,
            absent,
            total,
        )

    attendance_summary.short_description = "Attendance"  # type: ignore[attr-defined]

    # ------------------------------------------------------------------
    # Detail-view readonly field
    # ------------------------------------------------------------------
    def get_readonly_fields(
        self, request: HttpRequest, obj: Any = None
    ) -> Sequence[str]:
        """Add attendance calendar to readonly fields if inline is enabled."""
        readonly = list(super().get_readonly_fields(request, obj))  # type: ignore[misc]
        if self.attendance_calendar_inline:
            readonly.append("attendance_calendar_display")
        return readonly

    def attendance_calendar_display(self, obj: Any) -> str:
        """Render the attendance calendar in the admin detail view."""
        if not obj or not obj.pk:
            return "Save the object first to view the attendance calendar."

        data = self.get_attendance_data(obj)
        today = date.today()

        # Import here to avoid circular imports
        from attendance_calendar.templatetags.attendance_tags import (
            get_calendar_data,
            get_status_colors,
        )

        calendar_data = get_calendar_data(today.year, today.month, data)
        colors = get_status_colors(self.attendance_color_scheme)

        # Build inline HTML (the admin doesn't load our static CSS,
        # so we render a minimal self-contained calendar).
        rows_html: list[str] = []
        for week in calendar_data["weeks"]:
            cells: list[str] = []
            for day in week:
                if not day["current_month"]:
                    cells.append(
                        f'<td style="color:#cbd5e1;text-align:center;padding:4px;">'
                        f'{day["day"]}</td>'
                    )
                elif day["status"] and day["status"] in colors:
                    color = colors[day["status"]]
                    cells.append(
                        f'<td style="text-align:center;padding:4px;">'
                        f'{day["day"]}'
                        f'<span style="display:block;width:6px;height:6px;'
                        f"border-radius:50%;background:{color};"
                        f'margin:2px auto 0;"></span></td>'
                    )
                else:
                    cells.append(
                        f'<td style="text-align:center;padding:4px;">'
                        f'{day["day"]}</td>'
                    )
            rows_html.append("<tr>" + "".join(cells) + "</tr>")

        weekday_headers = "".join(
            f'<th style="text-align:center;padding:4px;color:#64748b;'
            f'font-weight:500;font-size:12px;">{d}</th>'
            for d in calendar_data["weekdays"]
        )

        legend_items = "".join(
            f'<span style="display:inline-flex;align-items:center;gap:4px;'
            f'margin-right:12px;font-size:12px;color:#64748b;">'
            f'<span style="width:8px;height:8px;border-radius:50%;'
            f'background:{color};display:inline-block;"></span>'
            f"{status.replace('_', ' ').title()}</span>"
            for status, color in colors.items()
        )

        html = (
            f'<div style="font-family:Inter,-apple-system,sans-serif;">'
            f'<h3 style="margin:0 0 8px;">'
            f'{calendar_data["month_name"]} {calendar_data["year"]}</h3>'
            f'<table style="border-collapse:collapse;">'
            f"<thead><tr>{weekday_headers}</tr></thead>"
            f'<tbody>{"".join(rows_html)}</tbody>'
            f"</table>"
            f'<div style="margin-top:8px;">{legend_items}</div>'
            f"</div>"
        )

        return format_html(html)

    attendance_calendar_display.short_description = "Attendance Calendar"  # type: ignore[attr-defined]


class AttendanceInline(admin.TabularInline):
    """
    Inline admin for attendance records.

    Usage::

        class EmployeeAdmin(admin.ModelAdmin):
            inlines = [AttendanceInline]

    You **must** set ``model`` in your subclass.
    """

    extra = 0
    fields: Sequence[str] = ["date", "status", "note"]
    readonly_fields: Sequence[str] = []

    def get_queryset(self, request: HttpRequest):  # type: ignore[override]
        """Limit to recent attendance records."""
        qs = super().get_queryset(request)
        return qs.order_by("-date")[:30]
