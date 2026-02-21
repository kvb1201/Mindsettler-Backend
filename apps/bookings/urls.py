from django.urls import path
from .views import (
    BookingDraftCreateView,
    VerifyEmailView,
    ConfirmBookingView,
    AdminApproveBookingView,
    AdminRejectBookingView,
    RequestCancellationView,
    VerifyCancellationView,
    BookingStatusCheckView,
)

from .views.payments import (
    InitiatePaymentView,
    CompletePaymentView,
)

urlpatterns = [
    # ───── User flow ─────
    path("draft/", BookingDraftCreateView.as_view()),
    path("verify-email/", VerifyEmailView.as_view()),
    path("confirm/", ConfirmBookingView.as_view()),
    path("check-status/", BookingStatusCheckView.as_view()),

    path("request-cancellation/", RequestCancellationView.as_view()),
    path("verify-cancellation/", VerifyCancellationView.as_view()),

    # ───── Payments ─────
    path("initiate-payment/", InitiatePaymentView.as_view()),
    path("complete-payment/", CompletePaymentView.as_view()),

    # ───── Admin flow ─────
    path("admin/bookings/<int:booking_id>/approve/", AdminApproveBookingView.as_view()),
    path("admin/bookings/<int:booking_id>/reject/", AdminRejectBookingView.as_view()),
]