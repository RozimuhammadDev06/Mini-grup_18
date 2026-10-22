from rest_framework import permissions, viewsets, status
from rest_framework.response import Response

from django.db.models import Avg, Count, Max, Min, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets
from rest_framework.decorators import action

from .api_defaults import AUTHENTICATION_CLASSES, CatalogPagination
from .filters import NewsFilter, ProductFilter, ReviewFilter
from .search import UnicodeSearchFilter, unicode_lower

from .models import Product
from .serializers import ProductSerializer


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







from .models import Product
from .serializers import ProductSerializer

class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Hamma user mahsulotlarni ko‘rishi mumkin.
    Faqat staff user mahsulot yaratishi, o‘zgartirishi va o‘chirishi mumkin.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
        )


class NewsWritePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_staff:
            return True
        return (
            view.action == "create"
            and user.has_perm("magazin.add_news")
        )


class ProductViewSet(viewsets.ModelViewSet):
    """
    Katalog mahsulotlari.

    GET /products/?category=power-tools&brand=makita,bosch&material=Металл
        &price_min=1000&price_max=20000&in_stock=true&search=дрель&ordering=-price
    GET /products/{id yoki slug}/
    GET /products/filters/?category=power-tools   — filtr paneli variantlari
    """

    serializer_class = ProductSerializer
    authentication_classes = AUTHENTICATION_CLASSES
    pagination_class = CatalogPagination

    filter_backends = [
        DjangoFilterBackend,
        UnicodeSearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = ProductFilter

    search_fields = [
        "name",
        "article",
        "description",
        "material",
        "color",
        "brand__name",
        "category__name",
        "product_type__name",
    ]

    ordering_fields = [
        "price",
        "name",
        "created_at",
        "stock_quantity",
        "rating_avg",
    ]

    ordering = [
        "-created_at",
    ]

    def get_queryset(self):
        approved = Q(reviews__is_approved=True)
        queryset = (
            Product.objects.select_related(
                "brand",
                "category",
                "product_type",
            )
            .prefetch_related("images")
            .annotate(
                rating_avg=Avg("reviews__rating", filter=approved),
                reviews_count=Count("reviews", filter=approved, distinct=True),
            )
        )

        if self.action in [
            "list",
            "retrieve",
        ]:
            return queryset.filter(
                is_active=True,
            )

        return queryset

    def get_object(self):
        """/products/12/ — id bo'yicha, /products/perforator-makita/ — slug bo'yicha"""
        lookup = self.kwargs[self.lookup_url_kwarg or self.lookup_field]
        field = "pk" if str(lookup).isdigit() else "slug"
        obj = get_object_or_404(self.get_queryset(), **{field: lookup})
        self.check_object_permissions(self.request, obj)
        return obj

    @action(detail=False, methods=["get"], url_path="filters")
    def filter_options(self, request):
        """
        Filtr paneli uchun variantlar (soni bilan) va narx/o'lcham chegaralari.
        Faqat ?category= va ?search= hisobga olinadi — boshqa filtr tanlanganda
        variantlar yo'qolib qolmasligi uchun.
        """
        # Reyting annotatsiyasisiz toza queryset — GROUP BY to'g'ri ishlashi uchun
        queryset = Product.objects.filter(is_active=True)
        category = request.query_params.get("category")
        if category:
            queryset = ProductFilter(
                {"category": category}, queryset=queryset
            ).qs
        queryset = UnicodeSearchFilter().filter_queryset(request, queryset, self)
        queryset = queryset.order_by()

        def ranges(field):
            data = queryset.aggregate(min=Min(field), max=Max(field))
            return {"min": data["min"], "max": data["max"]}

        def related_options(field):
            rows = (
                queryset.exclude(**{f"{field}__isnull": True})
                .values(f"{field}__id", f"{field}__name", f"{field}__slug")
                .annotate(count=Count("id", distinct=True))
                .order_by("-count", f"{field}__name")
            )
            return [
                {
                    "id": row[f"{field}__id"],
                    "name": row[f"{field}__name"],
                    "slug": row[f"{field}__slug"],
                    "count": row["count"],
                }
                for row in rows
            ]

        def value_options(field):
            # "Металл" va "металл" bitta variant bo'lib sanaladi
            rows = (
                queryset.exclude(**{field: ""})
                .annotate(_key=unicode_lower(field))
                .values("_key")
                .annotate(count=Count("id", distinct=True), value=Min(field))
                .order_by("-count", "_key")
            )
            return [{"value": row["value"], "count": row["count"]} for row in rows]

        return Response(
            {
                "total": queryset.values("id").distinct().count(),
                "in_stock_count": queryset.filter(stock_quantity__gt=0)
                .values("id")
                .distinct()
                .count(),
                "price": ranges("price"),
                "length_mm": ranges("length_mm"),
                "width_mm": ranges("width_mm"),
                "height_mm": ranges("height_mm"),
                "brands": related_options("brand"),
                "product_types": related_options("product_type"),
                "materials": value_options("material"),
                "colors": value_options("color"),
            }
        )

    def get_permissions(self):
        if self.action in [
            "list",
            "retrieve",
            "filter_options",
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
    """
    Yangiliklar / blog.

    GET /news/?rubric=news,tips&search=...&ordering=-published_at&page=2
    GET /news/{id yoki slug}/
    GET /news/rubrics/   — rubrikalar va har biridagi yangiliklar soni
    Yaratish / o'zgartirish / o'chirish — faqat admin (is_staff).
    """

    serializer_class = NewsSerializer
    authentication_classes = AUTHENTICATION_CLASSES
    pagination_class = CatalogPagination

    filter_backends = [
        DjangoFilterBackend,
        UnicodeSearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = NewsFilter
    search_fields = ["title", "excerpt", "content"]
    ordering_fields = ["published_at", "title"]
    ordering = ["-published_at", "-id"]

    def get_queryset(self):
        queryset = News.objects.select_related("product")

        # Admin bo'lmaganlar faqat chop etilgan va vaqti kelgan yangiliklarni ko'radi
        user = self.request.user
        if not (user and user.is_staff):
            queryset = queryset.filter(
                is_published=True,
                published_at__lte=timezone.now(),
            )
        return queryset

    def get_object(self):
        lookup = self.kwargs[self.lookup_url_kwarg or self.lookup_field]
        field = "pk" if str(lookup).isdigit() else "slug"
        obj = get_object_or_404(self.get_queryset(), **{field: lookup})
        self.check_object_permissions(self.request, obj)
        return obj

    def get_permissions(self):
        if self.action in ["list", "retrieve", "rubrics"]:
            return [permissions.AllowAny()]
        return [NewsWritePermission()]

    @action(detail=False, methods=["get"])
    def rubrics(self, request):
        """[{slug, name, count}] + "Все публикации" uchun umumiy son"""
        queryset = self.get_queryset()
        counts = dict(
            queryset.order_by()
            .values_list("rubric")
            .annotate(count=Count("id"))
        )
        return Response(
            {
                "total": queryset.count(),
                "results": [
                    {"slug": value, "name": label, "count": counts.get(value, 0)}
                    for value, label in News.Rubric.choices
                ],
            }
        )


class PromotionViewSet(viewsets.ModelViewSet):
    """
    Aksiya CRUD API.

    Aksiyalarni ko‘rish hammaga ochiq.
    Aksiya yaratish, o‘zgartirish va o‘chirish
    faqat login qilgan foydalanuvchiga ruxsat etiladi.
    """

    serializer_class = PromotionSerializer

    def get_queryset(self):
        queryset = Promotion.objects.order_by("-id")

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
    """
    Mahsulot sharhlari.

    GET /reviews/?product=12&ordering=-rating   — faqat tasdiqlangan sharhlar
    POST /reviews/ {product, rating, text}      — login talab qilinadi, admin tasdiqlaguncha ko'rinmaydi
    """

    serializer_class = ReviewSerializer
    authentication_classes = AUTHENTICATION_CLASSES
    pagination_class = CatalogPagination

    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    filterset_class = ReviewFilter
    ordering_fields = ["created_at", "rating"]
    ordering = ["-created_at"]

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
    