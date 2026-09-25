import os

import environ


# ============================================================
# Asosiy sozlamalar
# ============================================================

env = environ.Env()

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

# .env fayli loyiha asosiy papkasida bo‘lishi kerak:
# /home/FixingTools/Mini-grup_18/.env
environ.Env.read_env(
    os.path.join(BASE_DIR, ".env")
)


# ============================================================
# Xavfsizlik
# ============================================================

SECRET_KEY = env(
    "SECRET_KEY",
    default="django-insecure-development-key-change-in-production",
)

DEBUG = env.bool(
    "DEBUG",
    default=False,
)

BASE_URL = env(
    "BASE_URL",
    default="http://127.0.0.1:8000",
 )

ALLOWED_HOSTS = env.list(
    "ALLOWED_HOSTS",
    default=[
        "127.0.0.1",
        "localhost",
    ],
)


# ============================================================
# Django ilovalari
# ============================================================

INSTALLED_APPS = [
    "jazzmin",

    # Django ilovalari
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party ilovalar
    "corsheaders",
    "rest_framework",
    "django_filters",
    "drf_spectacular",

    # Loyiha ilovalari
    "apps.users",
    "apps.magazin",
]


# ============================================================
# Middleware
# ============================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "config.urls"


# ============================================================
# Template sozlamalari
# ============================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "templates"),
        ],
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


WSGI_APPLICATION = "config.wsgi.application"


# ============================================================
# Parol tekshiruvi
# ============================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]


# ============================================================
# Til va vaqt
# ============================================================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Tashkent"

USE_I18N = True

USE_TZ = False


# ============================================================
# Static va media fayllar
# ============================================================

# Brauzer ko‘radigan URL
STATIC_URL = "/static/"

# collectstatic fayllarni shu papkaga yig‘adi
# PythonAnywhere uchun:
# /home/FixingTools/Mini-grup_18/staticfiles/
STATIC_ROOT = os.path.join(
    BASE_DIR,
    "staticfiles",
)

# Siz yaratadigan static fayllar uchun papka
STATICFILES_DIRS = [
    os.path.join(
        BASE_DIR,
        "static",
    ),
]

# User yuklaydigan fayllar: rasmlar, hujjatlar va hokazo
MEDIA_URL = "/media/"

MEDIA_ROOT = os.path.join(
    BASE_DIR,
    "media",
)


# ============================================================
# Django REST Framework
# ============================================================

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],

    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],

    "DEFAULT_PAGINATION_CLASS": (
        "api.pagination.CustomPagination"
    ),

    "PAGE_SIZE": 10,

    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],

    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.ScopedRateThrottle",
    ],

    "DEFAULT_THROTTLE_RATES": {
        "login": "5/day",
    },

    "DEFAULT_SCHEMA_CLASS": (
        "drf_spectacular.openapi.AutoSchema"
    ),
}


# ============================================================
# Swagger / OpenAPI
# ============================================================

SPECTACULAR_SETTINGS = {
    "TITLE": "СтройОптТорг API",
    "DESCRIPTION": (
        "Wholesale/Retail Construction Materials "
        "E-commerce Platform API"
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_PATCH": True,
    "COMPONENT_NO_READ_ONLY_REQUIRED": True,
    "SCHEMA_PATH_PREFIX": r"/api/",
}


# ============================================================
# Database
# ============================================================

DB_TYPE = env(
    "DB_TYPE",
    default="sqlite",
)

if DB_TYPE == "psql":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "CONN_MAX_AGE": 60,
            "NAME": env("DB_NAME"),
            "USER": env("DB_USER"),
            "PASSWORD": env("DB_PASSWORD"),
            "HOST": env("DB_HOST"),
            "PORT": env("DB_PORT", default="5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(
                BASE_DIR,
                "db.sqlite3",
            ),
        }
    }


# ============================================================
# Custom User modeli
# ============================================================

AUTH_USER_MODEL = "users.User"


# ============================================================
# Primary key
# ============================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ============================================================
# Email
# ============================================================

EMAIL_BACKEND = (
    "django.core.mail.backends.smtp.EmailBackend"
)

EMAIL_HOST = "smtp.gmail.com"

EMAIL_PORT = 587

EMAIL_USE_TLS = True

EMAIL_HOST_USER = env(
    "EMAIL_HOST",
    default="",
)

EMAIL_HOST_PASSWORD = env(
    "EMAIL_PASSWORD",
    default="",
)


# ============================================================
# Loyiha URL sozlamalari
# ============================================================

BASE_URL_LINK = env(
    "BASE_URL_LINK",
    default=BASE_URL,
)


# ============================================================
# CORS
# ============================================================

CORS_ALLOW_ALL_ORIGINS = env.bool(
    "CORS_ALLOW_ALL_ORIGINS",
    default=True,
)


# ============================================================
# Celery
# ============================================================

CELERY_BROKER_URL = env(
    "CELERY_BROKER_URL",
    default="redis://localhost:6379/0",
)

CELERY_RESULT_BACKEND = env(
    "CELERY_RESULT_BACKEND",
    default="redis://localhost:6379/0",
)

CELERY_ACCEPT_CONTENT = [
    "application/json",
]

CELERY_TASK_SERIALIZER = "json"

CELERY_RESULT_SERIALIZER = "json"

CELERY_IGNORE_RESULT = False

CELERY_TASK_SOFT_TIME_LIMIT = 60
