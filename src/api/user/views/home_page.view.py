"""
catalog/home_views.py — 'СтройОптТорг'

TASK: HOME PAGE (2026-08-21)
"Siz home page da qanday malumotlar bolsa shularni chiqarasiz u yerda
misol category, yangiliklar, mashxur tavarlar, engkop sotilgan tavarlar
shulardan minimal 10 tasini chiqarib qoyasiz"

One endpoint returns everything the home page needs:
- categories            (top-level, with product counts)
- news                  (latest articles / "yangiliklar")
- popular_products      (products with old_price -> "on sale" / popular)
- best_selling_products (products ordered by highest order quantity sold)
"""

from django.db.models import Sum, Count, Q, F
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.content.models import Article

from .models import Category, Product, Stock, ProductImage


# =============================================================
# Minimal lightweight product serializer for the home page
# (we define it here to avoid pulling the whole detail serializer)
# =============================================================
def _product_dict(product):
    """Build a lightweight dict for one product card."""
    image = None
    main_image = product.images.filter(is_main=True).first()
    if not main_image:
        main_image = product.images.first()
    if main_image:
        image = main_image.image.url

    stock = product.stocks.first()
    in_stock = True
    quantity = None
    if stock:
        in_stock = stock.quantity > 0
        quantity = stock.quantity

    return {
        'id': product.id,
        'name': product.name,
        'slug': product.slug,
        'article': product.article,
        'price': str(product.price),
        'old_price': str(product.old_price) if product.old_price else None,
        'discount_percent': product.discount_percent,
        'image': image,
        'in_stock': in_stock,
        'quantity': quantity,
        'category': {
            'id': product.category_id,
            'name': product.category.name,
            'slug': product.category.slug,
        },
    }


# =============================================================
# TASK: HOME PAGE (2026-08-21)
# =============================================================
class HomePageView(APIView):
    """
    Aggregates all home-page data into ONE response:
    - categories:  top-level active categories (min. 10 if available)
    - news:        latest published news articles (min. 10)
    - popular_products: products currently on sale (has old_price)
    - best_selling_products: products with highest total sold quantity

    Public endpoint — no authentication required.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        # --- 1. Categories (top-level, active) ---
        categories = Category.objects.filter(parent__isnull=True, is_active=True)
        categories_data = [
            {
                'id': cat.id,
                'name': cat.name,
                'slug': cat.slug,
                'image': cat.image.url if cat.image else None,
                'product_count': cat.products.filter(is_active=True).count(),
            }
            for cat in categories
        ]

        # --- 2. News (latest published) ---
        news_qs = Article.objects.filter(
            published_at__isnull=False,
            type='news',
        ).order_by('-published_at')
        news_data = [
            {
                'id': article.id,
                'title': article.title,
                'slug': article.slug,
                'image': article.image.url if article.image else None,
                'published_at': article.published_at,
            }
            for article in news_qs
        ]

        # --- 3. Popular products (products on sale / discounted) ---
        popular = Product.objects.filter(
            is_active=True,
            old_price__isnull=False,
        ).exclude(old_price__lte=F('price')).order_by('-created_at')
        popular_data = [_product_dict(p) for p in popular]

        # --- 4. Best selling products (by total ordered quantity) ---
        # Aggregates quantity from OrderItem rows (orders.models has
        # related_name='items' from OrderItem -> product)
        top_sold = (
            Product.objects.filter(is_active=True)
            .annotate(total_sold=Sum('items__quantity'))
            .filter(total_sold__gt=0)
            .order_by('-total_sold')
        )
        best_selling_data = [_product_dict(p) for p in top_sold]

        return Response({
            'categories': categories_data,
            'news': news_data,
            'popular_products': popular_data,
            'best_selling_products': best_selling_data,
        }, status=status.HTTP_200_OK)
