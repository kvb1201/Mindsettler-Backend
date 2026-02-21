from django.contrib import admin
from .models import AppUser


@admin.register(AppUser)
class AppUserAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "email",
        "phone",
        "is_verified",
        "created_at",
    )

    search_fields = (
        "email",
        "full_name",
        "phone",
    )

    list_filter = (
        "is_verified",
        "created_at",
    )

    ordering = ("-created_at",)