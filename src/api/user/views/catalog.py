"""
catalog/views.py — 'СтройОптТорг'

Complete catalog views including:
- Product List
- Product Category List
- Product Filter
- Product Detail
- Product Comparison

All views work together in one file.
"""

from rest_framework import viewsets, status, permissions, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination

from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from apps.catalog.models import (
    Category,
    Product,
    Compare,
    CategoryAttribute,
    Attribute,
)

from ..serializers.catalog_serializers import (
    CategorySerializer,
    ProductListSerializer,
    ProductDetailSerializer,
    FilterAttributeSerializer,
    CompareSerializer,
)


# =============================================================
# Pagination
# =============================================================

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 24
    page_size_query_param = "page_size"
    max_page_size = 100


# =============================================================
# PRODUCT CATEGORY LIST
# =============================================================

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Returns a list of active top-level categories.
    """

    queryset = Category.objects.filter(
        is_active=True,
        parent=None
    )

    serializer_class = CategorySerializer
    lookup_field = "slug"
    pagination_class = None


# =============================================================
# PRODUCT LIST + FILTER + DETAIL
# =============================================================

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Handles:

    - Product list
    - Product detail
    - Category filtering
    - Brand filtering
    - Price range filtering
    - Attribute filtering
    - Stock filtering
    - Searching
    - Sorting
    """

    serializer_class = ProductListSerializer
    pagination_class = StandardResultsSetPagination
    lookup_field = "slug"

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    search_fields = [
        "name",
        "article",
        "description",
    ]

    ordering_fields = [
        "price",
        "created_at",
        "name",
    ]

    def get_queryset(self):
        qs = Product.objects.filter(
            is_active=True
        ).select_related(
            "category",
            "brand",
        )

        # =====================================================
        # Category filter
        # =====================================================

        category_id = self.request.query_params.get("category")

        if category_id:
            children = Category.objects.filter(
                parent_id=category_id
            )

            category_ids = [
                category_id
            ] + list(
                children.values_list(
                    "id",
                    flat=True
                )
            )

            qs = qs.filter(
                category_id__in=category_ids
            )

        # =====================================================
        # Brand filter
        # =====================================================

        brand_id = self.request.query_params.get("brand")

        if brand_id:
            qs = qs.filter(
                brand_id=brand_id
            )

        # =====================================================
        # Price range filter
        # =====================================================

        price_min = self.request.query_params.get("price_min")
        price_max = self.request.query_params.get("price_max")

        if price_min is not None:
            qs = qs.filter(
                price__gte=price_min
            )

        if price_max is not None:
            qs = qs.filter(
                price__lte=price_max
            )

        # =====================================================
        # Attribute filter
        #
        # Example:
        # ?attr=3:12
        # ?attr=3:12&attr=5:8
        # =====================================================

        attr_params = self.request.query_params.getlist("attr")

        for attr_param in attr_params:
            try:
                attribute_id, value_id = attr_param.split(":")

                qs = qs.filter(
                    product_attributes__attribute_id=attribute_id,
                    product_attributes__value_id=value_id,
                )

            except ValueError:
                pass

        # =====================================================
        # Number attribute filter
        #
        # Example:
        # ?num_attr=3::1800
        # =====================================================

        num_attr_params = self.request.query_params.getlist(
            "num_attr"
        )

        for num_param in num_attr_params:
            try:
                parts = num_param.split(":")

                attribute_id = parts[0]

                min_val = (
                    parts[1]
                    if len(parts) > 1 and parts[1] != ""
                    else None
                )

                max_val = (
                    parts[2]
                    if len(parts) > 2 and parts[2] != ""
                    else None
                )

                pa_filter = Q(
                    product_attributes__attribute_id=attribute_id
                )

                if min_val is not None:
                    pa_filter &= Q(
                        product_attributes__value_number__gte=min_val
                    )

                if max_val is not None:
                    pa_filter &= Q(
                        product_attributes__value_number__lte=max_val
                    )

                qs = qs.filter(pa_filter)

            except (ValueError, IndexError):
                pass

        # =====================================================
        # In-stock filter
        # =====================================================

        in_stock = self.request.query_params.get("in_stock")

        if in_stock and in_stock.lower() in (
            "true",
            "1",
            "yes",
        ):
            qs = qs.filter(
                stocks__quantity__gt=0
            )

        return qs

    # =========================================================
    # Serializer
    # =========================================================

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ProductDetailSerializer

        return ProductListSerializer

    # =========================================================
    # Filter metadata
    # =========================================================

    @action(
        detail=False,
        methods=["get"],
        url_path="filters",
    )
    def filters(self, request):
        """
        Returns available filters for a category.

        Example:

        GET /api/catalog/products/filters/?category=5
        """

        category_id = request.query_params.get("category")

        if not category_id:
            return Response(
                {
                    "error": "category query parameter is required"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        category = Category.objects.filter(
            id=category_id,
            is_active=True,
        ).first()

        if not category:
            return Response(
                {
                    "error": "Category not found"
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        attribute_ids = CategoryAttribute.objects.filter(
            category=category,
            attribute__is_filterable=True,
        ).order_by(
            "sort"
        ).values_list(
            "attribute_id",
            flat=True,
        )

        attributes = Attribute.objects.filter(
            id__in=attribute_ids
        )

        serializer = FilterAttributeSerializer(
            attributes,
            many=True,
            context={
                "category": category
            },
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


# =============================================================
# PRODUCT COMPARISON
# =============================================================

class CompareViewSet(viewsets.ModelViewSet):
    """
    Product comparison.

    Authenticated users:
        Uses user.

    Guests:
        Uses X-Session-Key.
    """

    serializer_class = CompareSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    # =========================================================
    # Session key
    # =========================================================

    def _get_session_key(self):
        return (
            self.request.headers.get("X-Session-Key")
            or self.request.META.get(
                "HTTP_X_SESSION_KEY"
            )
        )

    # =========================================================
    # Queryset
    # =========================================================

    def get_queryset(self):
        user = self.request.user
        session_key = self._get_session_key()

        if user.is_authenticated:
            return Compare.objects.filter(
                user=user
            ).select_related(
                "product",
                "product__category",
                "product__brand",
            )

        if session_key:
            return Compare.objects.filter(
                session_key=session_key
            ).select_related(
                "product",
                "product__category",
                "product__brand",
            )

        return Compare.objects.none()

    # =========================================================
    # Get root category
    # =========================================================

    def _get_category(self, product):
        category = product.category

        while category.parent is not None:
            category = category.parent

        return category

    # =========================================================
    # Create comparison
    # =========================================================

    def perform_create(self, serializer):
        product = serializer.validated_data.get("product")

        if not product:
            return

        category = self._get_category(product)

        existing = self.get_queryset().first()

        if existing and existing.category_id != category.id:
            from rest_framework.exceptions import ValidationError

            raise ValidationError(
                "All compared products must belong to the same category."
            )

        serializer.save(
            user=(
                self.request.user
                if self.request.user.is_authenticated
                else None
            ),
            session_key=(
                None
                if self.request.user.is_authenticated
                else self._get_session_key()
            ),
            category=category,
        )

    # =========================================================
    # Toggle
    # =========================================================

    @action(
        detail=False,
        methods=["post"],
        url_path="toggle",
    )
    def toggle(self, request):

        product_id = request.data.get("product_id")

        if not product_id:
            return Response(
                {
                    "error": "product_id is required"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        product = Product.objects.filter(
            id=product_id,
            is_active=True,
        ).first()

        if not product:
            return Response(
                {
                    "error": "Product not found"
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        qs = self.get_queryset()

        existing = qs.filter(
            product=product
        ).first()

        # Remove
        if existing:
            existing.delete()

            return Response(
                {
                    "status": "removed",
                    "product_id": product.id,
                },
                status=status.HTTP_200_OK,
            )

        # Add
        serializer = self.get_serializer(
            data={
                "product": product.id
            }
        )

        serializer.is_valid(
            raise_exception=True
        )

        self.perform_create(serializer)

        return Response(
            {
                "status": "added",
                "product_id": product.id,
            },
            status=status.HTTP_201_CREATED,
        )

    # =========================================================
    # Comparison table
    # =========================================================

    @action(
        detail=False,
        methods=["get"],
        url_path="table",
    )
    def table(self, request):

        items = self.get_queryset()

        if not items.exists():
            return Response(
                {
                    "products": [],
                    "rows": [],
                },
                status=status.HTTP_200_OK,
            )

        products = [
            item.product
            for item in items
        ]

        product_details = ProductDetailSerializer(
            products,
            many=True,
            context={
                "request": request
            },
        ).data

        row_map = {}

        for detail in product_details:

            for attr in detail.get(
                "comparable_attributes",
                []
            ):

                if not attr.get(
                    "is_comparable"
                ):
                    continue

                key = attr[
                    "attribute_code"
                ]

                row_map.setdefault(
                    key,
                    {
                        "name": attr[
                            "attribute_name"
                        ],
                        "unit": attr[
                            "unit"
                        ],
                        "values": {},
                    },
                )

                row_map[key]["values"][
                    detail["id"]
                ] = attr["value"]

        rows = [
            {
                "attribute": key,
                **value,
            }
            for key, value in row_map.items()
        ]

        return Response(
            {
                "products": product_details,
                "rows": rows,
            },
            status=status.HTTP_200_OK,
        )

    # =========================================================
    # Clear comparison
    # =========================================================

    @action(
        detail=False,
        methods=["post"],
        url_path="clear",
    )
    def clear(self, request):

        self.get_queryset().delete()

        return Response(
            {
                "status": "cleared"
            },
            status=status.HTTP_200_OK,
        )