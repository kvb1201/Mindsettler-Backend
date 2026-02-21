from datetime import timedelta

from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError

from apps.users.models import AppUser
from apps.bookings.serializers.draft import BookingDraftSerializer
from apps.bookings.services import get_active_booking
from apps.bookings.email import send_booking_verification_email


class BookingDraftCreateView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        email = request.data.get("email", "").strip().lower()
        consent = request.data.get("consent_given")

        # ─────────────────────────
        # Basic validation
        # ─────────────────────────
        if not email:
            raise ValidationError("Email is required")

        if consent is not True:
            raise ValidationError("Privacy policy consent required")

        user, _ = AppUser.objects.get_or_create(email=email)

        # ─────────────────────────
        # Active booking exists → email verification gate
        # ─────────────────────────
        active_booking = get_active_booking(user)

        if active_booking:
            # Throttle verification email
            if (
                active_booking.last_verification_email_sent_at
                and timezone.now() - active_booking.last_verification_email_sent_at
                < timedelta(seconds=60)
            ):
                return Response(
                    {
                        "message": (
                            "Please wait before requesting another verification email."
                        )
                    },
                    status=429,
                )

            send_booking_verification_email(active_booking)

            active_booking.last_verification_email_sent_at = timezone.now()
            active_booking.save(
                update_fields=["last_verification_email_sent_at"]
            )

            return Response(
                {
                    "message": (
                        "Please verify your email to continue "
                        "and view details of your existing booking."
                    )
                },
                status=200,
            )

        # ─────────────────────────
        # Create fresh draft booking (explicit intent)
        # ─────────────────────────
        serializer = BookingDraftSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        booking = serializer.save(
            user=user,
            status="DRAFT",
            consent_given=True,
            consent_given_at=timezone.now(),
        )

        send_booking_verification_email(booking)

        booking.last_verification_email_sent_at = timezone.now()
        booking.save(
            update_fields=["last_verification_email_sent_at"]
        )

        return Response(
            {
                "message": (
                    "Verification email sent. Please verify to submit booking."
                )
            },
            status=201,
        )