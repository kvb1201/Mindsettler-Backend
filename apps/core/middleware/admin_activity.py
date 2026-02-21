from django.utils import timezone
from django.shortcuts import redirect
from django.contrib.auth import logout
from datetime import timedelta


class AdminActivityMiddleware:
    """
    Force admin logout after inactivity.
    HARD BLOCK — browser independent.
    """

    IDLE_TIMEOUT = timedelta(minutes=10)

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if request.path.startswith("/admin/"):
            user = request.user

            if user.is_authenticated and user.is_staff:
                now = timezone.now()
                last_seen = request.session.get("admin_last_seen")

                if last_seen:
                    last_seen = timezone.datetime.fromisoformat(last_seen)

                    if now - last_seen > self.IDLE_TIMEOUT:
                        logout(request)
                        request.session.flush()
                        return redirect("/admin/login/?timeout=1")

                #  update ONLY on admin HTML pages
                if request.method == "GET" and "text/html" in request.META.get("HTTP_ACCEPT", ""):
                    request.session["admin_last_seen"] = now.isoformat()

        return self.get_response(request)