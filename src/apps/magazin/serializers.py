from rest_framework import serializers
from django.utils import timezone

from .models import Product, Promotion, Brand, Category


class ProductSerializer(serializers.ModelSerializer):
    brand = serializers.StringRelatedField(read_only=True)
    category = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Product
        fields = "__all__"


class PromotionSerializer(serializers.ModelSerializer):
    """Serializer for `Promotion` model.

    The `Promotion` model currently defines: title, description,
    discount_value, start_date, end_date, is_active.
    """
    is_current = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Promotion
        fields = [
            "id",
            "title",
            "description",
            "discount_value",
            "start_date",
            "end_date",
            "is_active",
            "is_current",
        ]
        read_only_fields = ["id", "is_current"]

    def get_is_current(self, obj):
        now = timezone.now()
        return obj.start_date <= now <= obj.end_date

