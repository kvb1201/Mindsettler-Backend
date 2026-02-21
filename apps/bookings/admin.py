from django.urls import path
from django.http import HttpResponse, JsonResponse
from django.contrib import admin, messages
from django.forms import SplitDateTimeWidget
from django.db import models
from django.db.models import Q

# ─────────────────────────
# ADMIN PANEL BRANDING
# ─────────────────────────
admin.site.site_header = "MindSettler Admin"
admin.site.site_title = "MindSettler Admin"
admin.site.index_title = "MindSettler Dashboard"

from .models import Booking
from apps.bookings.services import approve_booking, reject_booking
from apps.bookings.email import (
    send_booking_approved_email,
    send_booking_rejected_email,
)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "calendar/",
                self.admin_site.admin_view(self.calendar_view),
                name="booking-calendar",
            ),
            path(
                "calendar/data/",
                self.admin_site.admin_view(self.calendar_data_view),
                name="booking-calendar-data",
            ),
            path(
                "calendar/list/",
                self.admin_site.admin_view(self.calendar_list_view),
                name="booking-calendar-list",
            ),
        ]
        return custom_urls + urls

    def calendar_view(self, request):
        return HttpResponse("""
<!DOCTYPE html>
<html>
<head>
    <title>Booking Calendar</title>
    <meta charset="utf-8" />
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/fullcalendar@6.1.11/index.global.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/fullcalendar@6.1.11/index.global.min.js"></script>
    <style>
        body {
            margin: 0;
            padding: 24px;
            font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont;
            background: linear-gradient(135deg, #f8fafc 0%, #eef2ff 100%);
            color: #0f172a;
        }

        #calendar {
            max-width: 1300px;
            margin: 0 auto;
            background: #fff;
            border-radius: 18px;
            border: 1px solid #e5e7eb;
            box-shadow: 0 12px 32px rgba(30,41,59,0.09), 0 2px 8px rgba(30,41,59,0.04);
            padding: 20px;
        }

        .fc {
            font-size: 14px;
        }

        .fc .fc-toolbar-title {
            font-weight: 700;
            font-size: 1.3rem;
            color: #1e293b;
        }

        .fc-theme-standard td,
        .fc-theme-standard th {
            border-color: #e5e7eb;
        }

        .fc-timegrid-slot {
            border-bottom: 1px solid #e5e7eb;
        }

        .fc-timegrid-slot-label,
        .fc-col-header-cell-cushion {
            color: #334155;
            font-weight: 500;
        }

        .fc .fc-button {
            background: #fff;
            border: 1.5px solid #2563eb;
            border-radius: 10px;
            color: #2563eb;
            font-weight: 600;
            padding: 6px 14px;
            transition: background 0.15s, color 0.15s, border-color 0.15s;
            box-shadow: none;
        }
        .fc .fc-button:hover {
            background: #2563eb;
            color: #fff;
            border-color: #2563eb;
        }

        .fc-event {
            border-radius: 14px !important;
            padding: 6px 8px !important;
            font-weight: 600;
            font-size: 0.85rem;
            box-shadow: 0 4px 12px rgba(30,41,59,0.10);
        }

        .fc-event-title {
            white-space: normal;
        }
    </style>
</head>
<body>
    <div id="calendar"></div>

    <script>
        document.addEventListener('DOMContentLoaded', function () {
            const calendarEl = document.getElementById('calendar');

            const calendar = new FullCalendar.Calendar(calendarEl, {
                initialView: 'timeGridWeek',
                buttonText: {
                    today: 'Today',
                    month: 'Month',
                    week: 'Week',
                    day: 'Day'
                },
                slotMinTime: '08:00:00',
                slotMaxTime: '22:00:00',
                allDaySlot: false,
                nowIndicator: true,
                headerToolbar: {
                    left: 'prev,next today',
                    center: 'title',
                    right: 'timeGridDay,timeGridWeek,dayGridMonth'
                },
                events: '/admin/bookings/booking/calendar/data/',
                eventDidMount: function(info) {
                    const status = info.event.extendedProps.status;
                    // Soften the gradients for light theme readability
                    if (status === 'CONFIRMED') {
                        info.el.style.background = 'linear-gradient(135deg, #22c55e 70%, #bbf7d0 100%)';
                        info.el.style.color = '#14532d';
                    } else if (status === 'APPROVED') {
                        info.el.style.background = 'linear-gradient(135deg, #3b82f6 70%, #dbeafe 100%)';
                        info.el.style.color = '#1e3a8a';
                    }
                },
                eventClick: function(info) {
                    const bookingId = info.event.id;
                    window.open(`/admin/bookings/booking/${bookingId}/change/`, '_blank');
                }
            });

            calendar.render();
        });
    </script>
</body>
</html>
        """)

    def calendar_list_view(self, request):
        bookings = self.get_calendar_queryset()
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>Booking List View</title>
    <meta charset="utf-8" />
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont;
            background: linear-gradient(135deg, #f8fafc 0%, #eef2ff 100%);
            margin: 0;
            padding: 28px;
            color: #0f172a;
        }

        h1 {
            max-width: 1200px;
            margin: 0 auto 24px auto;
            font-weight: 700;
            font-size: 1.9rem;
            color: #111827;
        }

        table {
            border-collapse: collapse;
            width: 100%;
            max-width: 1200px;
            margin: 0 auto;
            background: #ffffff;
            border-radius: 18px;
            box-shadow: 0 12px 32px rgba(30,41,59,0.10);
            overflow: hidden;
        }

        thead {
            background: #2563eb;
            color: #ffffff;
        }

        th {
            text-align: left;
            padding: 14px 18px;
            font-size: 13px;
            letter-spacing: 0.03em;
            text-transform: uppercase;
            font-weight: 600;
        }

        td {
            padding: 14px 18px;
            border-bottom: 1px solid #e5e7eb;
            font-size: 14px;
            font-weight: 500;
            color: #1e293b;
        }

        tbody tr {
            transition: background 0.15s ease;
        }

        tbody tr:nth-child(even) {
            background-color: #f9fafb;
        }

        tbody tr:hover {
            background-color: #eef2ff;
            cursor: pointer;
        }

        .status-badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 600;
        }

        .status-APPROVED {
            background: #dbeafe;
            color: #1e40af;
        }

        .status-CONFIRMED {
            background: #dcfce7;
            color: #166534;
        }

        a {
            color: inherit;
            text-decoration: none;
            display: block;
            width: 100%;
            height: 100%;
        }

        @media (max-width: 768px) {
            table, thead, tbody, th, td, tr {
                display: block;
            }

            thead {
                display: none;
            }

            tbody tr {
                margin-bottom: 18px;
                border-radius: 16px;
                box-shadow: 0 6px 18px rgba(30,41,59,0.10);
                background: #ffffff;
                padding: 16px;
            }

            tbody td {
                border: none;
                padding: 10px 0;
                font-size: 13px;
                position: relative;
                padding-left: 48%;
            }

            tbody td::before {
                position: absolute;
                top: 10px;
                left: 16px;
                width: 45%;
                white-space: nowrap;
                font-weight: 600;
                content: attr(data-label);
                color: #64748b;
                font-size: 12px;
            }
        }
    </style>
</head>
<body>
    <h1>Booking List View</h1>
    <table>
        <thead>
            <tr>
                <th>Acknowledgement ID</th>
                <th>Name</th>
                <th>Psychologist</th>
                <th>Start</th>
                <th>End</th>
                <th>Status</th>
                <th>Mode</th>
            </tr>
        </thead>
        <tbody>
"""
        for b in bookings:
            psychologist = str(b.psychologist) if b.psychologist else "-"
            start = b.approved_slot_start.strftime("%Y-%m-%d %H:%M") if b.approved_slot_start else "-"
            end = b.approved_slot_end.strftime("%Y-%m-%d %H:%M") if b.approved_slot_end else "-"
            url = f"/admin/bookings/booking/{b.id}/change/"
            html += f"""
            <tr onclick="window.open('{url}', '_blank')">
                <td data-label="Acknowledgement ID"><a href="{url}" target="_blank" rel="noopener">{b.acknowledgement_id}</a></td>
                <td data-label="Name"><a href="{url}" target="_blank" rel="noopener">{b.full_name}</a></td>
                <td data-label="Psychologist"><a href="{url}" target="_blank" rel="noopener">{psychologist}</a></td>
                <td data-label="Start"><a href="{url}" target="_blank" rel="noopener">{start}</a></td>
                <td data-label="End"><a href="{url}" target="_blank" rel="noopener">{end}</a></td>
                <td data-label="Status"><a href="{url}" target="_blank" rel="noopener">{b.status}</a></td>
                <td data-label="Mode"><a href="{url}" target="_blank" rel="noopener">{b.mode}</a></td>
            </tr>
"""
        html += """
        </tbody>
    </table>
</body>
</html>
"""
        return HttpResponse(html)

    def calendar_data_view(self, request):
        return JsonResponse(self.get_calendar_events(), safe=False)

    # ─────────────────────────
    # CALENDAR DATA (STEP 2)
    # ─────────────────────────
    def get_calendar_queryset(self):
        """
        Fetch bookings that should appear on admin calendar
        """
        return Booking.objects.filter(
            (
                Q(status="CONFIRMED") |
                (Q(status="APPROVED") & Q(mode="OFFLINE"))
            ),
            approved_slot_start__isnull=False,
            approved_slot_end__isnull=False,
        ).select_related("psychologist", "corporate")

    def get_calendar_events(self):
        """
        Return bookings in calendar-friendly format
        """
        events = []
        for booking in self.get_calendar_queryset():
            events.append({
                "id": booking.id,
                "title": f"{booking.full_name} ({booking.mode})",
                "start": booking.approved_slot_start,
                "end": booking.approved_slot_end,
                "status": booking.status,
                "psychologist": (
                    str(booking.psychologist)
                    if booking.psychologist else None
                ),
            })
        return events

    # ─────────────────────────
    # QUERYSET
    # ─────────────────────────
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Hide unverified drafts
        return qs.exclude(status="DRAFT")

    # ─────────────────────────
    # LIST VIEW
    # ─────────────────────────
    list_display = (
        "acknowledgement_id",
        "full_name",
        "user_email",
        "phone_number",
        "city",
        "status",
        "preferred_date",
        "preferred_period",
        "mode",
        "created_at",
    )

    list_filter = (
        "status",
        "mode",
        "preferred_period",
        "city",
    )

    search_fields = (
        "acknowledgement_id",
        "full_name",
        "user__email",
        "phone_number",
        "city",
    )

    ordering = ("-created_at",)
    actions = ["approve_bookings", "reject_bookings"]

    # ─────────────────────────
    # READ ONLY
    # ─────────────────────────
    readonly_fields = (
        "acknowledgement_id",
        "email_verified",
        "email_verified_at",
        "consent_given",
        "consent_given_at",
        "created_at",
        "updated_at",
        "cancelled_at",
        "cancelled_by",
        "preferred_date",
        "preferred_date_formatted",
    )

    # ─────────────────────────
    # FORM LAYOUT
    # ─────────────────────────
    fieldsets = (
        ("Personal Details", {
            "fields": (
                "full_name",
                "phone_number",
                "city",
                "user",
            )
        }),
        ("Verification", {
            "fields": (
                "email_verified",
                "email_verified_at",
            )
        }),
        ("User Preferences", {
            "fields": (
                "preferred_date",
                "preferred_period",
                "preferred_time_start",
                "preferred_time_end",
                "mode",
                "payment_mode",
                "user_message",
            )
        }),
        ("Admin Decision", {
            "fields": (
                "approved_slot_start",
                "approved_slot_end",
                "amount",
                "psychologist",
                "corporate",
                "rejection_reason",
                "alternate_slots",
            )
        }),
        ("System", {
            "fields": (
                "status",
                "acknowledgement_id",
                "created_at",
                "updated_at",
            )
        }),
    )

    # ─────────────────────────
    # DISPLAY HELPERS
    # ─────────────────────────
    @admin.display(description="Email")
    def user_email(self, obj):
        return obj.user.email if obj.user else "-"

    @admin.display(description="Preferred Date")
    def preferred_date_formatted(self, obj):
        if not obj.preferred_date:
            return "-"
        return obj.preferred_date.strftime("%d/%m/%Y")

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if "user" in form.base_fields:
            form.base_fields["user"].required = True
            form.base_fields["user"].help_text = (
                "Select the user for whom this booking is being created"
            )
        return form

    # ─────────────────────────
    # SAVE VALIDATION
    # ─────────────────────────
    def save_model(self, request, obj, form, change):

        # Prevent edits to finalized bookings
        if change:
            old = Booking.objects.get(pk=obj.pk)
            if old.status in {"COMPLETED", "CANCELLED"}:
                self.message_user(
                    request,
                    "This booking is finalized and cannot be modified.",
                    level=messages.ERROR,
                )
                return

        # Slot sanity checks
        if obj.approved_slot_start and obj.approved_slot_end:
            if obj.approved_slot_end <= obj.approved_slot_start:
                self.message_user(
                    request,
                    "Approved end time must be after start time.",
                    level=messages.ERROR,
                )
                return

            overlapping = Booking.objects.filter(
                status__in=["APPROVED", "CONFIRMED"],
                psychologist=obj.psychologist,
                approved_slot_start__lt=obj.approved_slot_end,
                approved_slot_end__gt=obj.approved_slot_start,
            ).exclude(pk=obj.pk)

            if overlapping.exists():
                messages.warning(
                    request,
                    "⚠️ This slot overlaps with another approved/confirmed booking."
                )

        super().save_model(request, obj, form, change)

    # ─────────────────────────
    # ADMIN ACTIONS
    # ─────────────────────────
    @admin.action(description="Approve selected bookings")
    def approve_bookings(self, request, queryset):
        for booking in queryset:

            if booking.status != "PENDING":
                messages.warning(
                    request,
                    f"{booking.acknowledgement_id}: Not pending."
                )
                continue

            if not booking.approved_slot_start or not booking.approved_slot_end:
                messages.error(
                    request,
                    f"{booking.acknowledgement_id}: Slot start & end required."
                )
                continue

            if booking.amount is None:
                messages.error(
                    request,
                    f"{booking.acknowledgement_id}: Amount required."
                )
                continue

            try:
                approve_booking(
                    booking=booking,
                    approved_start=booking.approved_slot_start,
                    approved_end=booking.approved_slot_end,
                    amount=booking.amount,
                    psychologist=booking.psychologist,
                    corporate=booking.corporate,
                )

                # ✅ EMAIL NOTIFICATION (Step 6)
                send_booking_approved_email(booking)

                messages.success(
                    request,
                    f"{booking.acknowledgement_id}: Approved successfully."
                )

            except Exception as e:
                messages.error(
                    request,
                    f"{booking.acknowledgement_id}: {str(e)}"
                )

    @admin.action(description="Reject selected bookings")
    def reject_bookings(self, request, queryset):
        for booking in queryset:

            if booking.status != "PENDING":
                messages.warning(
                    request,
                    f"{booking.acknowledgement_id}: Not pending."
                )
                continue

            if not booking.rejection_reason:
                messages.error(
                    request,
                    f"{booking.acknowledgement_id}: Rejection reason required."
                )
                continue

            try:
                reject_booking(
                    booking=booking,
                    reason=booking.rejection_reason,
                    alternate_slots=booking.alternate_slots,
                )

                # ✅ EMAIL NOTIFICATION (Step 6)
                send_booking_rejected_email(booking)

                messages.success(
                    request,
                    f"{booking.acknowledgement_id}: Rejected successfully."
                )

            except Exception as e:
                messages.error(
                    request,
                    f"{booking.acknowledgement_id}: {str(e)}"
                )
    formfield_overrides = {
        models.DateTimeField: {
            "widget": SplitDateTimeWidget(
                date_attrs={"type": "date"},
                time_attrs={"type": "time"}
            )
        }
    }