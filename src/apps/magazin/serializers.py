from rest_framework import serializers
from django.utils import timezone
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes

from .models import (
    Product,
    ProductImage,
    ProductType,
    Promotion,
    Brand,
    Category,
    Cart,
    CartItem,
    Order,
    News,
    Review,
)


def absolute_url(serializer, file_field):
    """Rasm uchun to'liq manzil (https://.../media/...)"""
    if not file_field:
        return None
    request = serializer.context.get("request")
    url = file_field.url
    return request.build_absolute_uri(url) if request else url


class ProductTypeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = ["id", "name", "slug"]


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

    product_type = ProductTypeShortSerializer(
        read_only=True,
    )
    product_type_id = serializers.PrimaryKeyRelatedField(
        source="product_type",
        queryset=ProductType.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )

    attributes = serializers.JSONField(
        source="attrs_json",
        required=False,
    )
    in_stock = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    rating_avg = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "brand",
            "brand_id",
            "category",
            "category_id",
            "product_type",
            "product_type_id",
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
            "images",
            "attributes",
            "description",
            "is_active",
            "is_hit",
            "rating_avg",
            "reviews_count",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "brand",
            "category",
            "product_type",
            "in_stock",
            "image_url",
            "images",
            "rating_avg",
            "reviews_count",
            "created_at",
        ]

    def get_in_stock(self, obj):
        return obj.stock_quantity > 0


    @extend_schema_field(OpenApiTypes.BOOL)
    def get_in_stock(self, obj):
        return obj.stock_quantity > 0

    @extend_schema_field(OpenApiTypes.URI)
    def get_image_url(self, obj):
        return absolute_url(self, obj.image)

    @extend_schema_field(OpenApiTypes.STR)
    def get_images(self, obj):
        """Galereya: to'liq manzillar ro'yxati (asosiy rasm image_url'da)"""
        return [absolute_url(self, item.image) for item in obj.images.all()]

    # rating_avg / reviews_count — ProductViewSet queryset'ida annotate qilinadi
    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_rating_avg(self, obj):
        value = getattr(obj, "rating_avg", None)
        return round(value, 1) if value is not None else None

    @extend_schema_field(OpenApiTypes.INT)
    def get_reviews_count(self, obj):
        return getattr(obj, "reviews_count", 0) or 0

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

    @extend_schema_field(OpenApiTypes.URI)
    def get_image_url(self, obj):
        return absolute_url(self, obj.image)


    @extend_schema_field(OpenApiTypes.STR)
    def get_user_name(self, obj):
        user = obj.user
        return (
            user.full_name
            or user.get_full_name()
            or user.username
            or "Покупатель"
        )



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


class NewsProductSerializer(serializers.ModelSerializer):
    """Yangilik ichidagi mahsulot — qisqa ko'rinish"""

    class Meta:
        model = Product
        fields = ["id", "name", "slug", "price"]


class NewsSerializer(serializers.ModelSerializer):
    rubric_label = serializers.CharField(source="get_rubric_display", read_only=True)
    image_url = serializers.SerializerMethodField()
    product = NewsProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        source="product",
        queryset=Product.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = News
        fields = [
            "id",
            "title",
            "slug",
            "rubric",
            "rubric_label",
            "excerpt",
            "content",
            "image",
            "image_url",
            "product",
            "product_id",
            "is_published",
            "published_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "rubric_label", "image_url", "product", "created_at", "updated_at"]
        extra_kwargs = {
            "title": {"required": True, "allow_blank": False},
            "slug": {"required": False},
        }

    def get_image_url(self, obj):
        return absolute_url(self, obj.image)


class ReviewSerializer(serializers.ModelSerializer):
    # Email ochiq ro'yxatda ko'rsatilmaydi — faqat ism
    user_name = serializers.SerializerMethodField()
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "product",
            "product_name",
            "user",
            "user_name",
            "rating",
            "text",
            "is_approved",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "user_name",
            "product_name",
            "is_approved",
            "created_at",
            "updated_at",
        ]

    def get_user_name(self, obj):
        user = obj.user
        return (
            user.full_name
            or user.get_full_name()
            or user.username
            or "Покупатель"
        )

    def validate(self, attrs):
        # Bitta foydalanuvchi bitta mahsulotga bitta sharh (DB constraint'dan oldin aniq xabar)
        request = self.context.get("request")
        product = attrs.get("product")
        if self.instance is None and request and product:
            if Review.objects.filter(product=product, user=request.user).exists():
                raise serializers.ValidationError(
                    {"product": "Вы уже оставили отзыв на этот товар."}
                )
        return attrs

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

