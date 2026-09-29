from rest_framework import serializers

from .models import Product, Brand, Category
from rest_framework import serializers

from rest_framework import serializers

from .models import Product, Promotion


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class PromotionSerializer(serializers.ModelSerializer):
    products = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Product.objects.all(),
        required=False,
    )

    is_current = serializers.BooleanField(
        read_only=True,
    )

    class Meta:
        model = Promotion
        fields = [
            "id",
            "title",
            "description",
            "products",
            "discount_type",
            "discount_value",
            "start_date",
            "end_date",
            "is_active",
            "image",
            "is_current",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "is_current",
            "created_at",
            "updated_at",
        ]



class ProductSerializer(serializers.ModelSerializer):
	brand = serializers.StringRelatedField(read_only=True)
	category = serializers.StringRelatedField(read_only=True)

	class Meta:
		model = Product
		fields = '__all__'

