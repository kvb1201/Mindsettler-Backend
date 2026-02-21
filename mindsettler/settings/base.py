"""
Base Django settings for MindSettler
"""

from pathlib import Path
import os
from dotenv import load_dotenv
from datetime import timedelta
import dj_database_url

# ───────────────────────────────
# Base directory & env loading
# ───────────────────────────────

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load .env ONLY for local development
load_dotenv(BASE_DIR / ".env")

# ───────────────────────────────
# Core security (DO NOT hard-crash here)
# ───────────────────────────────

SECRET_KEY = os.getenv("SECRET_KEY", "unsafe-dev-secret-key")

DEBUG = True
ALLOWED_HOSTS = []

# ───────────────────────────────
# Email (values only, no validation here)
# ───────────────────────────────

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
DEFAULT_FROM_EMAIL = "mindsettler.dev@gmail.com"

# Console email backend for development (prints emails to terminal)
if DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# ───────────────────────────────
# CORS (Frontend ↔ Backend)
# ───────────────────────────────

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    FRONTEND_URL,
]

from corsheaders.defaults import default_headers
CORS_ALLOW_HEADERS = list(default_headers)

CORS_ALLOW_CREDENTIALS = False

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    FRONTEND_URL,
]

# ───────────────────────────────
# Application definition
# ───────────────────────────────

INSTALLED_APPS = [
    # ───────── Admin Theme ─────────
    "jazzmin",

    # ───────── Django Core ─────────
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # ───────── Project Apps ─────────
    "apps.users",
    "apps.bookings",
    "apps.chatbot", 
    "apps.core",
    "apps.psychologists",
    "apps.corporates",

    # ───────── Third-party ─────────
    "rest_framework",
    "corsheaders",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",

    "apps.core.middleware.admin_activity.AdminActivityMiddleware",
    "apps.core.middleware.admin_no_cache.AdminNoCacheMiddleware",

    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "mindsettler.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "mindsettler.wsgi.application"

# ───────────────────────────────
# Database (SQLite local fallback)
# ───────────────────────────────

DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        ssl_require=False,
    )
}

# ───────────────────────────────
# Auth / Internationalization
# ───────────────────────────────

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ───────────────────────────────
# Static files
# ───────────────────────────────

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ───────────────────────────────
# REST & JWT
# ───────────────────────────────

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# ───────────────────────────────
# Session & CSRF
# ───────────────────────────────

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_AGE = 60 * 10
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = False

CSRF_COOKIE_HTTPONLY = False
# ─────────────────────────────
# JAZZMIN ADMIN THEME
# ─────────────────────────────

JAZZMIN_SETTINGS = {
    "site_title": "MindSettler Admin",
    "site_header": "MindSettler",
    "site_brand": "MindSettler",
    "welcome_sign": "Welcome to MindSettler Admin",
    "copyright": "MindSettler",

    "site_logo_classes": "img-circle",

    "topmenu_links": [
        {"name": "Dashboard", "url": "admin:index", "permissions": ["auth.view_user"]},
    ],

    "icons": {
        "apps.bookings": "fas fa-calendar-check",
        "apps.users": "fas fa-user",
        "apps.psychologists": "fas fa-brain",
        "apps.corporates": "fas fa-building",
    },

    "theme": "flatly",

    "custom_css": "admin/css/mindsettler.css",
}

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
