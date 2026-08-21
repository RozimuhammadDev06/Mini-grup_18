from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    ProductViewSet,
    CompareViewSet,
)

from .home_views import HomePageView


router = DefaultRouter()

router.register(
    r"categories",
    CategoryViewSet,
    basename="category",
)

router.register(
    r"products",
    ProductViewSet,
    basename="product",
)

router.register(
    r"compare",
    CompareViewSet,
    basename="compare",
)


urlpatterns = [
    path("", include(router.urls)),

    path(
        "home/",
        HomePageView.as_view(),
        name="home-page",
    ),
]