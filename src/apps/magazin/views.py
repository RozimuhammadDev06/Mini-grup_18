from rest_framework import permissions, viewsets, status
from rest_framework.response import Response

from .models import (
    Brand,
    Cart,
    CartItem,
    Category,
    News,
    Order,
    Product,
    Promotion,
    Review,
)
from .serializers import (
    ProductSerializer,
    PromotionSerializer,
    CartSerializer,
    CartItemSerializer,
    BrandSerializer,
    CategorySerializer,
    OrderSerializer,
    NewsSerializer,
    ReviewSerializer,
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


class CartViewSet(viewsets.ModelViewSet):
    from .models import Cart
    from .serializers import CartSerializer

    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        # If user is authenticated, return or create a cart for them.
        if request.user and request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=request.user)
            serializer = self.get_serializer(cart)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # Fallback: create anonymous cart tied to session_key if provided
        session_key = request.data.get("session_key") or request.session.session_key
        cart = Cart.objects.create(session_key=session_key)
        serializer = self.get_serializer(cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


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



# Note: ProductViewSet is defined above with documentation and permissions.


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        queryset = Review.objects.select_related(
            "product",
            "user",
        )

        if self.action in [
            "list",
            "retrieve",
        ]:
            return queryset.filter(
                is_approved=True,
            )

        if not self.request.user.is_authenticated:
            return Review.objects.none()

        return queryset.filter(
            user=self.request.user,
        )

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

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            is_approved=False,
        )

    def perform_update(self, serializer):
        serializer.save(
            is_approved=False,
        )
    