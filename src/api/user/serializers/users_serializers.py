"""
Fixed and unified users/serializers.py for 'СтройОптТорг'

What was wrong in the original file (fixed here):
1. The serializers.py was pasted TWICE in the same file (two separate code
   blocks were combined). This caused `AddressSerializer` to be defined twice
   and raised a NameError when registering.
2. UserProfileSerializer referenced fields that do NOT exist on the new unified
   User model: `username`, `phone`, `full_name`, `region`. The new User model
   uses `email` login, has `first_name`/`last_name` (plus `full_name` property),
   `phone_number`, and has no `region` field. All references fixed.
3. Duplicate `get_user_model()` + local `User` import conflict — simplified.
4. Register / Verify / Reset serializers from the auth tasks are included here
   so the whole authentication flow works together.
"""

from rest_framework import serializers
from apps.users.models import User, Address, Region, City, DeliveryZone


# =============================================================
# Geography serializers
# =============================================================

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


# =============================================================
# Address serializers
# =============================================================

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


# =============================================================
# User profile serializers
# =============================================================

class UserProfileSerializer(serializers.ModelSerializer):
    """Read-only profile info with nested addresses."""
    addresses = AddressSerializer(many=True, read_only=True)
    full_name = serializers.CharField(read_only=True)  # model property

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone_number', 'telegram_id', 'language', 'is_email_verified',
            'is_active', 'addresses', 'created_at'
        ]
        read_only_fields = ['id', 'email', 'created_at']


class UserUpdateSerializer(serializers.ModelSerializer):
    """Allows the user to update their own profile info."""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'telegram_id', 'language']


# =============================================================
# Authentication serializers (Register / Verify / Resend / Reset)
# =============================================================

class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150, required=False, default='')
    phone_number = serializers.CharField(max_length=13, required=False, default='')

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "A user with this email already exists."})
        return attrs

    def validate_password(self, value):
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError("Password must contain at least one number.")
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data.get('last_name', ''),
            phone_number=validated_data.get('phone_number', ''),
            is_active=False,  # activated after email verification
        )
        return user


class VerifyCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)


class ResendCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class RequestPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ConfirmPasswordResetSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=255)
    password = serializers.CharField(min_length=8)

    def validate_password(self, value):
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError("Password must contain at least one number.")
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        return value


# =============================================================
# TASK: USER PROFIL UPDATE PASSWORD (2026-08-22)
# =============================================================

class ChangePasswordSerializer(serializers.Serializer):
    """
    Allows an authenticated user to change their password
    by providing the current password and a new one.
    """
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True, required=True)

    def validate_new_password(self, value):
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError("Password must contain at least one number.")
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError(
                {"new_password_confirm": "New passwords do not match."}
            )
        if attrs['old_password'] == attrs['new_password']:
            raise serializers.ValidationError(
                {"new_password": "New password must be different from the old one."}
            )
        return attrs
