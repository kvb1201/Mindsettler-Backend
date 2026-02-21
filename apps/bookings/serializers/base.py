from rest_framework import serializers
from apps.bookings.models import Booking


class BookingBaseSerializer(serializers.ModelSerializer):
    """
    Base serializer shared across booking flows.
    Contains generic, non-state-specific validations only.
    """

    class Meta:
        model = Booking
        fields = "__all__"
        read_only_fields = (
            "id",
            "status",
            "acknowledgement_id",
            "email_verified",
            "email_verified_at",
            "submitted_at",
            "created_at",
            "updated_at",
        )

    # ─────────────────────────
    # FIELD-LEVEL VALIDATIONS
    # ─────────────────────────
    def validate_preferred_date(self, value):
        """
        Preferred date must be provided once booking
        moves beyond DRAFT.
        """
        if not value:
            raise serializers.ValidationError(
                "Preferred date is required"
            )
        return value

    # ─────────────────────────
    # OBJECT-LEVEL VALIDATIONS
    # ─────────────────────────
    def validate(self, data):
        """
        Generic sanity checks only.
        Do NOT enforce workflow/state rules here.
        """
        start = data.get("preferred_time_start")
        end = data.get("preferred_time_end")

        if start and end and start >= end:
            raise serializers.ValidationError(
                {
                    "preferred_time_end": (
                        "Preferred end time must be after start time"
                    )
                }
            )

        return data