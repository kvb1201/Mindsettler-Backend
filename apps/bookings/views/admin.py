from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

from apps.bookings.models import Booking
from apps.bookings.services import approve_booking, reject_booking


class AdminApproveBookingView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, booking_id):
        booking = Booking.objects.get(id=booking_id)

        approve_booking(
            booking,
            approved_start=request.data["start"],
            approved_end=request.data["end"],
            psychologist=request.data.get("psychologist"),
            corporate=request.data.get("corporate"),
        )

        return Response({"message": "Booking approved. Awaiting user confirmation."})


class AdminRejectBookingView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, booking_id):
        booking = Booking.objects.get(id=booking_id)

        reject_booking(
            booking,
            reason=request.data.get("reason"),
            alternate_slots=request.data.get("alternate_slots", ""),
        )

        return Response({"message": "Booking rejected and user notified"})