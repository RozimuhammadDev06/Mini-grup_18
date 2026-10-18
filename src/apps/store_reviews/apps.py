from django.apps import AppConfig


class StoreReviewsConfig(AppConfig):
    """Do'kon haqidagi sharhlar ("Отзывы" sahifasi). Mahsulot sharhlari — apps.magazin.Review"""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.store_reviews"
    verbose_name = "Отзывы о магазине"
