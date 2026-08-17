from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Review(models.Model):
    """
    A customer's review and rating for a product.
    """

    product = models.ForeignKey(
        "catalog.Product",
        on_delete=models.CASCADE,
        related_name="reviews",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
    )

    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
        help_text="Rating from 1 to 5.",
    )

    comment = models.TextField(
        blank=True,
        help_text="Customer's review.",
    )

    is_published = models.BooleanField(
        default=False,
        help_text="Whether this review is visible to customers.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["product", "is_published"]),
            models.Index(fields=["user"]),
        ]

    def __str__(self):
        return f"{self.product} — {self.rating}/5"


class Wishlist(models.Model):
    """
    Products saved by an authenticated user.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wishlist_items",
    )

    product = models.ForeignKey(
        "catalog.Product",
        on_delete=models.CASCADE,
        related_name="wishlist_items",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"],
                name="unique_user_wishlist_product",
            ),
        ]

        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["product"]),
        ]

    def __str__(self):
        return f"{self.user} → {self.product}"


class Compare(models.Model):
    """
    Products selected for comparison.

    Authenticated users are identified by `user`.
    Guests are identified by `session_key`.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="compare_items",
        null=True,
        blank=True,
    )

    product = models.ForeignKey(
        "catalog.Product",
        on_delete=models.CASCADE,
        related_name="compare_items",
    )

    session_key = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_index=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["session_key"]),
            models.Index(fields=["product"]),
        ]

    def __str__(self):
        if self.user:
            return f"{self.user} → {self.product}"

        return f"Guest ({self.session_key}) → {self.product}"


class Lead(models.Model):
    """
    Contact information submitted by a potential customer.
    """

    name = models.CharField(
        max_length=150,
    )

    email = models.EmailField()

    phone = models.CharField(
        max_length=30,
        blank=True,
    )

    message = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.name} — {self.email}"



from django.db import models
from django.conf import settings

class Wishlist(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='wishlist'
    )
    product = models.ForeignKey(
        'catalog.Product', 
        on_delete=models.CASCADE, 
        related_name='wishlisted_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Prevent a user from adding the same product multiple times
        unique_together = ('user', 'product')
        verbose_name = "Wishlist Item"
        verbose_name_plural = "Wishlist Items"

    def __str__(self):
        return f"{self.user.username} likes {self.product.name}"

# (Keep other engagement models like Review, Compare, Lead here as well)
