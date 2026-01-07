from django.contrib import admin
from .models import ManagerProfile, StaffEvaluation


@admin.register(ManagerProfile)
class ManagerProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "hire_date", "department", "office_location"]
    list_filter = ["department", "hire_date"]
    search_fields = ["user__email", "user__full_name", "department"]
    ordering = ["user__full_name"]


@admin.register(StaffEvaluation)
class StaffEvaluationAdmin(admin.ModelAdmin):
    list_display = ["id", "reviewer", "reviewee", "evaluation_date", "rating_score"]
    list_filter = ["evaluation_date", "rating_score"]
    search_fields = ["reviewer__email", "reviewee__email", "comments"]
    ordering = ["-evaluation_date"]
