import uuid
from django.conf import settings
from django.utils import timezone
from datetime import timezone as dt_timezone
from rest_framework.exceptions import ValidationError

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from python_http_client.exceptions import ForbiddenError, UnauthorizedError


def _send_email(message):
    """
    Best-effort email sender.
    - Attempts to send email via SendGrid.
    - Logs errors and returns False on failure, True on success.
    """

    api_key = getattr(settings, "SENDGRID_API_KEY", None)

    if not api_key:
        print("Email service misconfigured: SENDGRID_API_KEY missing")
        return False

    try:
        sg = SendGridAPIClient(api_key)
        sg.send(message)
        return True

    except (ForbiddenError, UnauthorizedError) as e:
        print(f"Email service rejected request (invalid API key or sender identity): {str(e)}")
        return False

    except Exception as e:
        print(f"Failed to send email. Please try again later. ({str(e)})")
        return False


def send_booking_verification_email(booking):
    verification_url = (
        f"{settings.FRONTEND_URL}/verify-email"
        f"?token={booking.email_verification_token}"
    )

    message = Mail(
        from_email="MindSettler Support <{}>".format(settings.DEFAULT_FROM_EMAIL),
        to_emails=booking.user.email,
        subject="Verify your email for MindSettler",
        plain_text_content="""
Hello,

You recently started a booking on MindSettler.

Please verify your email to continue: {verification_url}

If you did not request this, you can safely ignore this email.

MindSettler
support@mindsettler.in
""",
        html_content=f"""
<div style="max-width:520px;margin:0 auto;font-family:Arial,Helvetica,sans-serif;color:#333;line-height:1.6;">
  <p>Hello,</p>

  <p>You recently started a booking on MindSettler.</p>

  <p>Please verify your email address by clicking the button below:</p>

  <div style="margin:24px 0;text-align:center;">
    <a href="{verification_url}"
       style="display:inline-block;padding:12px 24px;background:#453859;color:#ffffff;text-decoration:none;border-radius:4px;font-size:14px;">
      Verify email
    </a>
  </div>

  <p style="font-size:13px;color:#555;">
    Or copy this link into your browser:<br/>
    <a href="{verification_url}">{verification_url}</a>
  </p>

  <hr style="border:none;border-top:1px solid #e6e6e6;margin:24px 0;" />

  <p style="font-size:12px;color:#777;">
    This email was sent because a booking was initiated on MindSettler.<br/>
    If this wasn’t you, you can safely ignore this message.
  </p>

  <p style="font-size:12px;color:#777;">
    MindSettler · support@mindsettler.in
  </p>

  <p style="font-size:12px;color:#777;">
    This is a transactional email related to your MindSettler booking.
  </p>
</div>
""",
    )

    _send_email(message)

    booking.last_verification_email_sent_at = timezone.now()
    booking.save(update_fields=["last_verification_email_sent_at"])

def send_cancellation_verification_email(booking):
    booking.cancellation_token = uuid.uuid4()
    booking.cancellation_requested_at = timezone.now()
    booking.save(update_fields=[
        "cancellation_token",
        "cancellation_requested_at",
    ])

    cancel_url = (
        f"{settings.FRONTEND_URL}/verify-cancellation"
        f"?token={booking.cancellation_token}"
    )

    message = Mail(
        from_email="MindSettler Support <{}>".format(settings.DEFAULT_FROM_EMAIL),
        to_emails=booking.user.email,
        subject="Confirm cancellation request – MindSettler",
        plain_text_content="""
Hello,

We received a request to cancel a booking on MindSettler.

Please open this email and use the button to confirm the cancellation.

If you did not request this, you can ignore this message.

MindSettler
support@mindsettler.in
""",
        html_content=f"""
<div style="max-width:520px;
            margin:0 auto;
            font-family:Arial, Helvetica, sans-serif;
            color:#333;
            line-height:1.6;">

  <p>Hello,</p>

  <p>
    We received a request to cancel a booking on
    <strong>MindSettler</strong>.
  </p>

  <p>
    Please confirm your request using the button below.
  </p>

  <div style="margin:28px 0; text-align:center;">
    <a href="{cancel_url}"
       style="display:inline-block;
              padding:12px 24px;
              background:#e55d80;
              color:#ffffff;
              text-decoration:none;
              border-radius:4px;
              font-size:15px;">
      Confirm cancellation
    </a>
  </div>

  <p style="font-size:13px;color:#666;">
    If you did not request this cancellation, you may safely ignore this email.
  </p>

  <hr style="border:none;border-top:1px solid #e6e6e6;margin:24px 0;" />

  <p style="font-size:12px;color:#777;">
    MindSettler – Mental Wellness Platform<br />
    Support: support@mindsettler.in
  </p>

  <p style="font-size:12px;color:#777;">
    This is a transactional email related to your MindSettler booking.
  </p>

</div>
""",
    )

    _send_email(message)

def send_booking_approved_email(booking):
    """
    Sends approval notification email (idempotent).
    """
    if booking.approval_email_sent:
        return

    message = Mail(
        from_email="MindSettler Support <{}>".format(settings.DEFAULT_FROM_EMAIL),
        to_emails=booking.user.email,
        subject="Your MindSettler session has been approved",
        html_content=f"""
<div style="max-width:600px;margin:0 auto;font-family:Arial,Helvetica,sans-serif;color:#333;line-height:1.6;">
  <h2 style="color:#453859;">Session Approved ✅</h2>

  <p>Hello,</p>

  <p>Your MindSettler session request has been approved with the following details:</p>

  <table style="border-collapse:collapse;margin-top:12px;">
    <tr><td><strong>Booking ID</strong></td><td>{booking.acknowledgement_id}</td></tr>
    <tr><td><strong>Date</strong></td><td>{booking.approved_slot_start.date()}</td></tr>
    <tr>
      <td><strong>Time</strong></td>
      <td>{booking.approved_slot_start.strftime("%H:%M")} – {booking.approved_slot_end.strftime("%H:%M")}</td>
    </tr>
    <tr><td><strong>Amount</strong></td><td>₹{booking.amount}</td></tr>
  </table>

  <p style="margin-top:16px;">
    Please proceed with payment to confirm your appointment.
  </p>

  <hr style="border:none;border-top:1px solid #e6e6e6;margin:24px 0;" />

  <p style="font-size:12px;color:#777;">
    This is a transactional email related to your MindSettler booking.<br/>
    Support: support@mindsettler.in
  </p>
</div>
""",
    )

    _send_email(message)

    booking.approval_email_sent = True
    booking.save(update_fields=["approval_email_sent"])


def send_booking_confirmed_email(booking):
    """
    Sends confirmation email after successful payment.
    Must be sent exactly once.
    """
    if getattr(booking, "confirmation_email_sent", False):
        return

    appointment_date = booking.approved_slot_start.strftime("%A, %d %B %Y")
    appointment_time = (
        f"{booking.approved_slot_start.strftime('%I:%M %p')} – "
        f"{booking.approved_slot_end.strftime('%I:%M %p')}"
    )

    start = booking.approved_slot_start.astimezone(dt_timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    end = booking.approved_slot_end.astimezone(dt_timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    calendar_url = (
        "https://www.google.com/calendar/render?action=TEMPLATE"
        f"&text=MindSettler+Session+({booking.acknowledgement_id})"
        f"&dates={start}/{end}"
        f"&details=MindSettler+session+({booking.mode})"
    )

    message = Mail(
        from_email="MindSettler Support <{}>".format(settings.DEFAULT_FROM_EMAIL),
        to_emails=booking.user.email,
        subject="Your MindSettler session is confirmed 🌿",
        html_content=f"""
        <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;color:#333;line-height:1.6;">
            <h2 style="color:#453859;">Appointment Confirmed 🎉</h2>

            <p>Hello,</p>

            <p>
                We’re happy to let you know that your MindSettler session has been
                <strong>successfully confirmed</strong>.
            </p>

            <h3 style="margin-top:24px;">🗓 Appointment Details</h3>
            <table style="border-collapse:collapse;">
                <tr><td><strong>Booking ID</strong></td><td>{booking.acknowledgement_id}</td></tr>
                <tr><td><strong>Date</strong></td><td>{appointment_date}</td></tr>
                <tr><td><strong>Time</strong></td><td>{appointment_time}</td></tr>
                <tr><td><strong>Mode</strong></td><td>{booking.mode}</td></tr>
                <tr><td><strong>Amount Paid</strong></td><td>₹{booking.amount}</td></tr>
            </table>

            <div style="margin:24px 0; text-align:center;">
              <a href="{calendar_url}"
                 style="display:inline-block;
                        padding:12px 24px;
                        background:#453859;
                        color:#ffffff;
                        text-decoration:none;
                        border-radius:4px;
                        font-size:14px;">
                ➕ Add to Google Calendar
              </a>
            </div>

            <h3 style="margin-top:28px;">❌ Cancellation Policy</h3>
            <ul>
                <li>Cancellations must be requested at least <strong>24 hours</strong> before the session.</li>
                <li>Late cancellations may not be eligible for a refund.</li>
                <li>All cancellations require email verification for security.</li>
            </ul>

            <p style="margin-top:28px;">
                If you need to cancel or have any questions, please reach out to us at
                <a href="mailto:support@mindsettler.in">support@mindsettler.in</a>.
            </p>

            <br />
            <p>
                Warm regards,<br />
                <strong>MindSettler Team</strong><br />
                <small>Your Sanctuary for Emotional Well-being</small>
            </p>

            <p style="font-size:12px;color:#777;">
              This is a transactional email related to your MindSettler booking.
            </p>
        </div>
        """,
    )

    _send_email(message)

    booking.confirmation_email_sent = True
    booking.save(update_fields=["confirmation_email_sent"])


def send_booking_rejected_email(booking):
    """
    Sends rejection notification email (idempotent).
    """
    if booking.rejection_email_sent:
        return

    message = Mail(
        from_email="MindSettler Support <{}>".format(settings.DEFAULT_FROM_EMAIL),
        to_emails=booking.user.email,
        subject="Update on your MindSettler booking",
        html_content=f"""
        <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;">
            <h2 style="color:#c0392b;">Booking Update</h2>

            <p>Hello,</p>

            <p>Unfortunately, your booking request could not be approved.</p>

            <p><strong>Reason:</strong></p>
            <div style="background:#faf9fb;padding:12px;border-left:4px solid #c0392b;">
                {booking.rejection_reason}
            </div>

            {"<p><strong>Suggested alternate slots:</strong></p><p>" + booking.alternate_slots + "</p>" if booking.alternate_slots else ""}

            <p>You are welcome to submit a new request anytime.</p>

            <br />
            <p>— MindSettler Team<br/>
            <small>support@mindsettler.in</small></p>

            <p style="font-size:12px;color:#777;">
              This is a transactional email related to your MindSettler booking.
            </p>
        </div>
        """,
    )

    _send_email(message)

    booking.rejection_email_sent = True
    booking.save(update_fields=["rejection_email_sent"])