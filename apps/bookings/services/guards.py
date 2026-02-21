from rest_framework.exceptions import ValidationError


# ─────────────────────────
# STATE MACHINE
# ─────────────────────────
ALLOWED_TRANSITIONS = {
    "DRAFT": {"PENDING", "REJECTED"},
    "PENDING": {"APPROVED", "REJECTED", "CANCELLED"},
    "APPROVED": {"PAYMENT_PENDING", "CONFIRMED", "CANCELLED"},
    "PAYMENT_PENDING": {
        "CONFIRMED",
        "PAYMENT_FAILED",
        "CANCELLED",   #
    },
    "CONFIRMED": {"COMPLETED", "CANCELLED"},
}


def assert_transition(current: str, target: str):
    allowed = ALLOWED_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise ValidationError(
            f"Invalid state transition: {current} → {target}"
        )


# ─────────────────────────
# GENERIC GUARDS (REQUIRED)
# ─────────────────────────
def ensure_status(booking, allowed_statuses: set):
    if booking.status not in allowed_statuses:
        raise ValidationError(
            f"Invalid booking status: {booking.status}"
        )


def ensure_email_verified(booking):
    """
    Hard gate before:
    - payment initiation
    - confirmations
    - protected booking actions
    """
    if not booking.email_verified:
        raise ValidationError(
            "Email verification required before proceeding"
        )


def ensure_amount_set(booking):
    if booking.amount is None:
        raise ValidationError("Booking amount not set")


def ensure_payment_reference(booking):
    if not booking.payment_reference:
        raise ValidationError("Payment reference missing")


def ensure_payment_not_required(booking):
    """
    Used to bypass payment flow for offline sessions
    with offline payment mode.
    """
    if booking.mode == "OFFLINE" and booking.payment_mode == "OFFLINE":
        return
    raise ValidationError("Payment is required for this booking")