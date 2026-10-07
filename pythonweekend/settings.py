from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)
raw_hosts = config("ALLOWED_HOSTS", default="*")
ALLOWED_HOSTS = [host.strip() for host in raw_hosts.split(",") if host.strip()]
import os
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
if "*" not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append("*")

SITE_NAME = config("SITE_NAME", default="Python Weekend")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.flatpages",
    # Project apps
    "core",
    "content",
    "coach",
    "sponsors",
    "applications",
    "newsletter",
    "subscribers",
    "tutorials",
]

SITE_ID = 1

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.contrib.flatpages.middleware.FlatpageFallbackMiddleware",
]

ROOT_URLCONF = "pythonweekend.urls"

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
            "builtins": [
                "content.templatetags.content_tags",
            ],
        },
    },
]

WSGI_APPLICATION = "pythonweekend.wsgi.application"

import dj_database_url

DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = config("TIME_ZONE", default="Europe/London")
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
# NOTE: static files storage backend is set via STORAGES["staticfiles"] below (Django 4.2+)

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CLOUDINARY_URL = config("CLOUDINARY_URL", default="")
CLOUDINARY_CLOUD_NAME = config("CLOUDINARY_CLOUD_NAME", default="")
CLOUDINARY_API_KEY = config("CLOUDINARY_API_KEY", default="")
CLOUDINARY_API_SECRET = config("CLOUDINARY_API_SECRET", default="")

USE_CLOUDINARY = bool(CLOUDINARY_URL or (CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET))

if USE_CLOUDINARY:
    INSTALLED_APPS += [
        "cloudinary_storage",
        "cloudinary",
    ]
    CLOUDINARY_STORAGE = {
        "CLOUD_NAME": CLOUDINARY_CLOUD_NAME,
        "API_KEY": CLOUDINARY_API_KEY,
        "API_SECRET": CLOUDINARY_API_SECRET,
    }

STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage" if USE_CLOUDINARY else "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

WHITENOISE_USE_FINDERS = True

WHITENOISE_SKIP_COMPRESS_EXTENSIONS = (
    'jpg', 'jpeg', 'png', 'gif', 'webp', 'zip', 'gz', 'tgz', 'bz2', 'tbz', 'xz', 'br', 'mp3', 'mp4', 'm4a', 'ogg', 'wav', 'webm', 'pdf'
)




# Email — Resend SMTP & Emergency Kill-switch
EMAIL_ENABLED = config("EMAIL_ENABLED", default=os.environ.get("EMAIL_ENABLED", "True")).strip().lower() in ("true", "1", "yes")
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = config("EMAIL_HOST", default=os.environ.get("EMAIL_HOST", "smtp.resend.com"))
EMAIL_PORT = int(config("EMAIL_PORT", default=os.environ.get("EMAIL_PORT", "465")))
EMAIL_USE_SSL = config("EMAIL_USE_SSL", default="True" if EMAIL_PORT == 465 else "False").strip().lower() in ("true", "1", "yes")
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default="False" if EMAIL_PORT == 465 else "True").strip().lower() in ("true", "1", "yes")

EMAIL_HOST_USER = config("EMAIL_HOST_USER", default=os.environ.get("EMAIL_HOST_USER", "resend"))
RESEND_API_KEY = config("RESEND_API_KEY", default=os.environ.get("RESEND_API_KEY", "")).strip()
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default=RESEND_API_KEY).strip()
EMAIL_TIMEOUT = int(config("EMAIL_TIMEOUT", default=os.environ.get("EMAIL_TIMEOUT", "15")))  # Timeout after 15 seconds to prevent server worker hangs

DEFAULT_FROM_EMAIL = config(
    "DEFAULT_FROM_EMAIL",
    default=os.environ.get("DEFAULT_FROM_EMAIL", "Python Weekend <hello@pythonweekend.org>")
)

SERVER_EMAIL = DEFAULT_FROM_EMAIL

# Public site domain for absolute links in emails (e.g. unsubscribe link)
SITE_URL = config("SITE_URL", default=os.environ.get("SITE_URL", "https://pythonweekend.org")).rstrip("/")

# Optional internal staff notification inbox for contact form submissions
CONTACT_NOTIFICATION_EMAIL = config("CONTACT_NOTIFICATION_EMAIL", default=os.environ.get("CONTACT_NOTIFICATION_EMAIL", "")).strip()

# Console logging so unhandled 500 errors print their full traceback to Render logs
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{levelname}] {asctime} {name}: {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": True,
        },
    },
}

