from django.contrib import admin
from .models import UserMessage


@admin.register(UserMessage)
class UserMessageAdmin(admin.ModelAdmin):
    list_display = ["sender", "receiver", "subject", "sent_at", "is_read"]
    list_filter = ["is_read", "sent_at"]
    search_fields = ["sender__email", "receiver__email", "subject", "body"]
    ordering = ["-sent_at"]
    readonly_fields = ["sent_at"]
