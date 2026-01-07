from django.contrib import admin
from .models import Secretary

@admin.register(Secretary)
class SecretaryAdmin(admin.ModelAdmin):
    list_display = ["user", "department", "office_number", "hire_date"]
    list_filter = ["department", "hire_date"]
    search_fields = ["user__email", "user__full_name", "department", "office_number"]
    ordering = ["user__full_name"]
