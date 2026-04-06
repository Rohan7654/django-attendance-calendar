# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-04-07

### Added

- **AJAX month navigation**: Calendars can now fetch attendance data for other months dynamically via two mechanisms:
  - `data-ajax-url` attribute on the calendar element for automatic URL-based fetching
  - `AttendanceCalendar.onFetch(calendar, callback)` JS API for custom fetch logic
  - `AttendanceCalendar.preload(calendar, year, month, data)` to pre-cache month data
- **Type hints**: Full PEP 484 type annotations on all public functions and constants
- **`py.typed` marker**: PEP 561 compliance — downstream typed projects can now use our annotations
- **Functional admin mixin**: `AttendanceCalendarMixin` now renders a real inline calendar table with colored dots in the Django admin detail view; subclasses just override `get_attendance_data(obj)` to return a `{date: status}` dict
- `attendance_summary()` admin column now shows real Present / Absent / Total counts from `get_attendance_data()`

### Changed

- Bumped version to 1.1.0
- `pyproject.toml`: `py.typed` is now included in package distribution
- Black target-version updated to include `py313`

## [1.0.0] - 2026-02-21

### Fixed

- **Thread-safety**: `get_calendar_data` now uses `Calendar(firstweekday=...)` instead of the global `setfirstweekday()`, preventing race conditions in multi-threaded servers
- **Calendar day calculation**: Fixed incorrect "other month" day numbering for previous/next month days displayed in the calendar grid
- **JS navigation**: `regenerateCalendar` now respects the `first_day` setting (Monday/Sunday) via the `data-first-day` attribute
- **Dark theme export**: PNG and PDF exports now automatically detect dark theme and use the correct background color instead of hardcoded white
- **Input validation**: Template tags now validate `theme`, `color_scheme`, `size`, `legend_position`, `first_day`, and `avatar_opacity`, falling back to defaults for invalid values

### Changed

- Removed deprecated `default_app_config` from `__init__.py` (unnecessary in Django ≥ 4.0)
- Extracted 150 lines of inline CSS from `dashboard.html` into separate `dashboard.css` static file
- Dashboard mini-calendar dots now use the active color scheme instead of hardcoded status colors
- Removed non-functional `sortable` and `show_filters` parameters from `attendance_dashboard` template tag
- Updated `pyproject.toml` classifiers to include Django 5.1 and Python 3.13
- Promoted development status from Beta to Production/Stable

### Added

- `MANIFEST.in` for reliable source distribution packaging
- `CHANGELOG.md` for tracking releases
- `data-first-day` attribute on the calendar root element for JS access
- `first_day` key in the calendar context data for template access

## [1.0.0] - Initial Release

### Added

- Attendance calendar template tag with themes, color schemes, and size variants
- Multi-person dashboard template tag
- Export functionality (PNG, PDF, CSV)
- Keyboard navigation and ARIA labels for accessibility
- Django admin integration mixins
- Five color schemes: default, pastel, vibrant, monochrome, corporate
- Three themes: light, dark (glassmorphism), auto (follows system)
- Legend positioning (top, bottom, left, right)
- Custom status support
- Example project with demos
