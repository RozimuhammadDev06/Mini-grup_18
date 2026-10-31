from .base import *
from datetime import timedelta

FHP_BASE_URL = env(
    "FHP_BASE_URL",
    default=FINTECHHUB_BASE_URL,
)
FHP_SERVICE_ID = env.int(
    "FHP_SERVICE_ID",
    default=FINTECHHUB_SERVICE_ID,
)
FHP_SERVICE_SECRET_KEY = (
    env("FHP_SERVICE_SECRET_KEY", default="")
    or FINTECHHUB_MERCHANT_SECRET_KEY
)

# INSTALLED_APPS += [
#     third-parties
# ]

ALLOWED_HOSTS = env("ALLOWED_HOSTS").split(",")

MIDDLEWARE += ['corsheaders.middleware.CorsMiddleware', ]
STATIC_ROOT = os.path.join(BASE_DIR, 'static')


SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=21),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'JTI_CLAIM': 'jti',
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}


CSRF_TRUSTED_ORIGINS = [o.strip() for o in env("CSRF_TRUSTED_ORIGINS").split(",")]
CORS_ALLOWED_ORIGINS = [o.strip() for o in env("CORS_ALLOWED_ORIGINS").split(",")]