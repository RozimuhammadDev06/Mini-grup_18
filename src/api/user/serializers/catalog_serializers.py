from rest_framework import serializers
from .models import Category, Brand, Product, ProductImage, Stock, Attribute, ProductAttribute

class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'sort', 'is_active', 'children']

    def get_children(self, obj):
        if obj.children.exists():
            return CategorySerializer(obj.children.filter(is_active=True), many=True).data
        return []

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'slug', 'logo']

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'sort', 'is_main']

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ['quantity', 'status', 'synced_at']

class ProductListSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    stocks = StockSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'article', 'price', 'old_price', 'images', 'stocks']

class ProductDetailSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    stocks = StockSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'article', 'price', 'old_price', 'description', 'attrs_json', 'category', 'brand', 'images', 'stocks', 'created_at']


from rest_framework import serializers
from .models import Category, Product

class CategorySerializer(serializers.ModelSerializer):
    """
    Recursive serializer to handle nested categories (parent/child).
    """
    children = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'sort', 'is_active', 'children', 'product_count']

    def get_children(self, obj):
        """Recursively fetches active child categories."""
        if obj.children.filter(is_active=True).exists():
            return CategorySerializer(obj.children.filter(is_active=True), many=True).data
        return []

    def get_product_count(self, obj):
        """Returns the number of active products in this category."""
        return obj.products.filter(is_active=True).count()

class ProductListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer optimized for the main product listing page.
    Excludes heavy fields like full description to ensure fast loading of 45k SKUs.
    """
    category_name = serializers.ReadOnlyField(source='category.name')
    discount_percent = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'article', 'price', 'old_price', 
            'category_name', 'discount_percent', 'created_at'
        ]

    def get_discount_percent(self, obj):
        """Calculates the discount percentage if old_price exists."""
        if obj.old_price and obj.price < obj.old_price:
            return int((1 - obj.price / obj.old_price) * 100)
        return 0

class ProductDetailSerializer(serializers.ModelSerializer):
    """
    Full serializer for the individual product detail page.
    """
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'article', 'price', 'old_price', 
            'attrs_json', 'description', 'category', 'created_at'
        ]
