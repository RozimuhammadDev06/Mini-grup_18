"""
catalog/urls.py — 'СтройОптТорг'

Routes for:
- Task: Product Category List (2026-08-17)   -> /api/catalog/categories/
- Task: Productni List (2026-08-16)           -> /api/catalog/products/
- Task: Producti Filtr (2026-08-18)           -> /api/catalog/products/filters/
- Task: Product detaili (2026-08-19)          -> /api/catalog/products/{slug}/
- Task: Product Savneniya (2026-08-21)        -> /api/catalog/compare/

All routes in one file — replace the whole file with this.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, CompareViewSet
from .home_views import HomePageView

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'compare', CompareViewSet, basename='compare')

urlpatterns = [
    path('', include(router.urls)),

    # --- TASK: HOME PAGE (2026-08-21) ---
    path('home/', HomePageView.as_view(), name='home-page'),
]
