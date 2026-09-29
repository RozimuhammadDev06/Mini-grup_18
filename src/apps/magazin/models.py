from django.conf import settings
from django.db import models
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Promotion(models.Model):
    DISCOUNT_PERCENT = "percent"
    DISCOUNT_FIXED = "fixed"

    DISCOUNT_TYPE_CHOICES = [
        (DISCOUNT_PERCENT, "Percentage"),
        (DISCOUNT_FIXED, "Fixed amount"),
    ]

    title = models.CharField(
        max_length=255,
        verbose_name="Aksiya nomi",
    )

    description = models.TextField(
        blank=True,
        default="",
        verbose_name="Aksiya tavsifi",
    )

    products = models.ManyToManyField(
        "Product",
        blank=True,
        related_name="promotions",
        verbose_name="Aksiyadagi mahsulotlar",
    )

    discount_type = models.CharField(
        max_length=20,
        choices=DISCOUNT_TYPE_CHOICES,
        default=DISCOUNT_PERCENT,
    )

    discount_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    start_date = models.DateTimeField(
        default=timezone.now,
    )

    end_date = models.DateTimeField()

    is_active = models.BooleanField(
        default=True,
    )

    image = models.ImageField(
        upload_to="promotions/",
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Promotion"
        verbose_name_plural = "Promotions"

    def __str__(self):
        return self.title

    def clean(self):
        if self.discount_value <= Decimal("0"):
            raise ValidationError(
                {
                    "discount_value": (
                        "Chegirma qiymati 0 dan katta bo‘lishi kerak."
                    )
                }
            )

        if self.discount_type == self.DISCOUNT_PERCENT:
            if self.discount_value > Decimal("100"):
                raise ValidationError(
                    {
                        "discount_value": (
                            "Foizli chegirma 100 dan katta bo‘lishi mumkin emas."
                        )
                    }
                )

        if self.end_date <= self.start_date:
            raise ValidationError(
                {
                    "end_date": (
                        "Tugash sanasi boshlanish sanasidan keyin bo‘lishi kerak."
                    )
                }
            )

    @property
    def is_current(self):
        now = timezone.now()

        return (
            self.is_active
            and self.start_date <= now <= self.end_date
        )


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
    logo = models.ImageField(
        upload_to="brands/logos/",
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        app_label = "magazin"



class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    article = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    attrs_json = models.JSONField(default=dict, blank=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'magazin'


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=255, null=True, blank=True)
    promo_code_id = models.IntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart {self.id}"

    class Meta:
        app_label = 'magazin'


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
    product = models.ForeignKey(Product,on_delete=models.SET_NULL,related_name='news',null=True,)

    def __str__(self):
        return str(self.product)