import os
from datetime import timedelta

from .base import *


# ============================================================
# Development sozlamalari
# ============================================================

DEBUG = True


ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "fixingtools.pythonanywhere.com",
]


CSRF_TRUSTED_ORIGINS = [
    "https://fixingtools.pythonanywhere.com",
]


# ============================================================
# Static va media fayllar
# ============================================================

STATIC_URL = "/static/"

STATIC_ROOT = os.path.join(
    BASE_DIR,
    "staticfiles",
 )

STATICFILES_DIRS = [
    os.path.join(
        BASE_DIR,
        "static",
    ),
]

MEDIA_URL = "/media/"

MEDIA_ROOT = os.path.join(
    BASE_DIR,
    "media",
)


# ============================================================
# Simple JWT
# ============================================================

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=21),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),

    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,

    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,

    "AUDIENCE": None,
    "ISSUER": None,

    "AUTH_HEADER_TYPES": ("Bearer",),

    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",

    "AUTH_TOKEN_CLASSES": (
        "rest_framework_simplejwt.tokens.AccessToken",
    ),

    "TOKEN_TYPE_CLAIM": "token_type",
    "JTI_CLAIM": "jti",

    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),
}


# ============================================================
# CORS
# ============================================================

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://fixingtools.pythonanywhere.com",
]
