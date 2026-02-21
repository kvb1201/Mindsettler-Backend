from rest_framework import serializers
from apps.bookings.models import Booking
from apps.bookings.utils.calendar import generate_google_calendar_link


class BookingPublicSerializer(serializers.ModelSerializer):
    """
    Public-facing booking serializer.
    Safe to expose to users after email verification.
    """

    add_to_calendar_url = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = (
            # ───────── Identity ─────────
            "acknowledgement_id",

            # ───────── Status ─────────
            "status",

            # ───────── User preferences ─────────
            "preferred_date",
            "preferred_period",
            "preferred_time_start",
            "preferred_time_end",
            "mode",

            # ───────── Admin-approved slot ─────────
            "approved_slot_start",
            "approved_slot_end",

            # ───────── Google Calendar ─────────
            "add_to_calendar_url",

            # ───────── Metadata ─────────
            "created_at",
        )

        read_only_fields = fields

    def get_add_to_calendar_url(self, obj):
        """
        Returns Google Calendar link only when booking is CONFIRMED.
        """
        return generate_google_calendar_link(obj)