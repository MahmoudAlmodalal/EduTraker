from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["title", "sender", "scope_type", "scope_id", "created_at"]
    list_filter = ["scope_type", "created_at"]
    search_fields = ["title", "body", "sender__email"]
    ordering = ["-created_at"]
    readonly_fields = ["created_at"]
