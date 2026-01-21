from django.contrib import admin
from .models import WorkStream


@admin.register(WorkStream)
class WorkStreamAdmin(admin.ModelAdmin):
    list_display = ["id", "workstream_name", "manager", "capacity", "is_active"]
    list_filter = ["is_active", "manager"]
    search_fields = ["workstream_name", "description", "manager__email"]
    ordering = ["workstream_name"]
