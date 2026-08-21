"""
Catalog API views.

The actual catalog ViewSets are implemented in
api.user.views.catalog and re-exported here so that
apps.catalog.urls can use them.
"""

from api.user.views.catalog import (
    CategoryViewSet,
    ProductViewSet,
    CompareViewSet,
)

__all__ = [
    "CategoryViewSet",
    "ProductViewSet",
    "CompareViewSet",
]