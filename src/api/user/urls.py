from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.user.serializers import PromotionViewSet, ReviewViewSet

router = DefaultRouter()
router.register(r'promotions', PromotionViewSet, basename='promotion')
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),
]