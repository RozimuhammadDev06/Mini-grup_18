from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from api.payments.views import (
    CardPaymentView,
    CardRequestView,
    CardVerifyView,
    PayInitView,
)

urlpatterns = [
    path(
        "",
        RedirectView.as_view(url="/api/docs/", permanent=False),
        name="home",
    ),
    path(
        "admin/",
        admin.site.urls,
    ),

    # Authentication and users
    path(
        "api/auth/",
        include("api.user.urls"),
    ),

    # Main catalog and commerce API
    path(
        "api/",
        include("apps.magazin.urls"),
    ),

    path(
        "api/payments/",
        include("api.payments.urls"),
    ),
    path(
        "api/v2/pay/init",
        PayInitView.as_view(),
        name="fintech-pay-init",
    ),
    path(
        "api/v2/merchant/card_token/request",
        CardRequestView.as_view(),
        name="fintech-card-token-request",
    ),
    path(
        "api/v2/merchant/card_token/verify",
        CardVerifyView.as_view(),
        name="fintech-card-token-verify",
    ),
    path(
        "api/v2/merchant/card_token/payment",
        CardPaymentView.as_view(),
        name="fintech-card-token-payment",
    ),

    path(
        "api/",
        include("apps.store_reviews.urls"),
    ),

    # Versioned API, if your frontend uses /api/v1/
    path(
        "api/v1/",
        include("apps.magazin.urls"),
    ),

    path(
        "api/v1/",
        include("apps.store_reviews.urls"),
    ),

    # OpenAPI schema
    path(
        "api/schema/",
        SpectacularAPIView.as_view(),
        name="schema",
    ),

    # Swagger UI
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(
            url_name="schema",
        ),
        name="swagger-ui",
    ),

    # ReDoc
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(
            url_name="schema",
        ),
        name="redoc",
    ),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )

    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT,
    )
