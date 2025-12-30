from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import CustomUser, SystemConfiguration


@admin.register(CustomUser)
class UserAdmin(BaseUserAdmin):
    """Admin interface for customUser model."""
    list_display = ["id", "email", "full_name", "role", "is_active", "is_staff"]
    list_filter = ["role", "is_active", "is_staff"]
    search_fields = ["email", "full_name"]
    ordering = ["email"]
    
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("full_name",)}),
        (_("Permissions"), {
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions"),
        }),
        (_("Role Information"), {"fields": ("role", "work_stream", "school")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined",)}),
    )
    
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "full_name", "password1", "password2", "role"),
        }),
    )


@admin.register(SystemConfiguration)
class SystemConfigurationAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "config_key", "config_value"]
    list_filter = ["school"]
    search_fields = ["config_key", "config_value"]
    ordering = ["school", "config_key"]
