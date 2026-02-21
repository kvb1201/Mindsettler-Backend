from django.utils import timezone
from rest_framework.exceptions import ValidationError
from decimal import Decimal

from .guards import assert_transition


def submit_booking(booking):
    """
    DRAFT → PENDING
    """
    assert_transition(booking.status, "PENDING")

    booking.status = "PENDING"
    booking.submitted_at = timezone.now()

    booking.save(update_fields=["status", "submitted_at"])
    return booking


def approve_booking(
    booking,
    approved_start,
    approved_end,
    amount,
    psychologist=None,
    corporate=None,
):
    """
    PENDING → APPROVED
    Amount is finalized here (single source of truth)
    """
    assert_transition(booking.status, "APPROVED")

    booking.status = "APPROVED"
    booking.approved_slot_start = approved_start
    booking.approved_slot_end = approved_end
    booking.amount = Decimal(amount)
    booking.psychologist = psychologist
    booking.corporate = corporate
    booking.approved_at = timezone.now()

    booking.save(update_fields=[
        "status",
        "approved_slot_start",
        "approved_slot_end",
        "amount",
        "psychologist",
        "corporate",
        "approved_at",
    ])

    return booking


def move_to_payment_pending(booking, payment_reference):
    """
    APPROVED → PAYMENT_PENDING
    (Idempotent-safe)
    """
    if booking.status == "PAYMENT_PENDING":
        return booking

    assert_transition(booking.status, "PAYMENT_PENDING")

    booking.status = "PAYMENT_PENDING"
    booking.payment_reference = payment_reference
    booking.payment_requested_at = timezone.now()

    booking.save(update_fields=[
        "status",
        "payment_reference",
        "payment_requested_at",
    ])
    return booking


def confirm_booking(booking):
    """
    PAYMENT_PENDING → CONFIRMED
    """
    assert_transition(booking.status, "CONFIRMED")

    booking.status = "CONFIRMED"
    booking.confirmed_at = timezone.now()

    booking.save(update_fields=["status", "confirmed_at"])
    return booking


def cancel_booking(booking, reason=None):
    """
    PENDING / APPROVED / PAYMENT_PENDING / CONFIRMED → CANCELLED
    """
    if booking.status in {"CANCELLED", "COMPLETED"}:
        raise ValidationError("Booking cannot be cancelled")

    assert_transition(booking.status, "CANCELLED")

    booking.status = "CANCELLED"
    booking.cancellation_reason = reason or "Cancelled by user"
    booking.cancelled_at = timezone.now()

    booking.save(update_fields=[
        "status",
        "cancellation_reason",
        "cancelled_at",
    ])
    return booking