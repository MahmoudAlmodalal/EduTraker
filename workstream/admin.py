from django.contrib import admin
from .models import WorkStream


@admin.register(WorkStream)
class WorkStreamAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "manager", "max_user", "is_active"]
    list_filter = ["is_active", "manager"]
    search_fields = ["name", "description", "manager__email"]
    ordering = ["name"]
