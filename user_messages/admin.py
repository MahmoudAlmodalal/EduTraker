from django.contrib import admin
from .models import Message, MessageReceipt


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ["sender", "subject", "sent_at", "is_draft"]
    list_filter = ["is_draft", "sent_at"]
    search_fields = ["sender__email", "subject", "body"]
    ordering = ["-sent_at"]
    readonly_fields = ["sent_at", "thread_id"]


@admin.register(MessageReceipt)
class MessageReceiptAdmin(admin.ModelAdmin):
    list_display = ["message", "recipient", "is_read", "read_at"]
    list_filter = ["is_read"]
    search_fields = ["recipient__email", "message__subject"]
