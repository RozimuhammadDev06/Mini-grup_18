from rest_framework import serializers
from apps.users.models import User, Address, Region, City, DeliveryZone

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['id', 'name']

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name', 'region', 'delivery_zone_id']

class DeliveryZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryZone
        fields = ['id', 'name', 'base_cost', 'per_kg']

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'company_name', 'region', 'city', 'street', 'house', 'phone', 'is_default']
        read_only_fields = ['id']

class UserProfileSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'full_name', 'region', 'is_active', 'addresses', 'created_at']
        read_only_fields = ['id', 'created_at', 'username']



from rest_framework import serializers
from .models import Address

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            'id', 'company_name', 'region', 'city', 
            'street', 'house', 'phone', 'is_default'
        ]
        read_only_fields = ['id']

    def validate_phone(self, value):
        # Basic phone validation logic
        if not value.startswith('+') and not value.isdigit():
            raise serializers.ValidationError("Enter a valid phone number.")
        return value
