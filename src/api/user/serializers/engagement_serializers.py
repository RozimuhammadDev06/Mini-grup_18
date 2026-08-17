from rest_framework import serializers
from .models import Review, Wishlist, Compare, Lead
from apps.catalog.serializers import ProductListSerializer

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'author_name', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

class WishlistSerializer(serializers.ModelSerializer):
    product_details = ProductListSerializer(source='product', read_only=True)

    class Meta:
        model = Wishlist
        fields = ['id', 'product', 'product_details']

class CompareSerializer(serializers.ModelSerializer):
    product_details = ProductListSerializer(source='product', read_only=True)

    class Meta:
        model = Compare
        fields = ['id', 'product', 'category', 'session_key', 'product_details']
        read_only_fields = ['id']

class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = ['id', 'type', 'name', 'phone', 'product_id', 'consent', 'status', 'created_at']
        read_only_fields = ['id', 'status', 'created_at']

    def validate_consent(self, value):
        if not value:
            raise serializers.ValidationError("You must provide consent to process your data.")
        return value


from rest_framework import serializers
from .models import Wishlist
from apps.catalog.serializers import ProductListSerializer

class WishlistSerializer(serializers.ModelSerializer):
    # This includes full product info (name, price, image) in the wishlist response
    product_details = ProductListSerializer(source='product', read_only=True)

    class Meta:
        model = Wishlist
        fields = ['id', 'product', 'product_details', 'created_at']
        read_only_fields = ['id', 'created_at']
