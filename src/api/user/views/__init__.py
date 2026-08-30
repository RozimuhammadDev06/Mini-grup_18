"""Top-level exports for api.user.views

This module re-exports view classes defined in submodules so that
`from api.user.views import X` works consistently (needed by urls).
"""

# User / auth views
from .users import (
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

__all__ = [
	# users
	"RegisterView",
	"VerifyCodeView",
	"ResendCodeView",
	"CustomTokenObtainPairView",
	"LogoutView",
	"RequestPasswordResetView",
	"ConfirmPasswordResetView",
	"UserProfileView",
	"ChangePasswordView",
	"AddressViewSet",
]
