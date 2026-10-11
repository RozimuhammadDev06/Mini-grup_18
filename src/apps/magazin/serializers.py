from rest_framework import serializers
from django.utils import timezone

from .models import Product, Promotion, Brand, Category, Cart, CartItem, Order, News, Review

class BrandShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = [
            "id",
            "name",
            "slug",
        ]


class CategoryShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
        ]


class ProductSerializer(serializers.ModelSerializer):
    # Response'da object ko'rinadi
    brand = BrandShortSerializer(
        read_only=True,
    )
    category = CategoryShortSerializer(
        read_only=True,
    )

    # Request'da ID yuboriladi
    brand_id = serializers.PrimaryKeyRelatedField(
        source="brand",
        queryset=Brand.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )
    category_id = serializers.PrimaryKeyRelatedField(
        source="category",
        queryset=Category.objects.all(),
        write_only=True,
    )

    attributes = serializers.JSONField(
        source="attrs_json",
        required=False,
    )
    in_stock = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "brand",
            "brand_id",
            "category",
            "category_id",
            "name",
            "slug",
            "article",
            "material",
            "color",
            "length_mm",
            "width_mm",
            "height_mm",
            "weight_kg",
            "price",
            "old_price",
            "stock_quantity",
            "in_stock",
            "image",
            "image_url",
            "attributes",
            "description",
            "is_active",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "brand",
            "category",
            "in_stock",
            "image_url",
            "created_at",
        ]

    def get_in_stock(self, obj):
        return obj.stock_quantity > 0

    def get_image_url(self, obj):
        if not obj.image:
            return None

        request = self.context.get("request")

        if request:
            return request.build_absolute_uri(
                obj.image.url,
            )

        return obj.image.url

    def validate(self, attrs):
        price = attrs.get(
            "price",
            getattr(self.instance, "price", None),
        )
        old_price = attrs.get(
            "old_price",
            getattr(self.instance, "old_price", None),
        )

        if (
            price is not None
            and old_price is not None
            and old_price < price
        ):
            raise serializers.ValidationError(
                {
                    "old_price": (
                        "old_price must be greater than or "
                        "equal to price."
                    )
                }
            )

        return attrs


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

