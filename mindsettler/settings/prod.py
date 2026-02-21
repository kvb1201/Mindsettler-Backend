"""
Production settings for MindSettler
"""

from .base import *
import os
import dj_database_url

# ─────────────────────────────
# CORE
# ─────────────────────────────

DEBUG = False

SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY not set")

ALLOWED_HOSTS = [
    ".onrender.com",
]

# ─────────────────────────────
# DATABASE (Render PostgreSQL)
# ─────────────────────────────

DATABASES = {
    "default": dj_database_url.parse(
        os.environ.get("DATABASE_URL"),
        conn_max_age=600,
        ssl_require=True,
    )
}

# ─────────────────────────────
# STATIC FILES
# ─────────────────────────────

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# ─────────────────────────────
# EMAIL 
# ─────────────────────────────

SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
if not SENDGRID_API_KEY:
    raise RuntimeError("SENDGRID_API_KEY not set")

DEFAULT_FROM_EMAIL = "mindsettler.dev@gmail.com"

# ─────────────────────────────
# FRONTEND
# ─────────────────────────────

FRONTEND_URL = os.environ.get(
    "FRONTEND_URL",
    "https://mindsettler.vercel.app"
)

# ─────────────────────────────
# CORS 
# ─────────────────────────────

CORS_ALLOWED_ORIGINS = [
    FRONTEND_URL,
]

CORS_ALLOW_CREDENTIALS = True


# ─────────────────────────────
# JAZZMIN – ADMIN SIDEBAR LINKS
# ─────────────────────────────

JAZZMIN_SETTINGS = {
    "custom_links": {
        "bookings": [
            {
                "name": "Booking Calendar",
                "url": "/admin/bookings/booking/calendar/",
                "icon": "fas fa-calendar-alt",
            },
            {
                "name": "Booking List View",
                "url": "/admin/bookings/booking/calendar/list/",
                "icon": "fas fa-list",
            },
        ]
    }
}




# ─────────────────────────────
# SECURITY
# ─────────────────────────────

CSRF_TRUSTED_ORIGINS = [
    FRONTEND_URL,
    "https://*.onrender.com",
]

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# ─────────────────────────────
# LOGGING
# ─────────────────────────────

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}