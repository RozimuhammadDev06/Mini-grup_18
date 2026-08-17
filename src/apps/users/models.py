import uuid
import random
import secrets
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from datetime import timedelta
from rest_framework_simplejwt.tokens import RefreshToken


class CustomUserManager(models.Manager):
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user with email and password."""
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Single unified User model:
    - UUID primary key
    - Email is the login field (USERNAME_FIELD)
    - Supports JWT tokens, email verification, and password reset
    """
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True)
    email = models.EmailField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    phone_number = models.CharField(max_length=13, null=True, blank=True)
    telegram_id = models.CharField(max_length=50, null=True, blank=True)
    language = models.CharField(max_length=2, default='uz')

    is_active = models.BooleanField(default=False)  # activated after email verification
    is_staff = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name']

    objects = CustomUserManager()

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return self.email

    def generate_jwt_token(self):
        """Returns access and refresh JWT tokens for this user."""
        refresh = RefreshToken.for_user(self)
        return {
            'refresh_token': str(refresh),
            'access_token': str(refresh.access_token),
        }

    # Backwards-compatible alias expected by some views
    def generate_jwt_token_alias(self):
        return self.generate_jwt_token()

    # --- Email verification helpers (kept from your original) ---
    def set_verification_code(self):
        """Generates a 6-digit code and sets expiration to 10 minutes."""
        self.verification_code = f"{random.randint(100000, 999999)}"
        self.verification_code_expires = timezone.now() + timedelta(minutes=10)
        self.save(update_fields=['verification_code', 'verification_code_expires'])

    def is_code_valid(self, code):
        """Checks if the code matches and hasn't expired."""
        return bool(
            self.verification_code == code
            and self.verification_code_expires is not None
            and self.verification_code_expires > timezone.now()
        )

    # --- Password reset helper (kept from your original) ---
    def set_password_reset_token(self):
        self.password_reset_token = secrets.token_urlsafe(32)
        self.save(update_fields=['password_reset_token'])
        return self.password_reset_token


# =============================================================
# OTP / Verification log models
# =============================================================

class UserOTPVerifications(models.Model):
    """
    Stores email/phone verification OTP codes.
    Used for registration verification AND forget-password flows.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    expired_at = models.DateTimeField()
    attapts = models.IntegerField(default=0)
    for_forget_password = models.BooleanField(default=False)
    for_forget_password_verified = models.BooleanField(default=False)
    resend_attapts = models.IntegerField(default=0)
    error_expired_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "User OTP Verification"
        verbose_name_plural = "User OTP Verifications"

    def __str__(self):
        return f"{self.user} | {self.code}"

    def generate_code(self):
        """Generates a new 6-digit OTP valid for 3 minutes."""
        otp = random.randint(100000, 999999)
        self.code = str(otp)
        self.expired_at = timezone.now() + timedelta(minutes=3)
        self.save()
        return otp

    def is_code_expired(self):
        """Returns the expiry timestamp if still valid, otherwise False."""
        if self.expired_at >= timezone.now():
            return self.expired_at.timestamp()
        return False


class UserOTPIDVerifications(models.Model):
    """
    Stores ID-based (UUID) verification tokens, e.g. for email reset links.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.UUIDField(default=uuid.uuid4)
    expired_at = models.DateTimeField()
    attapts = models.IntegerField(default=0)
    error_expired_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "User OTP ID Verification"
        verbose_name_plural = "User OTP ID Verifications"

    def __str__(self):
        return f"{self.user} | {self.code}"

    def is_code_expired(self):
        """Returns the expiry timestamp if still valid, otherwise False."""
        if self.expired_at >= timezone.now():
            return self.expired_at.timestamp()
        return False


class ChangePasswordLogs(models.Model):
    """
    Logs password change attempts.
    NOTE: old_password and new_password store HASHED passwords only
    (never store plaintext passwords for security).
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    old_password = models.CharField(max_length=255, blank=True)
    new_password = models.CharField(max_length=255, blank=True)
    expired_at = models.DateTimeField(null=True, blank=True)
    attapts = models.IntegerField(default=0)
    error_expired_at = models.DateTimeField(null=True, blank=True)
    is_changed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Change Password Log"
        verbose_name_plural = "Change Password Logs"

    def __str__(self):
        return f"{self.user} | {self.attapts}"

    def is_expired(self):
        if self.expired_at and self.expired_at >= timezone.now():
            return self.expired_at
        return False

    def is_blocked(self):
        if self.error_expired_at and self.error_expired_at >= timezone.now():
            return self.error_expired_at
        return False


class ChangeEmailLogs(models.Model):
    """
    Logs email change attempts with their own verification code.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    old_email = models.CharField(max_length=150, default="")
    new_email = models.CharField(max_length=150, default="")
    expired_at = models.DateTimeField(null=True, blank=True)
    attapts = models.IntegerField(default=0)
    resend_attapts = models.IntegerField(default=0)
    error_expired_at = models.DateTimeField(null=True, blank=True)
    is_changed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Change Email Log"
        verbose_name_plural = "Change Email Logs"

    def __str__(self):
        return f"{self.user} | {self.attapts}"

    def is_expired(self):
        if self.expired_at and self.expired_at >= timezone.now():
            return self.expired_at
        return False

    def generate_code(self):
        """Generates a new 6-digit code valid for 3 minutes."""
        otp = random.randint(100000, 999999)
        self.code = str(otp)
        self.expired_at = timezone.now() + timedelta(minutes=3)
        self.save()
        return otp

    def is_blocked(self):
        if self.error_expired_at and self.error_expired_at >= timezone.now():
            return self.error_expired_at
        return False


# =============================================================
# Geography models
# =============================================================

class Region(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class City(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='cities')
    name = models.CharField(max_length=255)
    delivery_zone_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name


class DeliveryZone(models.Model):
    name = models.CharField(max_length=255)
    base_cost = models.DecimalField(max_digits=12, decimal_places=2)
    per_kg = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return self.name


# =============================================================
# Address model
# =============================================================

class Address(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='addresses'
    )
    company_name = models.CharField(max_length=255, blank=True, null=True)
    region = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    street = models.CharField(max_length=255)
    house = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name = "User Address"
        verbose_name_plural = "User Addresses"

    def save(self, *args, **kwargs):
        """If set as default, unset other default addresses for this user."""
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email} - {self.city}, {self.street}"
