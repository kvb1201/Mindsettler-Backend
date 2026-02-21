from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

from apps.bookings.models import Booking
from apps.bookings.serializers.public import BookingPublicSerializer
from apps.users.models import AppUser
from apps.bookings.services import get_active_booking
from apps.bookings.email import send_booking_verification_email


class BookingStatusCheckView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        acknowledgement_id = request.query_params.get("acknowledgement_id")

        if not acknowledgement_id:
            raise ValidationError("Acknowledgement ID is required")

        try:
            booking = Booking.objects.get(
                acknowledgement_id=acknowledgement_id
            )
        except Booking.DoesNotExist:
            raise ValidationError("Booking not found")

        # Build timeline
        timeline = []
        if booking.created_at:
            timeline.append("DRAFT")
        if booking.submitted_at:
            timeline.append("PENDING")
        if booking.approved_at:
            timeline.append("APPROVED")
        if booking.payment_requested_at:
            timeline.append("PAYMENT_PENDING")
        if booking.confirmed_at:
            timeline.append("CONFIRMED")
        if booking.cancelled_at:
            timeline.append("CANCELLED")
        if booking.rejected_at:
            timeline.append("REJECTED")

        serializer = BookingPublicSerializer(booking)
        data = serializer.data
        data["timeline"] = timeline
        data["amount"] = str(booking.amount) if booking.amount else None

        return Response(data)

    def post(self, request):
        email = request.data.get("email", "").strip().lower()

        if not email:
            raise ValidationError("Email is required")

        user, _ = AppUser.objects.get_or_create(email=email)
        booking = get_active_booking(user)

        if not booking:
            return Response(
                {
                    "has_booking": False,
                    "message": "No active booking found."
                },
                status=200,
            )

        # Throttle email
        if (
            booking.last_verification_email_sent_at
            and timezone.now() - booking.last_verification_email_sent_at
            < timedelta(seconds=60)
        ):
            return Response(
                {
                    "message": "Please wait before requesting another verification email."
                },
                status=429,
            )

        send_booking_verification_email(booking)

        booking.last_verification_email_sent_at = timezone.now()
        booking.save(update_fields=["last_verification_email_sent_at"])

        return Response(
            {
                "message": "Verification email sent. Verify to view your booking details."
            },
            status=200,
        )
