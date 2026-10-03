from rest_framework import viewsets
from apps.magazin.models import Category, Brand, Product, Cart, CartItem, Order,News
from .serializers import (
    CategorySerializer, BrandSerializer, ProductSerializer,
    CartSerializer, CartItemSerializer, OrderSerializer,NewsSerializer
)

# Qolgan viewset kodlari o'zgarishsiz qoladi...

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'slug'

from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet


class CartViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class NewsViewSet(viewsets.ModelViewSet):
    queryset = News.objects.all()
    serializer_class = NewsSerializer

