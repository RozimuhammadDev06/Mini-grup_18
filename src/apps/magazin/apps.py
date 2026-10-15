from django.apps import AppConfig


class MagazinConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.magazin"

    def ready(self):
        from django.db.backends.signals import connection_created

        from .search import register_sqlite_functions

        # Kirill harflari bilan qidiruv uchun (faqat yangi funksiya qo'shadi)
        connection_created.connect(register_sqlite_functions)
