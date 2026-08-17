"""
catalog/models.py — 'СтройОптТорг'

Complete catalog models including:
- Task: Productni List (2026-08-16)
- Task: Product Category List (2026-08-17)
- Task: Producti Filtr (2026-08-18) — ATTRIBUTE / PRODUCT_ATTRIBUTE for filtering
- Task: Product detaili (2026-08-19) — PRODUCT_IMAGE / STOCK / attrs_json
- Task: Product Savneniya (2026-08-21) — COMPARE model

Matches the Draw.io ERD: ATTRIBUTE, ATTRIBUTE_VALUE, CATEGORY, BRAND,
PRODUCT, PRODUCT_ATTRIBUTE, PRODUCT_IMAGE, STOCK, COMPARE
"""

from django.db import models
from django.utils import timezone


# =============================================================
# TASK: PRODUCT CATEGORY LIST
# =============================================================
class Category(models.Model):
    """Hierarchical category structure supporting nested children."""
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    sort = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['sort', 'name']

    def __str__(self):
        return self.name

    @property
    def product_count(self):
        return self.products.filter(is_active=True).count()


# =============================================================
# TASK: PRODUCTI FILTR (Attributes for filtering)
# =============================================================
class Brand(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Attribute(models.Model):
    """e.g. 'Power (W)', 'Type', 'Material' — ERD ATTRIBUTE table.
    Without ATTRIBUTE/PRODUCT_ATTRIBUTE the 'Power 8+ and Type'
    filter on 3,457 products cannot be built (your ERD comment)."""
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    unit = models.CharField(max_length=50, blank=True, default='')  # 'W', 'kg', etc.
    type = models.CharField(
        max_length=20,
        default='string',
        choices=[('string', 'String'), ('number', 'Number'), ('boolean', 'Boolean')],
    )
    is_filterable = models.BooleanField(default=True)
    is_comparable = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class CategoryAttribute(models.Model):
    """Which attributes are shown for which category (category-specific filters)."""
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='category_attributes')
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name='category_attributes')
    sort = models.IntegerField(default=0)

    class Meta:
        unique_together = ('category', 'attribute')
        ordering = ['sort']


class AttributeValue(models.Model):
    """Dictionary of attribute values, e.g. named values for 'Type'."""
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name='values')
    value_string = models.CharField(max_length=255, blank=True, null=True)
    value_number = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"{self.attribute.name}: {self.value_string or self.value_number}"


# =============================================================
# TASK: PRODUCTNI LIST + PRODUCT DETAILI
# =============================================================
class Product(models.Model):
    """The core product model. attrs_json is used for fast detail rendering."""
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    article = models.CharField(max_length=100, unique=True)  # SKU
    price = models.DecimalField(max_digits=12, decimal_places=2)
    old_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    attrs_json = models.JSONField(default=dict, blank=True)
    description = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.article} — {self.name}"

    @property
    def discount_percent(self):
        if self.old_price and self.old_price > self.price:
            return int((1 - self.price / self.old_price) * 100)
        return 0


class ProductAttribute(models.Model):
    """Structured product attributes — required for PRODUCTI FILTR.
    Allows range filters (e.g. price/power range) and multi-value filters."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_attributes')
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name='product_attributes')
    value_id = models.ForeignKey(
        AttributeValue,
        on_delete=models.CASCADE,
        related_name='product_attributes',
    )
    value_number = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    class Meta:
        unique_together = ('product', 'attribute')


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    sort = models.IntegerField(default=0)
    is_main = models.BooleanField(default=False)

    class Meta:
        ordering = ['sort']


class Stock(models.Model):
    """Stock level synced from ERP every 15 minutes (per your ERD notes)."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stocks')
    quantity = models.IntegerField(default=0)
    status = models.CharField(max_length=20, default='in_stock')
    synced_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-synced_at']

    def __str__(self):
        return f"{self.product.article}: {self.quantity}"

    @property
    def is_available(self):
        return self.quantity > 0


# =============================================================
# TASK: PRODUCT SAVNENIYA (Product Comparison)
# =============================================================
class Compare(models.Model):
    """Product comparison list.
    - session_key for guest users (per your ERD note)
    - user_id for authenticated users
    - Includes category to ensure comparison within the same category
      (per your ERD note about COMPARE)
    """
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='compares',
    )
    session_key = models.CharField(max_length=64, blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='compares')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='compares')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            # One product per user (or session)
            models.UniqueConstraint(
                fields=['user', 'product'],
                name='unique_user_product_compare',
            ),
            models.UniqueConstraint(
                fields=['session_key', 'product'],
                name='unique_session_product_compare',
            ),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"Compare: {self.product.article}"
