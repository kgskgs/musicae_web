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

ALLOWED_HOSTS = ['fundamentamusicae.bg', 'www.fundamentamusicae.bg', '35.157.187.254', '127.0.0.1', ]

CSRF_TRUSTED_ORIGINS = [
    "https://fundamentamusicae.bg",
    "https://www.fundamentamusicae.bg",
]

# Nginx terminates SSL → Django must trust forwarded headers
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Use Nginx's Host header so redirects and security checks work
USE_X_FORWARDED_HOST = True

# Force HTTPS
SECURE_SSL_REDIRECT = True

# Production cookie security
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Strong HSTS
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True