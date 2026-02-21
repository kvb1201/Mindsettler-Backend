from .base import BookingBaseSerializer


class BookingDraftSerializer(BookingBaseSerializer):
    """
    Serializer used ONLY for draft creation.
    Ensures user cannot touch system-managed fields.
    """

    class Meta(BookingBaseSerializer.Meta):
        read_only_fields = (
            # ───────── Ownership / System ─────────
            "id",
            "user",
            "status",
            "acknowledgement_id",

            # ───────── Verification ─────────
            "email_verified",
            "email_verified_at",
            "last_verification_email_sent_at",

            # ───────── Consent (set explicitly in view) ─────────
            "consent_given",
            "consent_given_at",

            # ───────── Admin-only fields ─────────
            "approved_slot_start",
            "approved_slot_end",
            "approved_at",
            "amount",
            "psychologist",
            "corporate",
            "rejection_reason",
            "alternate_slots",

            # ───────── Payment / Confirmation ─────────
            "payment_reference",
            "payment_requested_at",
            "confirmation_token",
            "confirmed_at",

            # ───────── Cancellation ─────────
            "cancellation_token",
            "cancellation_requested_at",
            "cancellation_reason",
            "cancelled_at",
            "cancelled_by",

            # ───────── Timestamps ─────────
            "submitted_at",
            "created_at",
            "updated_at",
        )