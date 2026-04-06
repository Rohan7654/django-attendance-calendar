"""
Attendance Calendar Template Tags

Provides template tags for rendering attendance calendars.
"""

from __future__ import annotations

import calendar
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Sequence, Set, Union

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


# ---------------------------------------------------------------------------
# Template Filters
# ---------------------------------------------------------------------------


@register.filter
def get_item(dictionary: Optional[Dict[str, Any]], key: str) -> Any:
    """Get item from dictionary by key in templates."""
    if dictionary and hasattr(dictionary, "get"):
        return dictionary.get(key, "")
    return ""


# ---------------------------------------------------------------------------
# Status / colour / size constants
# ---------------------------------------------------------------------------

AttendanceData = Dict[str, Union[str, Dict[str, Any]]]
"""Type alias: maps ``"YYYY-MM-DD"`` → status string **or** info dict."""

# Default status colors
DEFAULT_COLORS: Dict[str, str] = {
    "present": "#22c55e",
    "absent": "#ef4444",
    "late": "#f59e0b",
    "half_day": "#eab308",
    "holiday": "#3b82f6",
    "leave": "#8b5cf6",
    "weekend": "#6b7280",
}

# Color schemes
COLOR_SCHEMES: Dict[str, Dict[str, str]] = {
    "default": {
        "present": "#22c55e",
        "absent": "#ef4444",
        "late": "#f59e0b",
        "half_day": "#eab308",
        "holiday": "#3b82f6",
        "leave": "#8b5cf6",
    },
    "pastel": {
        "present": "#86efac",
        "absent": "#fca5a5",
        "late": "#fcd34d",
        "half_day": "#fef08a",
        "holiday": "#93c5fd",
        "leave": "#c4b5fd",
    },
    "vibrant": {
        "present": "#00ff88",
        "absent": "#ff3366",
        "late": "#ffaa00",
        "half_day": "#ffdd00",
        "holiday": "#0088ff",
        "leave": "#aa00ff",
    },
    "monochrome": {
        "present": "#4ade80",
        "absent": "#f87171",
        "late": "#a3a3a3",
        "half_day": "#d4d4d4",
        "holiday": "#525252",
        "leave": "#737373",
    },
    "corporate": {
        "present": "#059669",
        "absent": "#dc2626",
        "late": "#d97706",
        "half_day": "#ca8a04",
        "holiday": "#2563eb",
        "leave": "#7c3aed",
    },
}

# Layout sizes
SIZES: Dict[str, str] = {
    "mini": "180px",
    "compact": "280px",
    "medium": "400px",
    "large": "100%",
}

# Status labels for legend
STATUS_LABELS: Dict[str, str] = {
    "present": "Present",
    "absent": "Absent",
    "late": "Late",
    "half_day": "Half Day",
    "holiday": "Holiday",
    "leave": "Leave",
}

# Valid options for input validation
VALID_THEMES: Set[str] = {"light", "dark", "auto"}
VALID_COLOR_SCHEMES: Set[str] = set(COLOR_SCHEMES.keys())
VALID_SIZES: Set[str] = set(SIZES.keys())
VALID_LEGEND_POSITIONS: Set[str] = {"top", "bottom", "left", "right"}
VALID_FIRST_DAYS: Set[str] = {"sunday", "monday"}
VALID_EXPORT_FORMATS: Set[str] = {"png", "pdf", "csv"}


# ---------------------------------------------------------------------------
# Calendar data builder
# ---------------------------------------------------------------------------


def get_calendar_data(
    year: int,
    month: int,
    attendance_data: AttendanceData,
    first_day: str = "sunday",
) -> Dict[str, Any]:
    """
    Generate calendar data for a specific month.

    Args:
        year: Year to display
        month: Month to display (1-12)
        attendance_data: Dictionary of date strings to status
        first_day: ``"sunday"`` or ``"monday"``

    Returns:
        Dictionary with calendar structure and metadata
    """
    # Thread-safe: pass firstweekday to Calendar() instead of setfirstweekday()
    if first_day == "monday":
        first_weekday = calendar.MONDAY
        weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    else:
        first_weekday = calendar.SUNDAY
        weekdays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

    # Create calendar instance with the correct first weekday (thread-safe)
    cal = calendar.Calendar(firstweekday=first_weekday)
    month_days = cal.monthdayscalendar(year, month)

    # Get previous and next month info
    if month == 1:
        prev_month, prev_year = 12, year - 1
    else:
        prev_month, prev_year = month - 1, year

    if month == 12:
        next_month, next_year = 1, year + 1
    else:
        next_month, next_year = month + 1, year

    # Days in previous month
    prev_month_days = calendar.monthrange(prev_year, prev_month)[1]

    # Track next month day counter across all weeks
    next_month_day_counter = 1
    today = date.today()

    # Build weeks data
    weeks: List[List[Dict[str, Any]]] = []
    for week_index, week in enumerate(month_days):
        week_data: List[Dict[str, Any]] = []
        for i, day in enumerate(week):
            if day == 0:
                if week_index == 0:
                    # Leading zeros in first week = previous month days
                    first_week = month_days[0]
                    zeros_before = 0
                    for d in first_week:
                        if d == 0:
                            zeros_before += 1
                        else:
                            break
                    prev_day = prev_month_days - zeros_before + i + 1
                    week_data.append(
                        {
                            "day": prev_day,
                            "date": f"{prev_year}-{prev_month:02d}-{prev_day:02d}",
                            "current_month": False,
                            "is_today": False,
                            "status": None,
                            "avatar": None,
                            "note": None,
                        }
                    )
                else:
                    # Trailing zeros in later weeks = next month days
                    week_data.append(
                        {
                            "day": next_month_day_counter,
                            "date": f"{next_year}-{next_month:02d}-{next_month_day_counter:02d}",
                            "current_month": False,
                            "is_today": False,
                            "status": None,
                            "avatar": None,
                            "note": None,
                        }
                    )
                    next_month_day_counter += 1
            else:
                # Current month day
                date_str = f"{year}-{month:02d}-{day:02d}"
                is_today = (
                    year == today.year and month == today.month and day == today.day
                )

                # Get attendance info
                att_info = attendance_data.get(date_str, None)
                if isinstance(att_info, dict):
                    status = att_info.get("status")
                    avatar = att_info.get("avatar")
                    note = att_info.get("note")
                elif isinstance(att_info, str):
                    status = att_info
                    avatar = None
                    note = None
                else:
                    status = None
                    avatar = None
                    note = None

                week_data.append(
                    {
                        "day": day,
                        "date": date_str,
                        "current_month": True,
                        "is_today": is_today,
                        "status": status,
                        "avatar": avatar,
                        "note": note,
                    }
                )
        weeks.append(week_data)

    return {
        "year": year,
        "month": month,
        "month_name": calendar.month_name[month],
        "weekdays": weekdays,
        "weeks": weeks,
        "prev_month": prev_month,
        "prev_year": prev_year,
        "next_month": next_month,
        "next_year": next_year,
        "first_day": first_day,
    }


def get_status_colors(
    color_scheme: str, custom_statuses: Optional[Dict[str, Any]] = None
) -> Dict[str, str]:
    """Get colors for all statuses based on scheme and custom definitions."""
    colors = COLOR_SCHEMES.get(color_scheme, COLOR_SCHEMES["default"]).copy()
    if custom_statuses:
        for status, info in custom_statuses.items():
            if isinstance(info, dict) and "color" in info:
                colors[status] = info["color"]
    return colors


def get_status_labels(
    custom_statuses: Optional[Dict[str, Any]] = None,
) -> Dict[str, str]:
    """Get labels for all statuses including custom ones."""
    labels = STATUS_LABELS.copy()
    if custom_statuses:
        for status, info in custom_statuses.items():
            if isinstance(info, dict) and "label" in info:
                labels[status] = info["label"]
    return labels


# ---------------------------------------------------------------------------
# Template tags
# ---------------------------------------------------------------------------


@register.inclusion_tag("attendance_calendar/calendar.html", takes_context=True)
def attendance_calendar(
    context: Dict[str, Any],
    data: AttendanceData,
    theme: str = "light",
    color_scheme: str = "default",
    size: str = "medium",
    year: Optional[int] = None,
    month: Optional[int] = None,
    show_legend: bool = False,
    legend_position: str = "bottom",
    show_avatar: bool = False,
    avatar_opacity: float = 0.25,
    show_month_nav: bool = True,
    first_day: str = "sunday",
    highlight_today: bool = True,
    show_tooltips: bool = True,
    show_export: bool = False,
    export_formats: str = "png,pdf,csv",
    custom_statuses: Optional[Dict[str, Any]] = None,
    css_class: str = "",
) -> Dict[str, Any]:
    """
    Render an attendance calendar.

    Args:
        data: Dictionary of date strings to status or status info dicts
        theme: ``"light"``, ``"dark"``, or ``"auto"``
        color_scheme: ``"default"``, ``"pastel"``, ``"vibrant"``,
            ``"monochrome"``, ``"corporate"``
        size: ``"mini"``, ``"compact"``, ``"medium"``, ``"large"``
        year: Year to display (default: current year)
        month: Month to display (default: current month)
        show_legend: Whether to show the status legend
        legend_position: ``"top"``, ``"bottom"``, ``"left"``, ``"right"``
        show_avatar: Whether to show avatar overlays
        avatar_opacity: Opacity for avatar overlays (0.1–0.5)
        show_month_nav: Whether to show month navigation arrows
        first_day: ``"sunday"`` or ``"monday"``
        highlight_today: Whether to highlight today's date
        show_tooltips: Whether to show tooltips on hover
        show_export: Whether to show export buttons
        export_formats: Comma-separated export formats
        custom_statuses: Dictionary of custom status definitions
        css_class: Additional CSS classes
    """
    # Validate inputs, fall back to defaults for invalid values
    if theme not in VALID_THEMES:
        theme = "light"
    if color_scheme not in VALID_COLOR_SCHEMES:
        color_scheme = "default"
    if size not in VALID_SIZES:
        size = "medium"
    if legend_position not in VALID_LEGEND_POSITIONS:
        legend_position = "bottom"
    if first_day not in VALID_FIRST_DAYS:
        first_day = "sunday"
    avatar_opacity = max(0.1, min(0.5, float(avatar_opacity)))
    # Use current date if not specified
    today = date.today()
    display_year = year if year else today.year
    display_month = month if month else today.month

    # Get calendar data
    calendar_data = get_calendar_data(
        display_year, display_month, data or {}, first_day
    )

    # Get colors and labels
    colors = get_status_colors(color_scheme, custom_statuses)
    labels = get_status_labels(custom_statuses)

    # Build legend items
    legend_items: List[Dict[str, str]] = []
    if show_legend:
        for status, label in labels.items():
            if status in colors:
                legend_items.append(
                    {
                        "status": status,
                        "label": label,
                        "color": colors[status],
                    }
                )

    # Get size value
    width = SIZES.get(size, SIZES["medium"])

    # Export formats list
    export_list = [f.strip() for f in export_formats.split(",")] if show_export else []

    return {
        "calendar": calendar_data,
        "theme": theme,
        "color_scheme": color_scheme,
        "colors": colors,
        "size": size,
        "width": width,
        "show_legend": show_legend,
        "legend_position": legend_position,
        "legend_items": legend_items,
        "show_avatar": show_avatar,
        "avatar_opacity": avatar_opacity,
        "show_month_nav": show_month_nav,
        "highlight_today": highlight_today,
        "show_tooltips": show_tooltips,
        "show_export": show_export,
        "export_formats": export_list,
        "css_class": css_class,
        "request": context.get("request"),
    }


@register.inclusion_tag("attendance_calendar/dashboard.html", takes_context=True)
def attendance_dashboard(
    context: Dict[str, Any],
    data: Dict[str, Any],
    theme: str = "light",
    color_scheme: str = "default",
    columns: int = 3,
    show_summary: bool = True,
    year: Optional[int] = None,
    month: Optional[int] = None,
    first_day: str = "sunday",
    custom_statuses: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Render a multi-person attendance dashboard.

    Args:
        data: Dictionary with ``"employees"`` list
        theme: ``"light"``, ``"dark"``, or ``"auto"``
        color_scheme: Color scheme name
        columns: Number of calendars per row
        show_summary: Whether to show summary statistics
        year: Year to display
        month: Month to display
        first_day: ``"sunday"`` or ``"monday"``
        custom_statuses: Custom status definitions
    """
    # Validate inputs
    if theme not in VALID_THEMES:
        theme = "light"
    if color_scheme not in VALID_COLOR_SCHEMES:
        color_scheme = "default"
    if first_day not in VALID_FIRST_DAYS:
        first_day = "sunday"
    columns = max(1, min(6, int(columns)))
    today = date.today()
    display_year = year if year else today.year
    display_month = month if month else today.month

    employees: List[Dict[str, Any]] = (
        data.get("employees", []) if isinstance(data, dict) else []
    )

    # Build calendar for each employee
    employee_calendars: List[Dict[str, Any]] = []
    total_present = 0
    total_absent = 0
    total_days = 0

    for emp in employees:
        cal_data = get_calendar_data(
            display_year, display_month, emp.get("attendance", {}), first_day
        )

        # Count stats
        for week in cal_data["weeks"]:
            for day in week:
                if day["current_month"] and day["status"]:
                    total_days += 1
                    if day["status"] == "present":
                        total_present += 1
                    elif day["status"] == "absent":
                        total_absent += 1

        employee_calendars.append(
            {
                "id": emp.get("id"),
                "name": emp.get("name"),
                "avatar": emp.get("avatar"),
                "department": emp.get("department"),
                "calendar": cal_data,
            }
        )

    # Calculate summary
    summary: Dict[str, Any] = (
        data.get("summary", {}) if isinstance(data, dict) else {}
    )
    if not summary and total_days > 0:
        summary = {
            "total_present": total_present,
            "total_absent": total_absent,
            "attendance_rate": (
                round((total_present / total_days) * 100, 1) if total_days else 0
            ),
        }

    colors = get_status_colors(color_scheme, custom_statuses)

    return {
        "employees": employee_calendars,
        "summary": summary,
        "theme": theme,
        "color_scheme": color_scheme,
        "colors": colors,
        "columns": columns,
        "show_summary": show_summary,
        "year": display_year,
        "month": display_month,
        "month_name": calendar.month_name[display_month],
        "request": context.get("request"),
    }
