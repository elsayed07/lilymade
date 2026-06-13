"""Django settings for the Lilymade store backend."""

from datetime import timedelta
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


def env_list(name, default=""):
    raw = os.getenv(name, default)
    return [item.strip() for item in raw.split(",") if item.strip()]


SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-insecure-secret-key")

DEBUG = os.getenv("DJANGO_DEBUG", "True").lower() == "true"

ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1")


INSTALLED_APPS = [
    "modeltranslation",  # must precede django.contrib.admin
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    # Third party
    "rest_framework",
    "corsheaders",
    # Local
    "accounts",
    "catalog",
    "orders",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

# Use DATABASE_URL (Postgres) in production; fall back to SQLite for local dev.
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}

AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = "en"
TIME_ZONE = "Europe/Rome"
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ("en", "English"),
    ("it", "Italiano"),
]

MODELTRANSLATION_DEFAULT_LANGUAGE = "en"
MODELTRANSLATION_LANGUAGES = ("en", "it")

# Static & media
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Django REST Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.AllowAny",
    ),
    # Rate limiting. The scoped throttles below guard the abuse-prone endpoints
    # (login/register/checkout/password reset); anon/user cover everything else.
    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.ScopedRateThrottle",
    ),
    "DEFAULT_THROTTLE_RATES": {
        "anon": os.getenv("THROTTLE_ANON", "300/min"),
        "user": os.getenv("THROTTLE_USER", "600/min"),
        "login": os.getenv("THROTTLE_LOGIN", "10/min"),
        "register": os.getenv("THROTTLE_REGISTER", "5/min"),
        "checkout": os.getenv("THROTTLE_CHECKOUT", "20/min"),
        "password_reset": os.getenv("THROTTLE_PASSWORD_RESET", "5/min"),
    },
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=14),
}

# CORS
CORS_ALLOWED_ORIGINS = env_list(
    "CORS_ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
)

# Currencies — base is EUR; rates are editable in admin via CurrencyRate.
BASE_CURRENCY = "EUR"
SUPPORTED_CURRENCIES = ["EUR", "USD", "GBP", "CAD"]

# Shipping (amounts in EUR; converted per currency at checkout)
SHIPPING_FLAT_RATE_EUR = 7
FREE_SHIPPING_THRESHOLD_EUR = 100

# Stripe
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
# Let Stripe compute VAT/sales tax at checkout (configure tax registrations in Stripe).
# Leave off for VAT-exempt regimes (e.g. Italian regime forfettario).
STRIPE_AUTOMATIC_TAX = os.getenv("STRIPE_AUTOMATIC_TAX", "False").lower() == "true"
# How long a pending checkout holds reserved stock before Stripe expires it and the
# reservation is released (Stripe requires 30–1440 minutes).
CHECKOUT_SESSION_TTL_MINUTES = int(os.getenv("CHECKOUT_SESSION_TTL_MINUTES", "30"))

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# Email — order confirmations, seller notifications, password resets.
# Defaults to the console backend in dev (emails print to the log) and SMTP in prod.
EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend"
    if DEBUG
    else "django.core.mail.backends.smtp.EmailBackend",
)
EMAIL_HOST = os.getenv("EMAIL_HOST", "")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() == "true"
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "Lilymade <no-reply@lilymade.it>")
# Where new-order / dispute alerts go (the seller's inbox). Blank disables them.
ORDER_NOTIFICATION_EMAIL = os.getenv("ORDER_NOTIFICATION_EMAIL", "")

# CSRF trusted origins (needed for admin login over your domain in production)
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS")

# Production security (active when DEBUG is off; assumes TLS terminated at nginx/proxy)
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "True").lower() == "true"
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

# Logging — to stdout so Docker/gunicorn captures it.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"simple": {"format": "[{asctime}] {levelname} {name}: {message}", "style": "{"}},
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "simple"}},
    "root": {"handlers": ["console"], "level": os.getenv("LOG_LEVEL", "INFO")},
    "loggers": {
        "django.request": {"handlers": ["console"], "level": "WARNING", "propagate": False},
    },
}

# Error monitoring (optional). Set SENTRY_DSN to enable.
SENTRY_DSN = os.getenv("SENTRY_DSN", "")
if SENTRY_DSN:
    import sentry_sdk

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
        send_default_pii=False,
        environment="production" if not DEBUG else "development",
    )
