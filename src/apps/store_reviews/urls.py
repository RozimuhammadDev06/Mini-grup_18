from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import StoreReviewViewSet

# SimpleRouter: magazin routeri bilan ikkinchi "api-root" sahifasi yaratilmaydi
router = SimpleRouter()
router.register(r"store-reviews", StoreReviewViewSet, basename="store-review")

urlpatterns = [
    path("", include(router.urls)),
]
