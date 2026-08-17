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

# Catalog views
from .catalog import (
	CategoryViewSet,
	ProductViewSet,
	CompareViewSet,
)

# Content views
from .content import (
	ArticleViewSet,
	PromotionViewSet,
	BannerViewSet,
	FAQViewSet,
	StaticPageViewSet,
)

# Engagement views (avoid importing CompareViewSet to prevent name clash)
from .engagement import (
	ReviewViewSet,
	WishlistViewSet,
	LeadViewSet,
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
	# catalog
	"CategoryViewSet",
	"ProductViewSet",
	"CompareViewSet",
	# content
	"ArticleViewSet",
	"PromotionViewSet",
	"BannerViewSet",
	"FAQViewSet",
	"StaticPageViewSet",
	# engagement
	"ReviewViewSet",
	"WishlistViewSet",
	"LeadViewSet",
]
