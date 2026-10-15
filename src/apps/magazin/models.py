from django.conf import settings
from django.db import models
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils import timezone


class Promotion(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    discount_value = models.DecimalField(max_digits=12, decimal_places=2)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        app_label = 'magazin'


class Region(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'magazin'


class Category(models.Model):
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    sort = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'magazin'


class Brand(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    logo = models.ImageField(upload_to="brands/logos/", blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        app_label = "magazin"


class ProductType(models.Model):
    """Mahsulot turi: Перфоратор, Дрель, Смеситель... (katalog filtri uchun)"""

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    class Meta:
        app_label = "magazin"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    product_type = models.ForeignKey(
        ProductType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    article = models.CharField(max_length=100, unique=True)

    material = models.CharField(
        max_length=120,
        blank=True,
        default="",
        db_index=True,
    )
    color = models.CharField(
        max_length=120,
        blank=True,
        default="",
        db_index=True,
    )
    length_mm = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
    width_mm = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
    height_mm = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
    weight_kg = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        null=True,
        blank=True,
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    old_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    stock_quantity = models.PositiveIntegerField(default=0)

    image = models.ImageField(
        upload_to="products/",
        null=True,
        blank=True,
    )

    attrs_json = models.JSONField(
        default=dict,
        blank=True,
    )
    description = models.TextField(
        blank=True,
        default="",
    )
    is_active = models.BooleanField(default=True)
    is_hit = models.BooleanField(
        default=False,
        help_text="Katalogda «ХИТ» belgisi bilan ko'rsatiladi",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    """Mahsulot galereyasi (asosiy rasm — Product.image)"""

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(upload_to="products/gallery/")
    sort = models.PositiveIntegerField(default=0)

    class Meta:
        app_label = "magazin"
        ordering = ["sort", "id"]

    def __str__(self):
        return f"{self.product} — {self.sort}"


class Cart(models.Model):
    user = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name="carts",
    null=True,
    blank=True,
)


    session_key = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )
    promo_code_id = models.IntegerField(
        null=True,
        blank=True,
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart {self.id}"



class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"

    class Meta:
        app_label = 'magazin'


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=50, default='pending')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.number}"

    class Meta:
        app_label = 'magazin'


class News(models.Model):
    class Rubric(models.TextChoices):
        NEWS = "news", "Новости"
        ARTICLES = "articles", "Статьи"
        TIPS = "tips", "Советы"
        REVIEWS = "reviews", "Обзоры"

    title = models.CharField(max_length=255, default="")
    slug = models.SlugField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        allow_unicode=True,
        help_text="Bo'sh qoldirilsa sarlavhadan avtomatik yaratiladi",
    )
    rubric = models.CharField(
        max_length=20,
        choices=Rubric.choices,
        default=Rubric.NEWS,
        db_index=True,
    )
    excerpt = models.TextField(blank=True, default="")
    content = models.TextField(blank=True, default="")
    image = models.ImageField(upload_to="news/", null=True, blank=True)
    # Yangilik biror mahsulot haqida bo'lsa (ixtiyoriy)
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        related_name="news",
        null=True,
        blank=True,
    )
    is_published = models.BooleanField(default=True, db_index=True)
    published_at = models.DateTimeField(default=timezone.now, db_index=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_at", "-id"]
        verbose_name_plural = "news"

    def __str__(self):
        return self.title or f"News #{self.pk}"

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            self.slug = self._unique_slug()
        super().save(*args, **kwargs)

    def _unique_slug(self):
        from django.utils.text import slugify

        base = slugify(self.title, allow_unicode=True)[:240] or "news"
        slug, n = base, 2
        while News.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug, n = f"{base}-{n}", n + 1
        return slug


class Review(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="product_reviews",
    )
    rating = models.PositiveSmallIntegerField()
    text = models.TextField(blank=True, default="")
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["product", "user"],
                name="one_review_per_user_product",
            ),
        ]




