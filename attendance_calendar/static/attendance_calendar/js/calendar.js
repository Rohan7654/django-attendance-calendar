/**
 * Attendance Calendar JavaScript
 * Handles navigation, keyboard accessibility, export, and optional AJAX data fetching.
 */

(function() {
    'use strict';

    // Prevent multiple initializations
    if (window.AttendanceCalendarInitialized) {
        return;
    }
    window.AttendanceCalendarInitialized = true;

    // Store original calendar data for each calendar
    const calendarDataStore = new Map();

    // Optional: user-registered AJAX fetch callbacks per calendar
    // Key: calendarId string, Value: function(year, month) => Promise<object>
    const fetchCallbacks = new Map();

    // Initialize all calendars on the page
    function initCalendars() {
        document.querySelectorAll('.attendance-calendar').forEach(function(calendar, index) {
            // Skip already initialized calendars
            if (calendar.dataset.initialized === 'true') return;
            calendar.dataset.initialized = 'true';
            calendar.dataset.calendarId = 'calendar-' + index;
            
            // Store original calendar HTML for restoration
            storeCalendarData(calendar);
            
            initNavigation(calendar);
            initKeyboardNav(calendar);
            initExport(calendar);
        });
    }

    // Store calendar attendance data
    function storeCalendarData(calendar) {
        const calendarId = calendar.dataset.calendarId;
        const year = parseInt(calendar.dataset.year, 10);
        const month = parseInt(calendar.dataset.month, 10);
        
        const attendanceData = {};
        calendar.querySelectorAll('.cal-day.current-month').forEach(function(day) {
            const date = day.dataset.date;
            const status = day.dataset.status;
            const note = day.dataset.note;
            if (date && status) {
                attendanceData[date] = { status: status, note: note || '' };
            }
        });
        
        if (!calendarDataStore.has(calendarId)) {
            calendarDataStore.set(calendarId, {});
        }
        
        const key = year + '-' + month;
        calendarDataStore.get(calendarId)[key] = attendanceData;
        calendarDataStore.get(calendarId).originalYear = year;
        calendarDataStore.get(calendarId).originalMonth = month;
    }

    // Month navigation
    function initNavigation(calendar) {
        const prevBtn = calendar.querySelector('.cal-nav-prev');
        const nextBtn = calendar.querySelector('.cal-nav-next');

        if (prevBtn) {
            prevBtn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                navigateMonth(calendar, -1);
            });
        }

        if (nextBtn) {
            nextBtn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                navigateMonth(calendar, 1);
            });
        }
    }

    // Navigate to previous/next month
    function navigateMonth(calendar, direction) {
        let year = parseInt(calendar.dataset.year, 10);
        let month = parseInt(calendar.dataset.month, 10);

        month += direction;
        if (month < 1) {
            month = 12;
            year -= 1;
        } else if (month > 12) {
            month = 1;
            year += 1;
        }

        // Update the calendar data attributes
        calendar.dataset.year = year;
        calendar.dataset.month = month;

        // Update the title
        const monthNames = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                           'July', 'August', 'September', 'October', 'November', 'December'];
        const title = calendar.querySelector('.cal-title');
        if (title) {
            title.textContent = monthNames[month] + ' ' + year;
        }

        // Dispatch custom event for external listeners
        calendar.dispatchEvent(new CustomEvent('monthChange', {
            detail: { year: year, month: month },
            bubbles: true
        }));

        // Check if we have stored data for this month
        const calendarId = calendar.dataset.calendarId;
        const key = year + '-' + month;
        const store = calendarDataStore.get(calendarId) || {};
        const hasStoredData = Boolean(store[key]);

        // If no stored data, try fetching via AJAX (if a URL or callback is registered)
        if (!hasStoredData) {
            const fetched = fetchMonthData(calendar, year, month);
            if (fetched) {
                // fetchMonthData will call regenerateCalendar after it resolves
                return;
            }
        }

        // Regenerate calendar with stored (or empty) data
        regenerateCalendar(calendar, year, month);
    }

    /**
     * Try to fetch attendance data for a given month.
     *
     * Checks (in order):
     *   1. A registered JS callback via AttendanceCalendar.onFetch()
     *   2. A data-ajax-url attribute on the calendar element
     *
     * Returns true if an async fetch was initiated, false otherwise.
     */
    function fetchMonthData(calendar, year, month) {
        const calendarId = calendar.dataset.calendarId;

        // Option 1: JS callback
        if (fetchCallbacks.has(calendarId)) {
            const cb = fetchCallbacks.get(calendarId);
            const result = cb(year, month);
            if (result && typeof result.then === 'function') {
                // It's a Promise
                result.then(function(data) {
                    cacheAndRender(calendar, year, month, data);
                }).catch(function() {
                    // On error, render with empty data
                    regenerateCalendar(calendar, year, month);
                });
                return true;
            } else if (result && typeof result === 'object') {
                // Synchronous result
                cacheAndRender(calendar, year, month, result);
                return true;
            }
        }

        // Option 2: data-ajax-url attribute
        var ajaxUrl = calendar.dataset.ajaxUrl;
        if (ajaxUrl) {
            // Append year/month as query params
            var separator = ajaxUrl.indexOf('?') === -1 ? '?' : '&';
            var url = ajaxUrl + separator + 'year=' + year + '&month=' + month;

            fetch(url, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(function(response) {
                if (!response.ok) throw new Error('Network error');
                return response.json();
            })
            .then(function(data) {
                cacheAndRender(calendar, year, month, data);
            })
            .catch(function() {
                regenerateCalendar(calendar, year, month);
            });
            return true;
        }

        return false;
    }

    /**
     * Cache fetched data and re-render the calendar grid.
     * Expects `data` to be a plain object: { "YYYY-MM-DD": "status", ... }
     */
    function cacheAndRender(calendar, year, month, data) {
        var calendarId = calendar.dataset.calendarId;
        if (!calendarDataStore.has(calendarId)) {
            calendarDataStore.set(calendarId, {});
        }
        // Normalise values: accept either plain strings or {status, note} objects
        var normalised = {};
        for (var dateStr in data) {
            if (!data.hasOwnProperty(dateStr)) continue;
            var val = data[dateStr];
            if (typeof val === 'string') {
                normalised[dateStr] = { status: val, note: '' };
            } else if (val && typeof val === 'object') {
                normalised[dateStr] = { status: val.status || '', note: val.note || '' };
            }
        }
        var key = year + '-' + month;
        calendarDataStore.get(calendarId)[key] = normalised;
        regenerateCalendar(calendar, year, month);
    }

    // Get stored attendance data for a month
    function getStoredData(calendar, year, month) {
        const calendarId = calendar.dataset.calendarId;
        const store = calendarDataStore.get(calendarId);
        if (!store) return {};
        
        const key = year + '-' + month;
        return store[key] || {};
    }

    // Calendar regeneration with data preservation
    function regenerateCalendar(calendar, year, month) {
        const grid = calendar.querySelector('.cal-grid');
        if (!grid) return;

        // Get stored attendance data
        const attendanceData = getStoredData(calendar, year, month);

        // Respect the first_day setting from the data attribute
        const firstDaySetting = calendar.dataset.firstDay || 'sunday';

        // Get first day of month and total days
        const firstDay = new Date(year, month - 1, 1);
        const lastDay = new Date(year, month, 0);
        const daysInMonth = lastDay.getDate();
        let startDayOfWeek = firstDay.getDay(); // 0 = Sunday

        // Adjust for Monday-first calendars
        if (firstDaySetting === 'monday') {
            startDayOfWeek = (startDayOfWeek + 6) % 7; // Monday=0, Sunday=6
        }

        // Get previous month info for leading days
        const prevMonth = month === 1 ? 12 : month - 1;
        const prevYear = month === 1 ? year - 1 : year;
        const prevMonthDays = new Date(prevYear, prevMonth, 0).getDate();

        // Clear grid
        grid.innerHTML = '';

        // Always render exactly 42 cells (6 rows) for consistent height
        const today = new Date();
        let dayCounter = 1;
        let nextMonthDay = 1;

        for (let i = 0; i < 42; i++) {
            const dayEl = document.createElement('div');
            
            if (i < startDayOfWeek) {
                // Previous month days (greyed)
                const prevDay = prevMonthDays - startDayOfWeek + i + 1;
                dayEl.className = 'cal-day other-month';
                dayEl.innerHTML = '<span class="cal-day-number">' + prevDay + '</span>';
            } else if (dayCounter <= daysInMonth) {
                // Current month days
                const dateStr = year + '-' + String(month).padStart(2, '0') + '-' + String(dayCounter).padStart(2, '0');
                const isToday = (year === today.getFullYear() && month === today.getMonth() + 1 && dayCounter === today.getDate());
                
                dayEl.className = 'cal-day current-month' + (isToday ? ' today' : '');
                dayEl.dataset.date = dateStr;
                
                // Check for attendance data
                const dayData = attendanceData[dateStr];
                if (dayData && dayData.status) {
                    dayEl.dataset.status = dayData.status;
                    if (dayData.note) dayEl.dataset.note = dayData.note;
                    dayEl.innerHTML = '<span class="cal-day-number">' + dayCounter + '</span>' +
                                      '<span class="cal-status-dot status-' + dayData.status + '"></span>';
                } else {
                    dayEl.innerHTML = '<span class="cal-day-number">' + dayCounter + '</span>';
                }
                
                dayEl.setAttribute('tabindex', '0');
                dayCounter++;
            } else {
                // Next month days (greyed)
                dayEl.className = 'cal-day other-month';
                dayEl.innerHTML = '<span class="cal-day-number">' + nextMonthDay + '</span>';
                nextMonthDay++;
            }
            
            grid.appendChild(dayEl);
        }
    }

    // Keyboard navigation for accessibility
    function initKeyboardNav(calendar) {
        const grid = calendar.querySelector('.cal-grid');
        if (!grid) return;

        grid.addEventListener('keydown', function(e) {
            const currentDay = document.activeElement;
            if (!currentDay.classList.contains('cal-day')) return;

            const days = Array.from(grid.querySelectorAll('.cal-day.current-month'));
            const currentIndex = days.indexOf(currentDay);

            let newIndex = currentIndex;
            switch(e.key) {
                case 'ArrowLeft':
                    newIndex = Math.max(0, currentIndex - 1);
                    break;
                case 'ArrowRight':
                    newIndex = Math.min(days.length - 1, currentIndex + 1);
                    break;
                case 'ArrowUp':
                    newIndex = Math.max(0, currentIndex - 7);
                    break;
                case 'ArrowDown':
                    newIndex = Math.min(days.length - 1, currentIndex + 7);
                    break;
                case 'Enter':
                case ' ':
                    currentDay.click();
                    return;
                default:
                    return;
            }

            e.preventDefault();
            days[newIndex].focus();
        });

        // Make days focusable
        grid.querySelectorAll('.cal-day.current-month').forEach(function(day) {
            day.setAttribute('tabindex', '0');
        });
    }

    // Export functionality - only exports the clicked calendar
    function initExport(calendar) {
        calendar.querySelectorAll('.cal-export-btn').forEach(function(btn) {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                e.stopImmediatePropagation();
                
                const format = this.dataset.format;
                exportCalendar(calendar, format);
            });
        });
    }

    // Detect if a calendar uses dark theme
    function isDarkTheme(calendar) {
        return calendar.classList.contains('theme-dark') ||
               (calendar.classList.contains('theme-auto') &&
                window.matchMedia('(prefers-color-scheme: dark)').matches);
    }

    // Get appropriate export background color based on theme
    function getExportBackground(calendar) {
        return isDarkTheme(calendar) ? '#1e1e2e' : '#ffffff';
    }

    // Export the specific calendar
    function exportCalendar(calendar, format) {
        const year = calendar.dataset.year;
        const month = calendar.dataset.month;
        const fileName = 'attendance-' + year + '-' + month;

        switch (format.toLowerCase()) {
            case 'csv':
                exportCSV(calendar, fileName);
                break;
            case 'png':
                exportPNG(calendar, fileName);
                break;
            case 'pdf':
                exportPDF(calendar, fileName);
                break;
        }
    }

    // Export to CSV
    function exportCSV(calendar, fileName) {
        const days = calendar.querySelectorAll('.cal-day.current-month');
        let csv = 'Date,Status,Note\n';

        days.forEach(function(day) {
            const date = day.dataset.date || '';
            const status = day.dataset.status || '';
            const note = day.dataset.note || '';
            csv += '"' + date + '","' + status + '","' + note + '"\n';
        });

        downloadFile(csv, fileName + '.csv', 'text/csv');
    }

    // Export to PNG (requires html2canvas)
    function exportPNG(calendar, fileName) {
        if (typeof html2canvas === 'undefined') {
            alert('PNG export requires html2canvas library.');
            return;
        }

        // Hide elements that shouldn't be in export
        const exportBtns = calendar.querySelector('.cal-export');
        const navBtns = calendar.querySelector('.cal-nav');
        if (exportBtns) exportBtns.style.display = 'none';
        if (navBtns) navBtns.style.display = 'none';

        html2canvas(calendar, {
            scale: 2,
            useCORS: true,
            backgroundColor: getExportBackground(calendar)
        }).then(function(canvas) {
            // Restore hidden elements
            if (exportBtns) exportBtns.style.display = '';
            if (navBtns) navBtns.style.display = '';
            
            const link = document.createElement('a');
            link.download = fileName + '.png';
            link.href = canvas.toDataURL('image/png');
            link.click();
        }).catch(function() {
            // Restore on error
            if (exportBtns) exportBtns.style.display = '';
            if (navBtns) navBtns.style.display = '';
        });
    }

    // Export to PDF (requires jsPDF)
    function exportPDF(calendar, fileName) {
        if (typeof html2canvas === 'undefined') {
            alert('PDF export requires html2canvas library.');
            return;
        }

        const PDF = window.jspdf ? window.jspdf.jsPDF : (window.jsPDF || null);
        if (!PDF) {
            alert('PDF export requires jsPDF library.');
            return;
        }

        // Hide elements that shouldn't be in export
        const exportBtns = calendar.querySelector('.cal-export');
        const navBtns = calendar.querySelector('.cal-nav');
        if (exportBtns) exportBtns.style.display = 'none';
        if (navBtns) navBtns.style.display = 'none';

        html2canvas(calendar, {
            scale: 2,
            useCORS: true,
            backgroundColor: getExportBackground(calendar)
        }).then(function(canvas) {
            // Restore hidden elements
            if (exportBtns) exportBtns.style.display = '';
            if (navBtns) navBtns.style.display = '';
            
            const imgData = canvas.toDataURL('image/png');
            
            // Calculate dimensions to fit on page
            const imgWidth = canvas.width;
            const imgHeight = canvas.height;
            
            // Use landscape for wider calendars
            const orientation = imgWidth > imgHeight ? 'landscape' : 'portrait';
            const pdf = new PDF(orientation, 'pt', 'a4');
            
            const pageWidth = pdf.internal.pageSize.getWidth();
            const pageHeight = pdf.internal.pageSize.getHeight();
            
            // Calculate scale to fit
            const margin = 40;
            const maxWidth = pageWidth - (margin * 2);
            const maxHeight = pageHeight - (margin * 2);
            
            let finalWidth = imgWidth / 2; // Divide by scale factor
            let finalHeight = imgHeight / 2;
            
            // Scale down if too large
            if (finalWidth > maxWidth) {
                const ratio = maxWidth / finalWidth;
                finalWidth = maxWidth;
                finalHeight = finalHeight * ratio;
            }
            if (finalHeight > maxHeight) {
                const ratio = maxHeight / finalHeight;
                finalHeight = maxHeight;
                finalWidth = finalWidth * ratio;
            }
            
            // Center on page
            const x = (pageWidth - finalWidth) / 2;
            const y = margin;
            
            pdf.addImage(imgData, 'PNG', x, y, finalWidth, finalHeight);
            pdf.save(fileName + '.pdf');
        }).catch(function() {
            // Restore on error
            if (exportBtns) exportBtns.style.display = '';
            if (navBtns) navBtns.style.display = '';
        });
    }

    // Helper to download file
    function downloadFile(content, fileName, mimeType) {
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = fileName;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initCalendars);
    } else {
        initCalendars();
    }

    // ---------------------------------------------------------------
    // Public API
    // ---------------------------------------------------------------
    window.AttendanceCalendar = {
        /**
         * Re-run initialisation (useful after dynamic DOM insertion).
         */
        init: initCalendars,

        /**
         * Programmatically navigate a calendar element.
         * @param {HTMLElement} calendar  The .attendance-calendar element.
         * @param {number}      direction  -1 (prev) or +1 (next).
         */
        navigateMonth: navigateMonth,

        /**
         * Programmatically trigger an export.
         * @param {HTMLElement} calendar  The .attendance-calendar element.
         * @param {string}      format    "csv", "png", or "pdf".
         */
        exportCalendar: exportCalendar,

        /**
         * Register an AJAX fetch callback for a calendar.
         *
         * The callback receives (year, month) and should return either:
         *   - a Promise that resolves to { "YYYY-MM-DD": "status", … }
         *   - a plain object with the same shape (synchronous)
         *
         * Example:
         *   const cal = document.querySelector('.attendance-calendar');
         *   AttendanceCalendar.onFetch(cal, function(year, month) {
         *       return fetch('/api/attendance/?year=' + year + '&month=' + month)
         *              .then(r => r.json());
         *   });
         *
         * Alternatively, set data-ajax-url="..." on the element and the
         * calendar will auto-fetch from that URL with ?year=…&month=…
         * query parameters appended.
         *
         * @param {HTMLElement} calendar  The .attendance-calendar element.
         * @param {Function}    callback  (year, month) → Promise|Object
         */
        onFetch: function(calendar, callback) {
            if (!calendar.dataset.calendarId) {
                console.warn('AttendanceCalendar.onFetch: calendar not initialised yet.');
                return;
            }
            fetchCallbacks.set(calendar.dataset.calendarId, callback);
        },

        /**
         * Pre-load attendance data for a specific month so that
         * navigating to it won't show an empty grid.
         *
         * @param {HTMLElement} calendar  The .attendance-calendar element.
         * @param {number}      year
         * @param {number}      month
         * @param {Object}      data  { "YYYY-MM-DD": "status", … }
         */
        preload: function(calendar, year, month, data) {
            cacheAndRender(calendar, year, month, data);
        }
    };
})();
