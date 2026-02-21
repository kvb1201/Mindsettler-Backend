# apps/bookings/utils/calendar.py

from urllib.parse import urlencode
from django.utils.timezone import localtime


def generate_google_calendar_link(booking):
    """
    Generates a Google Calendar 'Add to Calendar' link
    for CONFIRMED bookings only.
    """

    # Only confirmed bookings should expose calendar link
    if booking.status != "CONFIRMED":
        return None

    if not booking.approved_slot_start or not booking.approved_slot_end:
        return None

    # Google Calendar expects local datetime without timezone suffix
    start = localtime(booking.approved_slot_start).strftime("%Y%m%dT%H%M%S")
    end = localtime(booking.approved_slot_end).strftime("%Y%m%dT%H%M%S")

    title = "MindSettler Counseling Session"

    description = (
        f"Session ID: {booking.acknowledgement_id}\n"
        f"Mode: {booking.mode}\n\n"
        "Please arrive 5 minutes early."
    )

    location = (
        "MindSettler Studio"
        if booking.mode == "OFFLINE"
        else "Online Session"
    )

    params = {
        "action": "TEMPLATE",
        "text": title,
        "dates": f"{start}/{end}",
        "details": description,
        "location": location,
    }

    return "https://calendar.google.com/calendar/render?" + urlencode(params)