from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for custom User model."""
    list_display = ["email", "username", "first_name", "last_name", "role", "is_active", "date_joined"]
    list_filter = ["role", "is_active", "date_joined"]
    search_fields = ["email", "username", "first_name", "last_name"]
    ordering = ["-date_joined"]
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Role Information", {"fields": ("role",)}),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Role Information", {"fields": ("role",)}),
    )