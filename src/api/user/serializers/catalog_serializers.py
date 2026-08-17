"""
catalog/serializers.py — 'СтройОптТорг'

Complete serializers including:
- Task: Productni List (2026-08-16)
- Task: Product Category List (2026-08-17)
- Task: Producti Filtr (2026-08-18) — filter metadata serializers
- Task: Product detaili (2026-08-19) — full detail with images, stock, attributes
- Task: Product Savneniya (2026-08-21) — compare list serializer

All serializers work together in one file — replace the whole file with this.
"""

from rest_framework import serializers
from apps.catalog.models import (
    Category,
    Brand,
    Attribute,
    CategoryAttribute,
    AttributeValue,
    Product,
    ProductAttribute,
    ProductImage,
    Stock,
    Compare,
)


# =============================================================
# TASK: PRODUCT CATEGORY LIST
# =============================================================
class CategorySerializer(serializers.ModelSerializer):
    """Recursive serializer to handle nested categories (parent/child)."""
    children = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'sort', 'is_active', 'image_url', 'children', 'product_count']

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

    def get_children(self, obj):
        """Recursively fetches active child categories."""
        children = obj.children.filter(is_active=True)
        if children.exists():
            return CategorySerializer(children, many=True, context=self.context).data
        return []

    def get_product_count(self, obj):
        """Returns the number of active products in this category."""
        return obj.products.filter(is_active=True).count()


# =============================================================
# TASK: PRODUCTI FILTR (Attribute / filter metadata)
# =============================================================
class FilterAttributeValueSerializer(serializers.ModelSerializer):
    """Serializes a single attribute value option (e.g. 'Cordless' for Type)."""
    class Meta:
        model = AttributeValue
        fields = ['id', 'value_string', 'value_number']


class FilterAttributeSerializer(serializers.ModelSerializer):
    """
    One filterable attribute with its possible values.
    Used by the frontend to build filter UI (checkboxes, range sliders).
    Example: {name: "Power (W)", type: "number", unit: "W",
              min: 800, max: 2200, values: [...]}
    """
    values = serializers.SerializerMethodField()
    min_value = serializers.SerializerMethodField()
    max_value = serializers.SerializerMethodField()
    sort = serializers.SerializerMethodField()

    class Meta:
        model = Attribute
        fields = ['id', 'code', 'name', 'type', 'unit', 'is_comparable', 'sort', 'min_value', 'max_value', 'values']

    def get_sort(self, obj):
        # Sort order within the current category (from CategoryAttribute)
        category = self.context.get('category')
        if category:
            ca = CategoryAttribute.objects.filter(category=category, attribute=obj).first()
            if ca:
                return ca.sort
        return 0

    def get_min_value(self, obj):
        """Min value among products in this category (for range filters)."""
        from django.db.models import Min
        category = self.context.get('category')
        qs = ProductAttribute.objects.filter(attribute=obj)
        if category:
            qs = qs.filter(product__category=category)
        agg = qs.aggregate(min_val=Min('value_number'))
        return agg.get('min_val')

    def get_max_value(self, obj):
        """Max value among products in this category (for range filters)."""
        from django.db.models import Max
        category = self.context.get('category')
        qs = ProductAttribute.objects.filter(attribute=obj)
        if category:
            qs = qs.filter(product__category=category)
        agg = qs.aggregate(max_val=Max('value_number'))
        return agg.get('max_val')

    def get_values(self, obj):
        """All possible values for this attribute (for checkbox filters)."""
        values = obj.values.all()
        return FilterAttributeValueSerializer(values, many=True).data


# =============================================================
# TASK: PRODUCTNI LIST
# =============================================================
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_main']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        if instance.image and request:
            data['image'] = request.build_absolute_uri(instance.image.url)
        return data


class ProductListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer optimized for the main product listing page.
    Excludes heavy fields like full description for fast loading of 45k SKUs.
    """
    category_name = serializers.ReadOnlyField(source='category.name')
    brand_name = serializers.ReadOnlyField(source='brand.name')
    discount_percent = serializers.SerializerMethodField()
    main_image = serializers.SerializerMethodField()
    in_stock = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'article', 'price', 'old_price',
            'category_name', 'brand_name', 'discount_percent',
            'main_image', 'in_stock', 'created_at',
        ]

    def get_discount_percent(self, obj):
        if obj.old_price and obj.price < obj.old_price:
            return int((1 - obj.price / obj.old_price) * 100)
        return 0

    def get_main_image(self, obj):
        main = obj.images.filter(is_main=True).first() or obj.images.first()
        if main and main.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(main.image.url)
            return main.image.url
        return None

    def get_in_stock(self, obj):
        latest_stock = obj.stocks.first()
        return latest_stock.is_available if latest_stock else False


# =============================================================
# TASK: PRODUCT DETAILI
# =============================================================
class ProductDetailSerializer(serializers.ModelSerializer):
    """Full serializer for the individual product detail page."""
    category = CategorySerializer(read_only=True)
    brand_name = serializers.ReadOnlyField(source='brand.name')
    brand_slug = serializers.ReadOnlyField(source='brand.slug')
    images = ProductImageSerializer(many=True, read_only=True)
    discount_percent = serializers.SerializerMethodField()
    stock = serializers.SerializerMethodField()
    comparable_attributes = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'article', 'price', 'old_price',
            'discount_percent', 'brand_name', 'brand_slug', 'category',
            'attrs_json', 'description', 'images', 'stock',
            'comparable_attributes', 'created_at',
        ]

    def get_discount_percent(self, obj):
        if obj.old_price and obj.price < obj.old_price:
            return int((1 - obj.price / obj.old_price) * 100)
        return 0

    def get_stock(self, obj):
        """Current stock status from the latest ERP sync."""
        latest = obj.stocks.first()
        if latest:
            return {
                'quantity': latest.quantity,
                'status': latest.status,
                'is_available': latest.is_available,
                'synced_at': latest.synced_at,
            }
        return {'quantity': 0, 'status': 'unknown', 'is_available': False, 'synced_at': None}

    def get_comparable_attributes(self, obj):
        """
        Returns structured attributes used on the detail page and
        in the comparison table (comparable attributes from the ERD).
        """
        result = []
        for pa in obj.product_attributes.select_related('attribute', 'value_id').all():
            result.append({
                'attribute_name': pa.attribute.name,
                'attribute_code': pa.attribute.code,
                'unit': pa.attribute.unit,
                'value': str(pa.value_id.value_string or pa.value_number or ''),
                'is_comparable': pa.attribute.is_comparable,
            })
        return result


# =============================================================
# TASK: PRODUCT SAVNENIYA (Product Comparison)
# =============================================================
class CompareSerializer(serializers.ModelSerializer):
    """
    Comparison item — returns the product with full detail so the
    frontend can render a comparison table in one request.
    """
    product = ProductDetailSerializer(read_only=True)

    class Meta:
        model = Compare
        fields = ['id', 'product', 'created_at']
