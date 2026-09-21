from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView,
    CustomTokenObtainPairView,
    LogoutView,
    RequestPasswordResetView,
    ConfirmPasswordResetView,
    UserProfileView,
    ChangePasswordView,
    AddressViewSet,
)

router = DefaultRouter()
router.register(r'addresses', AddressViewSet, basename='user-address')

urlpatterns = [
    path('', include(router.urls)),

    # --- Authentication URLs ---
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # --- Password Reset URLs ---
    path('password/reset/request/', RequestPasswordResetView.as_view(), name='password_reset_request'),
    path('password/reset/confirm/', ConfirmPasswordResetView.as_view(), name='password_reset_confirm'),

    # --- Profile URLs ---
    path('profile/', UserProfileView.as_view(), name='user-profile'),

    # --- TASK: USER PROFIL UPDATE PASSWORD (2026-08-22) ---
    path('password/change/', ChangePasswordView.as_view(), name='change-password'),
]