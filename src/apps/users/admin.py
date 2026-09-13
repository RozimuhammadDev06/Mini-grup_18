from django.contrib import admin

from apps.users.models import (
    Address,
    ChangeEmailLogs,
    ChangePasswordLogs,
    City,
    DeliveryZone,
    Region,
    User,
    UserOTPIDVerifications,
    UserOTPVerifications,
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "full_name", "phone", "is_active")
    search_fields = ("username", "email", "full_name", "phone")
    list_filter = ("is_active", "is_staff")


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(DeliveryZone)
class DeliveryZoneAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "base_cost", "per_kg")
    search_fields = ("name",)


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "region", "delivery_zone")
    list_filter = ("region", "delivery_zone")
    search_fields = ("name",)


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "company_name",
        "region",
        "city",
        "phone",
        "is_default",
    )
    list_filter = ("is_default", "region", "city")
    search_fields = ("user__username", "user__email", "company_name", "phone")


@admin.register(UserOTPVerifications)
class UserOTPVerificationsAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "code", "expired_at", "created_at")
    search_fields = ("user__username", "user__email", "code")


@admin.register(UserOTPIDVerifications)
class UserOTPIDVerificationsAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "code", "expired_at", "created_at")
    search_fields = ("user__username", "user__email", "code")


@admin.register(ChangePasswordLogs)
class ChangePasswordLogsAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "attapts", "is_changed", "expired_at")
    search_fields = ("user__username", "user__email")


@admin.register(ChangeEmailLogs)
class ChangeEmailLogsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "old_email",
        "new_email",
        "attapts",
        "is_changed",
        "created_at",
    )
    search_fields = (
        "user__username",
        "user__email",
        "old_email",
        "new_email",
    )
