from rest_framework import serializers

from apps.engagement.models import (
    Review,
    Wishlist,
    Compare,
    Lead,
)

from ..serializers.catalog_serializers import ProductListSerializer


# =============================================================
# REVIEW SERIALIZER
# =============================================================

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            "id",
            "user",
            "product",
            "author_name",
            "rating",
            "comment",
            "is_published",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "created_at",
        ]


# =============================================================
# WISHLIST SERIALIZER
# =============================================================

class WishlistSerializer(serializers.ModelSerializer):
    product_details = ProductListSerializer(
        source="product",
        read_only=True,
    )

    class Meta:
        model = Wishlist
        fields = [
            "id",
            "product",
            "product_details",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
        ]


# =============================================================
# COMPARE SERIALIZER
# =============================================================

class CompareSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compare
        fields = [
            "id",
            "user",
            "product",
            "session_key",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "created_at",
        ]


# =============================================================
# LEAD SERIALIZER
# =============================================================

class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = [
            "id",
            "name",
            "email",
            "phone",
            "message",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]