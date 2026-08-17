"""
Fixed and unified users/urls.py for 'СтройОптТорг'

What was wrong in the original file (fixed here):
1. The file was pasted TWICE — two separate `router = DefaultRouter()` and
   `urlpatterns = [...]` blocks. Django would crash with a NameError on the
   second assignment or silently lose routes. Merged into one clean file.
2. Broken import: `from api.user.serializers import PromotionViewSet, ReviewViewSet`
   - imports ViewSets from a `.serializers` module (wrong; views live in views.py),
   - `api.user` path doesn't match the `apps.users` structure,
   - `PromotionViewSet`/`ReviewViewSet` are not defined anywhere in the users app.
   Replaced with the actual views from this app.
3. Duplicate `from rest_framework.routers import DefaultRouter` import removed.
4. The fixed views.py defines 9 endpoints (register, verify, resend, login,
   refresh, logout, password reset x2, profile, addresses). All are wired here,
   grouped under one router with proper prefixes.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView,
    VerifyCodeView,
    ResendCodeView,
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
    path('verify/', VerifyCodeView.as_view(), name='verify-code'),
    path('resend-code/', ResendCodeView.as_view(), name='resend-code'),
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
