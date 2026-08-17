from rest_framework import serializers
from apps.orders.models import Cart, CartItem, Order, OrderItem, PromoCode, DiscountTier
from api.user.serializers.catalog_serializers import ProductListSerializer

class CartItemSerializer(serializers.ModelSerializer):
    product_details = ProductListSerializer(source='product', read_only=True)
    total_item_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'price', 'product_details', 'total_item_price']

    def get_total_item_price(self, obj):
        return obj.quantity * obj.price

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    cart_total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'session_key', 'promo_code', 'items', 'cart_total', 'updated_at']
        read_only_fields = ['id', 'updated_at']

    def get_cart_total(self, obj):
        return sum(item.quantity * item.price for item in obj.items.all())

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'name_snapshot', 'article_snapshot', 'price', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'number', 'user', 'status', 'delivery_type', 'address_snapshot',
            'payment_method', 'subtotal', 'cart_discount', 'promo_discount',
            'delivery_cost', 'total', 'created_at', 'paid_at', 'items'
        ]
        read_only_fields = ['id', 'number', 'user', 'created_at', 'paid_at', 'subtotal', 'total']


from rest_framework import serializers
from .models import Order, OrderItem
from apps.catalog.serializers import ProductListSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    product_details = ProductListSerializer(source='product', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_details', 'name_snapshot', 'article_snapshot', 'price', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'number', 'user', 'status', 'delivery_type', 'address_snapshot',
            'payment_method', 'subtotal', 'cart_discount', 'promo_discount',
            'delivery_cost', 'total', 'created_at', 'paid_at', 'items'
        ]
        read_only_fields = ['id', 'number', 'user', 'created_at', 'paid_at', 'subtotal', 'total']

class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'delivery_type', 'address_snapshot', 'payment_method',
            'cart_discount', 'promo_discount', 'delivery_cost', 'total'
        ]
