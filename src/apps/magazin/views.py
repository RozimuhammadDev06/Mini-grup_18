from rest_framework import permissions, viewsets

from .models import Product
from .serializers import ProductSerializer
from rest_framework import permissions, viewsets

from .models import Product, Promotion
from .serializers import (
    ProductSerializer,
    PromotionSerializer,
)
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from .models import Cart
from .serializers import CartSerializer


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get_queryset(self):
        return Cart.objects.filter(
            user=self.request.user
        ).prefetch_related("items")

    def create(self, request, *args, **kwargs):
        cart, created = Cart.objects.get_or_create(
            user=request.user,
            defaults={
                "session_key": request.data.get(
                    "session_key",
                    "",
                ),
            },
        )

        serializer = self.get_serializer(cart)

        return Response(
            serializer.data,
            status=(
                status.HTTP_201_CREATED
                if created
                else status.HTTP_200_OK
            ),
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



class BrandViewSet(viewsets.ModelViewSet):
    from .models import Brand
    from .serializers import BrandSerializer

    queryset = Brand.objects.all()
    serializer_class = BrandSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]


class CategoryViewSet(viewsets.ModelViewSet):
    from .models import Category
    from .serializers import CategorySerializer

    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]


class CartItemViewSet(viewsets.ModelViewSet):
    from .models import CartItem
    from .serializers import CartItemSerializer

    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]


class OrderViewSet(viewsets.ModelViewSet):
    from .models import Order
    from .serializers import OrderSerializer

    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]


class NewsViewSet(viewsets.ModelViewSet):
    from .models import News
    from .serializers import NewsSerializer

    queryset = News.objects.all()
    serializer_class = NewsSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]


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
