# apps/bookings/services/cancellation.py

from datetime import timedelta
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from .guards import assert_transition

# ─────────────────────────
# CONFIG
# ─────────────────────────
CANCELLATION_CUTOFF_HOURS = 24


# ─────────────────────────
# INTERNAL VALIDATION
# ─────────────────────────
def _validate_cancellation_window(booking):
    """
    Applies ONLY to CONFIRMED bookings.
    """
    if not booking.approved_slot_start:
        raise ValidationError("Approved slot not found")

    cutoff_time = booking.approved_slot_start - timedelta(
        hours=CANCELLATION_CUTOFF_HOURS
    )

    if timezone.now() > cutoff_time:
        raise ValidationError(
            f"Cancellation allowed only up to "
            f"{CANCELLATION_CUTOFF_HOURS} hours before the session"
        )


# ─────────────────────────
# USER CANCELLATION
# ─────────────────────────
def cancel_by_user(booking, reason=None):
    """
    USER cancellation rules:
    - PENDING         → immediate cancel (no verification)
    - PAYMENT_PENDING → immediate cancel (no verification)
    - APPROVED        → immediate cancel (no verification)
    - CONFIRMED       → allowed only before cutoff window
    """

    if booking.status not in {
        "PENDING",
        "PAYMENT_PENDING",
        "APPROVED",
        "CONFIRMED",
    }:
        raise ValidationError(
            "This booking cannot be cancelled at its current stage"
        )

    assert_transition(booking.status, "CANCELLED")

    # Apply cutoff ONLY for confirmed bookings
    if booking.status == "CONFIRMED":
        _validate_cancellation_window(booking)

    booking.status = "CANCELLED"
    booking.cancellation_reason = (
        reason
        or (
            "Cancelled before payment"
            if booking.status == "PAYMENT_PENDING"
            else "Cancelled by user"
        )
    )
    booking.cancelled_at = timezone.now()
    booking.cancelled_by = "USER"

    # Cleanup flow artifacts
    booking.cancellation_token = None
    booking.cancellation_requested_at = None
    booking.payment_reference = None
    booking.payment_requested_at = None

    booking.save(update_fields=[
        "status",
        "cancellation_reason",
        "cancelled_at",
        "cancelled_by",
        "cancellation_token",
        "cancellation_requested_at",
        "payment_reference",
        "payment_requested_at",
    ])

    return booking


# ─────────────────────────
# ADMIN CANCELLATION
# ─────────────────────────
def cancel_by_admin(booking, reason=None):
    """
    ADMIN cancellation:
    Allowed for:
    - PAYMENT_PENDING
    - APPROVED
    - CONFIRMED
    No time restriction
    """

    if booking.status not in {
        "PAYMENT_PENDING",
        "APPROVED",
        "CONFIRMED",
    }:
        raise ValidationError("Booking cannot be cancelled")

    assert_transition(booking.status, "CANCELLED")

    booking.status = "CANCELLED"
    booking.cancellation_reason = reason or "Cancelled by admin"
    booking.cancelled_at = timezone.now()
    booking.cancelled_by = "ADMIN"

    booking.cancellation_token = None
    booking.cancellation_requested_at = None
    booking.payment_reference = None
    booking.payment_requested_at = None

    booking.save(update_fields=[
        "status",
        "cancellation_reason",
        "cancelled_at",
        "cancelled_by",
        "cancellation_token",
        "cancellation_requested_at",
        "payment_reference",
        "payment_requested_at",
    ])

    return booking