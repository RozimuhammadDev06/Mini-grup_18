from rest_framework import serializers

from .models import Product, Brand, Category


class ProductSerializer(serializers.ModelSerializer):
	brand = serializers.StringRelatedField(read_only=True)
	category = serializers.StringRelatedField(read_only=True)

	class Meta:
		model = Product
		fields = '__all__'

