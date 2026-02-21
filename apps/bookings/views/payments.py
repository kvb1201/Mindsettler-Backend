from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError

from apps.bookings.models import Booking
from apps.bookings.services import initiate_payment, complete_payment


class InitiatePaymentView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        acknowledgement_id = request.data.get("acknowledgement_id")

        if not acknowledgement_id:
            raise ValidationError("Acknowledgement ID is required")

        try:
            booking = Booking.objects.get(
                acknowledgement_id=acknowledgement_id
            )
        except Booking.DoesNotExist:
            raise ValidationError("Invalid acknowledgement ID")

        data = initiate_payment(booking)

        return Response({
            "message": "Payment initiated",
            **data
        })
    

class CompletePaymentView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        payment_reference = request.data.get("payment_reference")

        if not payment_reference:
            raise ValidationError("Payment reference is required")

        try:
            booking = Booking.objects.get(
                payment_reference=payment_reference
            )
        except Booking.DoesNotExist:
            raise ValidationError("Invalid payment reference")

        complete_payment(booking)

        return Response({
            "message": "Payment successful",
            "status": booking.status
        })