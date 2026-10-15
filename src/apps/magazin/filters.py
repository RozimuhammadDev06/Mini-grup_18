"""
Katalog, yangiliklar va sharhlar filtrlari.

Ro'yxat qiymatlari vergul bilan: ?brand=makita,bosch
category / brand / product_type — id yoki slug qabul qiladi.
Eski so'rovlar (?category=1, ?price__gte=100, ?material__icontains=...) ishlashda davom etadi.
"""

import django_filters
from django.db.models import F, Q

from .models import Category, News, Product, Review
from .search import unicode_iexact_any


def split_values(value):
    return [item.strip() for item in str(value).split(",") if item.strip()]


def id_or_slug_q(field, values):
    """['1', 'makita'] -> Q(field__id__in=[1]) | Q(field__slug__in=['makita'])"""
    ids = [int(v) for v in values if v.isdigit()]
    slugs = [v for v in values if not v.isdigit()]
    query = Q()
    if ids:
        query |= Q(**{f"{field}__id__in": ids})
    if slugs:
        query |= Q(**{f"{field}__slug__in": slugs})
    return query


def category_with_children(values):
    """Tanlangan kategoriyalar va ularning barcha ichki kategoriyalari id'lari"""
    ids = [int(v) for v in values if v.isdigit()]
    slugs = [v for v in values if not v.isdigit()]
    roots = Category.objects.filter(Q(id__in=ids) | Q(slug__in=slugs))

    result = set(roots.values_list("id", flat=True))
    frontier = set(result)
    while frontier:
        children = set(
            Category.objects.filter(parent_id__in=frontier).values_list("id", flat=True)
        )
        frontier = children - result
        result |= children
    return result


class ProductFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(method="filter_category")
    brand = django_filters.CharFilter(method="filter_brand")
    product_type = django_filters.CharFilter(method="filter_product_type")
    material = django_filters.CharFilter(method="filter_in_list")
    color = django_filters.CharFilter(method="filter_in_list")

    price_min = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    price_max = django_filters.NumberFilter(field_name="price", lookup_expr="lte")

    in_stock = django_filters.BooleanFilter(method="filter_in_stock")
    is_hit = django_filters.BooleanFilter(field_name="is_hit")
    has_discount = django_filters.BooleanFilter(method="filter_has_discount")

    class Meta:
        model = Product
        # Oldingi filterset_fields bilan bir xil lookup'lar saqlangan
        fields = {
            "material": ["icontains"],
            "color": ["icontains"],
            "price": ["exact", "gte", "lte"],
            "length_mm": ["exact", "gte", "lte"],
            "width_mm": ["exact", "gte", "lte"],
            "height_mm": ["exact", "gte", "lte"],
            "weight_kg": ["exact", "gte", "lte"],
            "stock_quantity": ["exact", "gte", "lte"],
        }

    def filter_category(self, queryset, name, value):
        return queryset.filter(category_id__in=category_with_children(split_values(value)))

    def filter_brand(self, queryset, name, value):
        return queryset.filter(id_or_slug_q("brand", split_values(value)))

    def filter_product_type(self, queryset, name, value):
        return queryset.filter(id_or_slug_q("product_type", split_values(value)))

    def filter_in_list(self, queryset, name, value):
        # "Металл" va "металл" bir xil hisoblanadi (Kirill harflari ham)
        return unicode_iexact_any(queryset, name, split_values(value))

    def filter_in_stock(self, queryset, name, value):
        if value is None:
            return queryset
        return queryset.filter(stock_quantity__gt=0) if value else queryset.filter(stock_quantity=0)

    def filter_has_discount(self, queryset, name, value):
        if value is None:
            return queryset
        discounted = Q(old_price__isnull=False, old_price__gt=F("price"))
        return queryset.filter(discounted) if value else queryset.exclude(discounted)


class NewsFilter(django_filters.FilterSet):
    rubric = django_filters.CharFilter(method="filter_rubric")
    product = django_filters.NumberFilter(field_name="product_id")

    class Meta:
        model = News
        fields = ["rubric", "product"]

    def filter_rubric(self, queryset, name, value):
        return queryset.filter(rubric__in=split_values(value))


class ReviewFilter(django_filters.FilterSet):
    product = django_filters.NumberFilter(field_name="product_id")
    rating = django_filters.NumberFilter(field_name="rating")
    rating_min = django_filters.NumberFilter(field_name="rating", lookup_expr="gte")

    class Meta:
        model = Review
        fields = ["product", "rating", "rating_min"]
