"""
Django settings for musicae_web project.

Safe for local dev and production:
- Reads secrets & hosts from environment variables
- Enables strong HTTPS settings only when DEBUG=0
- Keeps your existing apps and CKEditor/CAPTCHA config
"""

import os
from .cap_funcs import add_sub_challange

# ────────────────────────────────────────────────────────────────────────────────
# Environment helpers
# Provide these env vars in prod at minimum:
# DJANGO_KEY, DJANGO_DEBUG, DJANGO_HOST, DJANGO_DB_NAME, DJANGO_DB_USER,
# DJANGO_DB_PASS, DJANGO_DB_HOST, DJANGO_DB_PORT, (optional) DJANGO_CSRF_TRUSTED_ORIGINS
# Email (optional): DJANGO_EMAIL_HOST, DJANGO_EMAIL_USER, DJANGO_EMAIL_PASS,
#                   DJANGO_EMAIL_FROM, DJANGO_EMAIL_CONTACTS
# ────────────────────────────────────────────────────────────────────────────────

def env_list(name: str, default: str = ""):
    # space-separated list
    return [x for x in os.environ.get(name, default).split() if x]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Core settings
SECRET_KEY = os.environ.get("DJANGO_KEY", "^dev-only-unsafe-key^")
DEBUG = False
# space-separated list → list
def env_list(name: str, default: str = ""):
    return [x for x in os.environ.get(name, default).split() if x]

ALLOWED_HOSTS = ['fundamentamusicae.bg', 'www.fundamentamusicae.bg', '3.121.16.126', '127.0.0.1']



# Application definition
INSTALLED_APPS = [
    "musicae_base.apps.MusicaeBaseConfig",
    "musicae_content",
    "modeltranslation",
    "captcha",
    "django_user_agents",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    "django_cleanup.apps.CleanupConfig",
    "ckeditor",
    "ckeditor_uploader",
]

SITE_ID = 1

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_user_agents.middleware.UserAgentMiddleware",
]

ROOT_URLCONF = "musicae_web.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.i18n",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.media",
                "musicae_base.context_processors.header_processor",
                "musicae_base.context_processors.research_pages_processor",
                "musicae_base.context_processors.about_pages_processor",
            ],
        },
    },
]

WSGI_APPLICATION = "musicae_web.wsgi.application"

# Database (MySQL) — all fields env-driven with sensible dev defaults
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get("DJANGO_DB_NAME", "musicae_db"),
        "USER": os.environ.get("DJANGO_DB_USER", "kakehavata"),
        "PASSWORD": os.environ.get("DJANGO_DB_PASS", "TheHobbit123!"),
        "HOST": os.environ.get("DJANGO_DB_HOST", "127.0.0.1"),
        "PORT": os.environ.get("DJANGO_DB_PORT", "3306"),
        "OPTIONS": {"init_command": "SET sql_mode='STRICT_TRANS_TABLES'"},
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = "bg"
TIME_ZONE = os.environ.get("DJANGO_TIME_ZONE", "Europe/Kiev")  # or "Europe/Kyiv"
USE_I18N = True
USE_L10N = True  # ignored on newer Django; harmless
USE_TZ = True

def gettext(s): return s

LANGUAGES = (
    ("bg", gettext("Bulgarian")),
    ("en", gettext("English")),
    ("de", gettext("German")),
)

APPEND_SLASH = True
LOCALE_PATHS = [os.path.join(BASE_DIR, "locale")]

# Static & Media
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Email (SMTP in prod, console in dev)
if "DJANGO_EMAIL_HOST" in os.environ:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.environ["DJANGO_EMAIL_HOST"]
    EMAIL_PORT = 587
    EMAIL_HOST_USER = 'musicae'
    EMAIL_HOST_PASSWORD = os.environ["DJANGO_EMAIL_PASS"]
    EMAIL_USE_TLS = True

    DEFAULT_FROM_EMAIL = os.environ["DJANGO_EMAIL_FROM"]
    CONTACT_EMAILS = os.environ["DJANGO_EMAIL_CONTACTS"].split()

else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    DEFAULT_FROM_EMAIL = 'testing@example.com'
    EMAIL_HOST_USER = ''
    EMAIL_HOST_PASSWORD = ''
    EMAIL_USE_TLS = False
    EMAIL_PORT = 1025

    CONTACT_EMAILS = ["test_mail@example.com"]

# CAPTCHA (kept from your version)
challenge = add_sub_challange()
CAPTCHA_CHALLENGE_FUNCT = challenge
CAPTCHA_LETTER_ROTATION = 0
CAPTCHA_NOISE_FUNCTIONS = []

# CKEditor
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_CONFIGS = {
    "default": {
        "height": 300,
        "width": "auto",
        "toolbar": "Custom",
        "toolbar_Custom": [
            ["Bold", "Italic", "Underline", "RemoveFormat"],
            ["Link", "Unlink"],
            ["BulletedList", "NumberedList", "Blockquote"],
            ["JustifyLeft", "JustifyCentre", "JustifyRight"],
            ["Format", "Styles"],
            ["Image", "Table"],
            ["Source"],
        ],
        # point to a built CSS you control
        "contentsCss": [STATIC_URL + "musicae_base/main.css"],
        "extraAllowedContent": "*(*){*};a[*];img[*];figure;figcaption",
    }
}


# Auto fieldasdasdasd
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# ────────────────────────────────────────────────────────────────────────────────
# Production-only security (enabled when DEBUG=0)
# ────────────────────────────────────────────────────────────────────────────────
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # Strong HTTPS headers
    SECURE_HSTS_SECONDS = int(os.environ.get("DJANGO_HSTS_SECONDS", "31536000"))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # Django 4+ expects full scheme (https://example.com). If you're on Django 3,
    # hostnames also work. Provide space-separated values in DJANGO_CSRF_TRUSTED_ORIGINS.
    CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS", "")

    # Extra hardening
    SESSION_COOKIE_SAMESITE = "Lax"
    X_FRAME_OPTIONS = "DENY"
