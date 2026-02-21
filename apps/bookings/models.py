from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
import uuid
import string
import random

from apps.users.models import AppUser
from apps.psychologists.models import Psychologist
from apps.corporates.models import Corporate


class Booking(models.Model):

    # ───────── CONSTANTS ─────────
    STATUS_CHOICES = [
        ("DRAFT", "Draft"),
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("PAYMENT_PENDING", "Payment Pending"),
        ("CONFIRMED", "Confirmed"),
        ("COMPLETED", "Completed"),
        ("REJECTED", "Rejected"),
        ("CANCELLED", "Cancelled"),
        ("PAYMENT_FAILED", "Payment Failed"),
    ]

    PERIOD_CHOICES = [
        ("MORNING", "Morning"),
        ("EVENING", "Evening"),
        ("CUSTOM", "Custom Range"),
    ]

    MODE_CHOICES = [
        ("ONLINE", "Online"),
        ("OFFLINE", "Offline"),
    ]

    PAYMENT_MODE_CHOICES = [
        ("ONLINE", "Online"),
        ("OFFLINE", "Offline"),
    ]

    GENDER_CHOICES = [
        ("MALE", "Male"),
        ("FEMALE", "Female"),
        ("OTHER", "Other"),
        ("PREFER_NOT_TO_SAY", "Prefer not to say"),
    ]

    # ───────── USER (AUTH ENTITY) ─────────
    user = models.ForeignKey(
        AppUser,
        on_delete=models.CASCADE,
        related_name="bookings",
    )

    # ───────── USER DETAILS (SNAPSHOT) ─────────
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)

    city = models.CharField(max_length=50, blank=True)
    state = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50, default="India")

    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(
        max_length=20,
        choices=GENDER_CHOICES,
        blank=True,
    )

    emergency_contact = models.CharField(
        max_length=15,
        blank=True,
    )

    # ───────── STATE ─────────
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="DRAFT",
    )

    # ───────── USER PREFERENCES ─────────
    preferred_date = models.DateField(null=True, blank=True)
    preferred_period = models.CharField(
        max_length=10,
        choices=PERIOD_CHOICES,
        null=True,
        blank=True,
    )

    preferred_time_start = models.TimeField(null=True, blank=True)
    preferred_time_end = models.TimeField(null=True, blank=True)

    # ───────── SESSION DETAILS ─────────
    mode = models.CharField(max_length=10, choices=MODE_CHOICES)
    payment_mode = models.CharField(
        max_length=10,
        choices=PAYMENT_MODE_CHOICES,
        null=True,
        blank=True,
    )

    user_message = models.TextField(blank=True)

    # ───────── ADMIN ASSIGNMENT ─────────
    psychologist = models.ForeignKey(
        Psychologist,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    corporate = models.ForeignKey(
        Corporate,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    approved_slot_start = models.DateTimeField(null=True, blank=True)
    approved_slot_end = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    rejection_reason = models.TextField(blank=True)
    alternate_slots = models.TextField(blank=True)

    # ───────── CONSENT ─────────
    consent_given = models.BooleanField(default=False)
    consent_given_at = models.DateTimeField(null=True, blank=True)

    # ───────── EMAIL VERIFICATION ─────────
    email_verified = models.BooleanField(default=False)
    email_verified_at = models.DateTimeField(null=True, blank=True)

    email_verification_token = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )

    last_verification_email_sent_at = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    # ───────── ACKNOWLEDGEMENT ─────────
    acknowledgement_id = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
    )

    # ───────── PAYMENT ─────────
    payment_reference = models.CharField(max_length=100, null=True, blank=True)
    payment_requested_at = models.DateTimeField(null=True, blank=True)

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    confirmed_at = models.DateTimeField(null=True, blank=True)

    # ───────── CANCELLATION FLOW ─────────
    cancellation_reason = models.TextField(blank=True, null=True)
    cancelled_at = models.DateTimeField(blank=True, null=True)

    cancelled_by = models.CharField(
        max_length=20,
        choices=(
            ("USER", "User"),
            ("ADMIN", "Admin"),
        ),
        blank=True,
        null=True,
    )

    cancellation_token = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
    )

    cancellation_requested_at = models.DateTimeField(null=True, blank=True)

    # ───────── TIMESTAMPS ─────────
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # ───────── Notifications ─────────
    approval_email_sent = models.BooleanField(default=False)
    rejection_email_sent = models.BooleanField(default=False)
    confirmation_email_sent = models.BooleanField(default=False)

    # ───────── VALIDATION ─────────
    def clean(self):
        if self.approved_slot_start and self.approved_slot_end:
            if self.approved_slot_end <= self.approved_slot_start:
                raise ValidationError({
                    "approved_slot_end": "End time must be after start time."
                })

        if self.phone_number and not self.phone_number.isdigit():
            raise ValidationError({
                "phone_number": "Phone number must contain digits only."
            })

    # ───────── DOMAIN HELPERS ─────────
    def generate_acknowledgement_id(self):
        while True:
            code = "MS-" + "".join(
                random.choices(string.ascii_uppercase + string.digits, k=6)
            )
            if not Booking.objects.filter(acknowledgement_id=code).exists():
                return code

    def save(self, *args, **kwargs):
        if not self.acknowledgement_id:
            self.acknowledgement_id = self.generate_acknowledgement_id()
        super().save(*args, **kwargs)

    def verify_email(self):
        self.email_verified = True
        self.email_verified_at = timezone.now()
        self.save(update_fields=["email_verified", "email_verified_at"])

    def __str__(self):
        return self.acknowledgement_id or f"Booking-{self.id}"

    class Meta:
        ordering = ["-created_at"]