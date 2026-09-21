from django.contrib.auth.models import AbstractUser
from django.db import models





class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

    class Meta:
        app_label = 'users'

class ChangePasswordLogs(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    attapts = models.PositiveIntegerField(default=0)
    is_changed = models.BooleanField(default=False)
    expired_at = models.DateTimeField(null=True, blank=True)
    error_expired_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Password log: {self.user.username}"

    class Meta:
        app_label = 'users'


class ChangeEmailLogs(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    old_email = models.EmailField()
    new_email = models.EmailField()
    code = models.CharField(max_length=10)
    attapts = models.PositiveIntegerField(default=0)
    resend_attapts = models.PositiveIntegerField(default=0)
    is_changed = models.BooleanField(default=False)
    expired_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Email change: {self.old_email} -> {self.new_email}"

    class Meta:
        app_label = 'users'

class Region(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        app_label = "users"


class DeliveryZone(models.Model):
    name = models.CharField(max_length=255)
    base_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    per_kg = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.name

    class Meta:
        app_label = "users"


class City(models.Model):
    region = models.ForeignKey(
        Region,
        on_delete=models.CASCADE,
        related_name="cities",
    )
    name = models.CharField(max_length=255)
    delivery_zone = models.ForeignKey(
        DeliveryZone,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cities",
    )

    def __str__(self):
        return self.name

    class Meta:
        app_label = "users"


class Address(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="addresses",
    )
    company_name = models.CharField(max_length=255, blank=True, null=True)
    region = models.ForeignKey(
        Region,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    city = models.ForeignKey(
        City,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    street = models.CharField(max_length=255, blank=True, null=True)
    house = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Address {self.id} for {self.user.username}"

    class Meta:
        app_label = "users"
