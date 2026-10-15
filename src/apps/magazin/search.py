"""
Kirill harflari bilan katta-kichik harfga qaramaydigan qidiruv.

SQLite'ning LOWER / LIKE funksiyalari faqat lotin harflarini kichraytiradi:
"Перфоратор" LIKE "%перфоратор%" -> topilmaydi. Shuning uchun SQLite ulanishiga
Python'ning str.lower() dan foydalanadigan UNICODE_LOWER funksiyasi qo'shiladi
(apps.py -> ready). Mavjud funksiyalar o'zgartirilmaydi, boshqa API'larga ta'sir yo'q.
PostgreSQL'da odatiy LOWER (u Unicode'ni to'g'ri biladi) ishlatiladi.
"""

from django.db import connection
from django.db.models import CharField, Func, Q
from django.db.models.functions import Lower
from rest_framework.filters import SearchFilter

SQLITE_FUNCTION = "UNICODE_LOWER"


def register_sqlite_functions(sender, connection, **kwargs):
    if connection.vendor == "sqlite":
        connection.connection.create_function(
            SQLITE_FUNCTION,
            1,
            lambda value: value.lower() if isinstance(value, str) else value,
            deterministic=True,
        )


class UnicodeLower(Func):
    function = SQLITE_FUNCTION
    output_field = CharField()


def unicode_lower(expression):
    if connection.vendor == "sqlite":
        return UnicodeLower(expression)
    return Lower(expression)


def unicode_iexact_any(queryset, field, values):
    """field qiymati ro'yxatdagilardan biriga teng (katta-kichik harfga qaramay)"""
    alias = f"_lower_{field}"
    lowered = [value.lower() for value in values]
    return queryset.annotate(**{alias: unicode_lower(field)}).filter(
        **{f"{alias}__in": lowered}
    )


class UnicodeSearchFilter(SearchFilter):
    """
    ?search=перфоратор makita — har bir so'z search_fields'dan birida bo'lishi kerak.
    Odatiy SearchFilter bilan bir xil parametr, faqat Kirill harflarini ham to'g'ri taqqoslaydi.
    """

    def filter_queryset(self, request, queryset, view):
        fields = getattr(view, "search_fields", None)
        terms = self.get_search_terms(request)
        if not fields or not terms:
            return queryset

        aliases = {}
        for index, field in enumerate(fields):
            alias = f"_search_{index}"
            aliases[alias] = unicode_lower(field)
        queryset = queryset.annotate(**aliases)

        for term in terms:
            term_q = Q()
            for alias in aliases:
                term_q |= Q(**{f"{alias}__contains": term.lower()})
            queryset = queryset.filter(term_q)

        # Bog'langan jadvallar (brand__name ...) takroriy qator bermasligi uchun
        return queryset.distinct()
