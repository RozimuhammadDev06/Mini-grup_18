"""
Products / News / Reviews uchun DRF sozlamalari — view'larning o'zida aniq beriladi.

Sabab: config/settings/base.py da `from rest_framework import ...` bor. Bu import
DRF sozlamalarini Django settings tugamasdan o'qitib yuboradi va REST_FRAMEWORK
bloki butunlay e'tiborsiz qoladi (JWT, sahifalash, page_size ishlamaydi).
Global tuzatish boshqa API'larga ta'sir qilgani uchun bu yerda faqat shu
uchta API uchun aniq belgilandi. Global muammo tuzatilgach ham bular to'g'ri ishlaydi.
"""

from rest_framework.permissions import SAFE_METHODS
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken

from api.pagination import CustomPagination


class CatalogPagination(CustomPagination):
    """{count, pages, results}; ?page=2&page_size=24"""

    page_size = 12
    max_page_size = 100


class OptionalJWTAuthentication(JWTAuthentication):
    """
    GET so'rovlarida eskirgan / yaroqsiz token xato bermaydi — foydalanuvchi
    mehmon sifatida ko'riladi (katalog ochilaveradi). Yozish so'rovlarida
    odatdagidek 401 qaytadi.
    """

    def authenticate(self, request):
        try:
            return super().authenticate(request)
        except (InvalidToken, AuthenticationFailed):
            if request.method in SAFE_METHODS:
                return None
            raise


AUTHENTICATION_CLASSES = [OptionalJWTAuthentication]


# drf-spectacular OpenAPI extension for the OptionalJWTAuthentication
# so spectacular can include a bearerAuth security scheme when this
# authenticator is used on views.
from drf_spectacular.extensions import OpenApiAuthenticationExtension


# The OptionalJWTAuthentication extension was removed because schema
# validation produced an incompatible security object with the
# project's OpenAPI JSON Schema. If you want to include a security
# definition for OptionalJWTAuthentication, add a custom
# OpenApiAuthenticationExtension implementation that returns a
# JSON-Schema-compliant object.

__all__ = ["CatalogPagination", "OptionalJWTAuthentication"]
