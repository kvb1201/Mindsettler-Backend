from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny

from apps.users.models import AppUser
from apps.bookings.models import Booking
from apps.bookings.services import has_active_booking
from apps.bookings.email import send_booking_verification_email


class ChatbotIntentView(APIView):
    """
    Chatbot entry point for session booking.
    Creates a DRAFT booking and sends verification email.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        intent = request.data.get("intent")

        if intent != "book_session":
            raise ValidationError("Unsupported intent")

        email = request.data.get("email", "").strip().lower()
        name = request.data.get("name", "").strip()
        phone = request.data.get("phone", "").strip()

        if not email:
            raise ValidationError("Email is required")

        # Create or fetch user
        user, _ = AppUser.objects.get_or_create(
            email=email,
            defaults={
                "full_name": name,
                "phone": phone,
            }
        )

        # Block if user already has an active booking
        if has_active_booking(user):
            return Response(
                {
                    "message": "You already have an active or pending session request."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create DRAFT booking (NOT ACTIVE YET)
        booking = Booking.objects.create(
            user=user,
            session_type=request.data.get("session_type"),
            preferred_period=request.data.get("preferred_period"),
            preferred_time_start=request.data.get("preferred_time_start"),
            preferred_time_end=request.data.get("preferred_time_end"),
            mode=request.data.get("mode"),
            payment_mode=request.data.get("payment_mode"),
            user_message=request.data.get("user_message", ""),
        )

        # Send verification email
        send_booking_verification_email(booking)

        return Response(
            {
                "message": "Verification email sent. Please verify to submit your request."
            },
            status=status.HTTP_201_CREATED
        )