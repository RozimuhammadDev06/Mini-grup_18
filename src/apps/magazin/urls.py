from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    BrandViewSet,
    CartItemViewSet,
    CartViewSet,
    CategoryViewSet,
    NewsViewSet,
    OrderViewSet,
    ProductViewSet,
    PromotionViewSet,
    ReviewViewSet,
)



router = DefaultRouter()

router.register(
    r"categories",
    CategoryViewSet,
    basename="category",
)
router.register(
    r"brands",
    BrandViewSet,
    basename="brand",
)
router.register(
    r"products",
    ProductViewSet,
    basename="product",
)
router.register(
    r"promotions",
    PromotionViewSet,
    basename="promotion",
)
router.register(
    r"carts",
    CartViewSet,
    basename="cart",
)
router.register(
    r"cart-items",
    CartItemViewSet,
    basename="cart-item",
)
router.register(
    r"orders",
    OrderViewSet,
    basename="order",
)
router.register(
    r"news",
    NewsViewSet,
    basename="news",
)
router.register(
    r"reviews",
    ReviewViewSet,
    basename="review",
)



urlpatterns = [
    path(
        "",
        include(router.urls),
    ),
]
