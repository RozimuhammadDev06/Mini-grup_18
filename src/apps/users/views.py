from rest_framework import viewsets, permissions
from .models import User, Address, Region, City, DeliveryZone
from .serializers import UserProfileSerializer, AddressSerializer, RegionSerializer, CitySerializer, DeliveryZoneSerializer

class RegionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer

class CityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    filterset_fields = ['region']

class DeliveryZoneViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DeliveryZone.objects.all()
    serializer_class = DeliveryZoneSerializer

from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserProfileSerializer


class MyProfileView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get(self, request):
        serializer = UserProfileSerializer(
            request.user,
            context={
                "request": request,
            },
        )

        return Response(serializer.data)
from rest_framework import permissions, viewsets

from apps.users.models import Address
from apps.users.serializers import AddressSerializer



class AddressViewSet(viewsets.ModelViewSet):
    """
    CRUD for the authenticated user's delivery addresses.
    """

    serializer_class = AddressSerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    # Explicitly use drf-spectacular for this ViewSet.
    schema = AutoSchema()

    def get_queryset(self):
        # drf-spectacular may inspect the view without a real user.
        if getattr(self, "swagger_fake_view", False):
            return Address.objects.none()

        if not self.request.user.is_authenticated:
            return Address.objects.none()

        return Address.objects.filter(
            user=self.request.user,
        )

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
        )

