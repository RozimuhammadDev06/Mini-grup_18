from rest_framework import serializers

from apps.users.models import (
    Address,
    City,
    DeliveryZone,
    Region,
    User,
)

  

# =============================================================
# Geography serializers
# =============================================================

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ("id", "name")


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ("id", "name", "region", "delivery_zone")


class DeliveryZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryZone
        fields = ("id", "name", "base_cost", "per_kg")


# =============================================================
# Address serializers
# =============================================================

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = (
            "id",
            "company_name",
            "region",
            "city",
            "street",
            "house",
            "phone",
            "is_default",
        )
        read_only_fields = ("id",)

    def validate_phone(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Phone number cannot be empty."
            )

        if not value.startswith("+") or not value[1:].isdigit():
            raise serializers.ValidationError(
                "Enter a valid phone number, for example +998901234567."
            )

        return value


# =============================================================
# User profile serializers
# =============================================================

class UserProfileSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "phone",
            "is_active",
            "created_at",
            "addresses",
        )
        read_only_fields = (
            "id",
            "email",
            "is_active",
            "created_at",
            "addresses",
        )


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "full_name",
            "phone",
        )


# =============================================================
# Authentication serializers
# =============================================================

class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        min_length=8,
    )
    password_confirm = serializers.CharField(
        write_only=True,
    )
    first_name = serializers.CharField(
        max_length=150,
    )
    last_name = serializers.CharField(
        max_length=150,
        required=False,
        allow_blank=True,
        default="",
    )
    phone_number = serializers.CharField(
        source="phone",
        max_length=20,
        required=False,
        allow_blank=True,
        default="",
    )

    def validate_email(self, value):
        email = value.strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError(
                "A user with this email already exists."
            )

        return email

    def validate_phone(self, value):
        value = value.strip()

        if value and (
            not value.startswith("+")
            or not value[1:].isdigit()
        ):
            raise serializers.ValidationError(
                "Enter a valid phone number, for example +998901234567."
            )

        return value

    def validate_password(self, value):
        if not any(character.isdigit() for character in value):
            raise serializers.ValidationError(
                "Password must contain at least one number."
            )

        if not any(character.isupper() for character in value):
            raise serializers.ValidationError(
                "Password must contain at least one uppercase letter."
            )

        return value

    def validate(self, attrs):
        password_confirm = attrs.pop("password_confirm")

        if attrs["password"] != password_confirm:
            raise serializers.ValidationError(
                {
                    "password_confirm": (
                        "Passwords do not match."
                    )
                }
            )

        return attrs

    def create(self, validated_data):
        email = validated_data["email"]

        return User.objects.create_user(
            username=email,
            email=email,
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            full_name=(
                f"{validated_data.get('first_name', '')} "
                f"{validated_data.get('last_name', '')}"
            ).strip(),
            phone=validated_data.get("phone", ""),
            is_active=True,
        )


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
    )


class RequestPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ConfirmPasswordResetSerializer(serializers.Serializer):
    token = serializers.CharField(
        max_length=255,
    )
    password = serializers.CharField(
        write_only=True,
        min_length=8,
    )
    password_confirm = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    def validate_password(self, value):
        if not any(character.isdigit() for character in value):
            raise serializers.ValidationError(
                "Password must contain at least one number."
            )

        if not any(character.isupper() for character in value):
            raise serializers.ValidationError(
                "Password must contain at least one uppercase letter."
            )

        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {
                    "password_confirm": (
                        "Passwords do not match."
                    )
                }
            )

        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        write_only=True,
    )
    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
    )
    new_password_confirm = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    def validate_new_password(self, value):
        if not any(character.isdigit() for character in value):
            raise serializers.ValidationError(
                "Password must contain at least one number."
            )

        if not any(character.isupper() for character in value):
            raise serializers.ValidationError(
                "Password must contain at least one uppercase letter."
            )

        return value

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError(
                {
                    "new_password_confirm": (
                        "New passwords do not match."
                    )
                }
            )

        if attrs["old_password"] == attrs["new_password"]:
            raise serializers.ValidationError(
                {
                    "new_password": (
                        "New password must be different "
                        "from the old password."
                    )
                }
            )

        return attrs