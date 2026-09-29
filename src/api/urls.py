from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, BrandViewSet, ProductViewSet,
    CartViewSet, CartItemViewSet, OrderViewSet,NewsViewSet
)
from django.urls import include, path


urlpatterns = [
    path(
        "",
        include("apps.magazin.urls"),
    ),
]

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'brands', BrandViewSet)
router.register(r'products', ProductViewSet)
router.register(r'carts', CartViewSet)
router.register(r'cart-items', CartItemViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'orders', NewsViewSet)

urlpatterns = [
    path('', include(router.urls)),
]