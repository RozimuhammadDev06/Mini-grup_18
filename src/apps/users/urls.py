from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from api.user.views.users import (
    AddressViewSet,
    ChangePasswordView,
    ConfirmPasswordResetView,
    CustomTokenObtainPairView,
    LogoutView,
    RegisterView,
    RequestPasswordResetView,
    UserProfileView,
)


router = DefaultRouter()

router.register(
    r"addresses",
    AddressViewSet,
    basename="user-address",
)


urlpatterns = [
    # ViewSet routes:
    # /addresses/
    # /addresses/<id>/
    path(
        "",
        include(router.urls),
    ),

    # Authentication
    path(
        "register/",
        RegisterView.as_view(),
        name="register",
    ),
    path(
        "login/",
        CustomTokenObtainPairView.as_view(),
        name="token-obtain-pair",
    ),
    path(
        "token/refresh/",
        TokenRefreshView.as_view(),
        name="token-refresh",
    ),
    path(
        "logout/",
        LogoutView.as_view(),
        name="logout",
    ),

    # Password reset
    path(
        "password/reset/request/",
        RequestPasswordResetView.as_view(),
        name="password-reset-request",
    ),
    path(
        "password/reset/confirm/",
        ConfirmPasswordResetView.as_view(),
        name="password-reset-confirm",
    ),
    path(
        "password/change/",
        ChangePasswordView.as_view(),
        name="password-change",
    ),

    # Current authenticated user profile
    path(
        "profile/",
        UserProfileView.as_view(),
        name="user-profile",
    ),
]
