from django.contrib import admin
from .models import Guardian, GuardianStudentLink


class GuardianStudentLinkInline(admin.TabularInline):
    model = GuardianStudentLink
    extra = 1
    autocomplete_fields = ["student"]

@admin.register(Guardian)
class GuardianAdmin(admin.ModelAdmin):
    list_display = ["user", "phone_number"]
    search_fields = ["user__email", "user__full_name", "phone_number"]
    ordering = ["user__full_name"]
    autocomplete_fields = ["user"]
    inlines = [GuardianStudentLinkInline]


@admin.register(GuardianStudentLink)
class GuardianStudentLinkAdmin(admin.ModelAdmin):
    list_display = ["guardian", "student", "relationship_type"]
    list_filter = ["relationship_type"]
    search_fields = [
        "guardian__user__email",
        "guardian__user__full_name",
        "student__user__email",
        "student__user__full_name"
    ]
    ordering = ["guardian", "student"]
