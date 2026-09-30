from rest_framework import serializers
from .models import User, Address, Region, City, DeliveryZone


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['id', 'name']


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'region', 'name', 'delivery_zone_id']


class DeliveryZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryZone
        fields = ['id', 'name', 'base_cost', 'per_kg']


from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Address


User = get_user_model()


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            "id",
            "company_name",
            "region",
            "city",
            "street",
            "house",
            "phone",
            "is_default",
        ]
        read_only_fields = [
            "id",
        ]

    def validate_phone(self, value):
        if not value:
            return value

        if not value.startswith("+") and not value.isdigit():
            raise serializers.ValidationError(
                "Enter a valid phone number."
            )

        return value


class UserProfileSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = User

        # Do not include username because your login is email-based.
        fields = [
            "id",
            "email",
            "phone",
            "full_name",
            "region",
            "is_active",
            "addresses",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "email",
            "is_active",
            "addresses",
            "created_at",
        ]
