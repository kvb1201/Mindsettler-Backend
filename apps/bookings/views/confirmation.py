from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError

from apps.bookings.models import Booking
from apps.bookings.services import confirm_booking


class ConfirmBookingView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        token = request.data.get("token")

        if not token:
            raise ValidationError("Confirmation token required")

        try:
            booking = Booking.objects.get(confirmation_token=token)
        except Booking.DoesNotExist:
            raise ValidationError("Invalid or expired token")

        if not booking.email_verified:
            raise ValidationError("Email verification required")

        confirm_booking(booking)

        return Response({
            "message": "Booking confirmed",
            "acknowledgement_id": booking.acknowledgement_id,
        })