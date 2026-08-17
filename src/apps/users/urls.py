from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegionViewSet,
    CityViewSet,
    DeliveryZoneViewSet,
    UserProfileViewSet,
    AddressViewSet,
)

router = DefaultRouter()
router.register(r'regions', RegionViewSet)
router.register(r'cities', CityViewSet)
router.register(r'delivery-zones', DeliveryZoneViewSet)
router.register(r'profile', UserProfileViewSet, basename='user-profile')
router.register(r'addresses', AddressViewSet, basename='user-address')

urlpatterns = [
    path('', include(router.urls)),
]
