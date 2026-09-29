from rest_framework import permissions, viewsets

from .models import Product
from .serializers import ProductSerializer
from rest_framework import permissions, viewsets

from .models import Product, Promotion
from .serializers import (
    ProductSerializer,
    PromotionSerializer,
)


class ProductViewSet(viewsets.ModelViewSet):
    """
    Product CRUD API.

    Mahsulotlarni ko‘rish hammaga ochiq.
    Mahsulot yaratish, o‘zgartirish va o‘chirish
    faqat login qilgan foydalanuvchiga ruxsat etiladi.
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.action in [
            "list",
            "retrieve",
        ]:
            return [
                permissions.AllowAny(),
            ]

        return [
            permissions.IsAuthenticated(),
        ]


class PromotionViewSet(viewsets.ModelViewSet):
    """
    Aksiya CRUD API.

    Aksiyalarni ko‘rish hammaga ochiq.
    Aksiya yaratish, o‘zgartirish va o‘chirish
    faqat login qilgan foydalanuvchiga ruxsat etiladi.
    """

    serializer_class = PromotionSerializer

    def get_queryset(self):
        queryset = Promotion.objects.prefetch_related(
            "products"
        )

        if self.action in [
            "list",
            "retrieve",
        ]:
            return queryset.filter(
                is_active=True
            )

        return queryset

    def get_permissions(self):
        if self.action in [
            "list",
            "retrieve",
        ]:
            return [
                permissions.AllowAny(),
            ]

        return [
            permissions.IsAuthenticated(),
        ]



class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [
                permissions.AllowAny(),
            ]

        return [
            permissions.IsAuthenticated(),
        ]
