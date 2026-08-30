from django.contrib.auth.models import AbstractUser
from django.db import models

# Import Region model directly to avoid unresolved string references during checks
try:
    from apps.magazin.models import Region
except Exception:
    Region = None


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    region = models.ForeignKey(Region or 'magazin.Region', on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

    class Meta:
        app_label = 'users'


class UserOTPVerifications(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=10)
    attapts = models.PositiveIntegerField(default=0)
    resend_attapts = models.PositiveIntegerField(default=0)
    for_forget_password = models.BooleanField(default=False)
    for_forget_password_verified = models.BooleanField(default=False)
    expired_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OTP for {self.user.username}"

    class Meta:
        app_label = 'users'


class UserOTPIDVerifications(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=10)
    attapts = models.PositiveIntegerField(default=0)
    expired_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OTP ID for {self.user.username}"

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
        app_label = 'users'


class City(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    delivery_zone = models.ForeignKey('DeliveryZone', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'users'


class DeliveryZone(models.Model):
    name = models.CharField(max_length=255)
    base_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    per_kg = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'users'


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)
    street = models.CharField(max_length=255, blank=True, null=True)
    house = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Address {self.id} for {self.user.username}"

    class Meta:
        app_label = 'users'
