from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError

from apps.bookings.models import Booking
from apps.bookings.services import get_active_booking, submit_booking
from apps.bookings.serializers.public import BookingPublicSerializer


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        token = request.query_params.get("token")

        if not token:
            raise ValidationError("Verification token is required")

        try:
            booking = Booking.objects.select_related("user").get(
                email_verification_token=token
            )
        except Booking.DoesNotExist:
            raise ValidationError("Invalid or expired verification link")

        # ─────────────────────────
        # Active booking guard
        # ─────────────────────────
        active = get_active_booking(booking.user)
        if active and active.id != booking.id:
            booking.status = "REJECTED"
            booking.rejection_reason = "Another active booking exists"
            booking.save(update_fields=["status", "rejection_reason"])

            return Response(
                {
                    "message": (
                        "Another active booking already exists. "
                        "This request was rejected."
                    ),
                    "status": "REJECTED",
                },
                status=200,
            )

        # ─────────────────────────
        # Email verification (idempotent)
        # ─────────────────────────
        if not booking.email_verified:
            booking.verify_email()

        # ─────────────────────────
        # Submit booking lifecycle
        # ─────────────────────────
        if booking.status == "DRAFT":
            submit_booking(booking)

        # ─────────────────────────
        # Ensure acknowledgement ID
        # ─────────────────────────
        if not booking.acknowledgement_id:
            booking.generate_acknowledgement_id()

        # ─────────────────────────
        # Public response
        # Calendar link appears ONLY after payment (CONFIRMED)
        # ─────────────────────────
        serializer = BookingPublicSerializer(booking)

        return Response(
            {
                "message": "Email verified successfully",
                "booking": serializer.data,
            },
            status=200,
        )