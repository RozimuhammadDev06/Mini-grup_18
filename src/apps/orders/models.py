from django.db import models
from django.conf import settings

class PromoCode(models.Model):
    code = models.CharField(max_length=50, unique=True)
    type = models.CharField(max_length=50) # e.g., 'percent', 'fixed'
    value = models.DecimalField(max_digits=12, decimal_places=2)
    min_order = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    valid_to = models.DateTimeField()
    usage_limit = models.IntegerField(null=True, blank=True)
    used_count = models.IntegerField(default=0)

class DiscountTier(models.Model):
    threshold = models.DecimalField(max_digits=12, decimal_places=2)
    percent = models.IntegerField()
    is_active = models.BooleanField(default=True)

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=255, null=True, blank=True) # For guest checkout
    promo_code = models.ForeignKey(PromoCode, on_delete=models.SET_NULL, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('catalog.Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2) # Current price

class Order(models.Model):
    number = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=50)
    delivery_type = models.CharField(max_length=50)
    address_snapshot = models.JSONField() # Lock in address at time of order
    payment_method = models.CharField(max_length=50)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    cart_discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    promo_discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    delivery_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('catalog.Product', on_delete=models.SET_NULL, null=True)
    name_snapshot = models.CharField(max_length=255) # Lock in name
    article_snapshot = models.CharField(max_length=100) # Lock in article
    price = models.DecimalField(max_digits=12, decimal_places=2) # Lock in price
    quantity = models.PositiveIntegerField()

class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    provider = models.CharField(max_length=100)
    provider_id = models.CharField(max_length=255, blank=True)
    payment_type = models.CharField(max_length=50)
    status = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
