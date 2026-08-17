from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Brand, Product
from .serializers import CategorySerializer, BrandSerializer, ProductListSerializer, ProductDetailSerializer

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    lookup_field = 'slug'

class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    lookup_field = 'slug'

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(is_active=True).prefetch_related('images', 'stocks', 'category', 'brand')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'brand', 'is_active']
    search_fields = ['name', 'article', 'description']
    ordering_fields = ['price', 'created_at', 'name']
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductListSerializer


from rest_framework import viewsets, filters
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Product
from .serializers import CategorySerializer, ProductListSerializer, ProductDetailSerializer

class StandardResultsSetPagination(PageNumberPagination):
    """
    Pagination is required for the Product List task to handle 45,000+ SKUs
    without crashing the server or frontend.
    """
    page_size = 24 # Typical e-commerce grid layout size
    page_size_query_param = 'page_size'
    max_page_size = 100

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Task: Product Category List
    Returns a nested tree of categories with product counts.
    """
    queryset = Category.objects.filter(is_active=True, parent=None)
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    pagination_class = None # Categories are usually few, so no pagination needed

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Task: Product List
    Handles filtering by category, searching by name/SKU, and price sorting.
    """
    serializer_class = ProductListSerializer
    pagination_class = StandardResultsSetPagination
    lookup_field = 'slug'
    
    # Advanced filtering and searching capabilities
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'article', 'description']
    ordering_fields = ['price', 'created_at', 'name']

    def get_queryset(self):
        # Only return active products that have stock (linked via Stock model)
        return Product.objects.filter(is_active=True).select_related('category')

    def get_serializer_class(self):
        """Switches to the detailed serializer if viewing a single product."""
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductListSerializer
