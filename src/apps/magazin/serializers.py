from rest_framework import serializers
from django.utils import timezone

from .models import Product, Promotion, Brand, Category, Cart, CartItem, Order, News, Review

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



class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "product", "quantity", "price"]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "user", "session_key", "promo_code_id", "updated_at", "items"]
        read_only_fields = ["id", "user", "updated_at"]


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"


class NewsSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = News
        fields = "__all__"


class ReviewSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "product",
            "product_name",
            "user",
            "user_email",
            "rating",
            "text",
            "is_approved",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "user_email",
            "product_name",
            "is_approved",
            "created_at",
            "updated_at",
        ]

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

