from django.utils import timezone
from rest_framework.exceptions import ValidationError

from .guards import assert_transition


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
    If OFFLINE + OFFLINE payment → CONFIRMED directly
    """
    assert_transition(booking.status, "APPROVED")

    booking.approved_slot_start = approved_start
    booking.approved_slot_end = approved_end
    booking.amount = amount
    booking.psychologist = psychologist
    booking.corporate = corporate
    booking.approved_at = timezone.now()

    # Offline session + offline payment → skip payment flow
    if booking.mode == "OFFLINE" and booking.payment_mode == "OFFLINE":
        assert_transition("APPROVED", "CONFIRMED")
        booking.status = "CONFIRMED"
        booking.confirmed_at = timezone.now()
        update_fields = [
            "status",
            "approved_slot_start",
            "approved_slot_end",
            "amount",
            "psychologist",
            "corporate",
            "approved_at",
            "confirmed_at",
        ]
    else:
        booking.status = "APPROVED"
        update_fields = [
            "status",
            "approved_slot_start",
            "approved_slot_end",
            "amount",
            "psychologist",
            "corporate",
            "approved_at",
        ]

    booking.save(update_fields=update_fields)
    return booking


def reject_booking(booking, reason, alternate_slots=None):
    """
    PENDING → REJECTED
    """
    assert_transition(booking.status, "REJECTED")

    booking.status = "REJECTED"
    booking.rejection_reason = reason
    booking.alternate_slots = alternate_slots
    booking.rejected_at = timezone.now()

    booking.save(update_fields=[
        "status",
        "rejection_reason",
        "alternate_slots",
        "rejected_at",
    ])

    return booking