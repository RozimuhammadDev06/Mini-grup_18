from django.db import models

from . import limits


class StoreReview(models.Model):
    """Do'kon haqida sharh. Admin tasdiqlaguncha saytda ko'rinmaydi."""

    name = models.CharField("Имя", max_length=limits.NAME_MAX_LENGTH)
    # Faqat admin uchun (javob berish / spam tekshirish), API'da ko'rsatilmaydi
    email = models.EmailField("Email")
    text = models.TextField("Текст отзыва", max_length=limits.TEXT_MAX_LENGTH)
    is_approved = models.BooleanField("Опубликован", default=False, db_index=True)
    ip_address = models.GenericIPAddressField("IP-адрес", null=True, blank=True, editable=False)
    created_at = models.DateTimeField("Дата", auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        verbose_name = "Отзыв о магазине"
        verbose_name_plural = "Отзывы о магазине"

    def __str__(self):
        return f"{self.name}: {self.text[:40]}"


class StoreReviewImage(models.Model):
    review = models.ForeignKey(
        StoreReview,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Отзыв",
    )
    image = models.ImageField("Фото", upload_to="store_reviews/%Y/%m/")
    sort = models.PositiveSmallIntegerField("Порядок", default=0)

    class Meta:
        ordering = ["sort", "id"]
        verbose_name = "Фото"
        verbose_name_plural = "Фото"

    def __str__(self):
        return f"Фото #{self.sort + 1} — {self.review.name}"
