from django.contrib import admin
from django.utils.html import format_html

from .models import StoreReview, StoreReviewImage


class StoreReviewImageInline(admin.TabularInline):
    model = StoreReviewImage
    extra = 0
    fields = ("preview", "image", "sort")
    readonly_fields = ("preview",)

    @admin.display(description="Превью")
    def preview(self, obj):
        if not obj.image:
            return "—"
        return format_html(
            '<a href="{0}" target="_blank"><img src="{0}" style="height:80px;border-radius:4px"></a>',
            obj.image.url,
        )


@admin.register(StoreReview)
class StoreReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "short_text", "photos_count", "is_approved", "created_at")
    list_display_links = ("id", "name")
    list_editable = ("is_approved",)
    list_filter = ("is_approved", "created_at")
    search_fields = ("name", "email", "text")
    readonly_fields = ("ip_address", "created_at")
    date_hierarchy = "created_at"
    inlines = [StoreReviewImageInline]
    actions = ["approve", "unapprove"]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("images")

    @admin.display(description="Текст")
    def short_text(self, obj):
        return obj.text[:80] + ("…" if len(obj.text) > 80 else "")

    @admin.display(description="Фото")
    def photos_count(self, obj):
        return len(obj.images.all())

    @admin.action(description="Опубликовать выбранные отзывы")
    def approve(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"Опубликовано отзывов: {updated}")

    @admin.action(description="Скрыть выбранные отзывы")
    def unapprove(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f"Скрыто отзывов: {updated}")
