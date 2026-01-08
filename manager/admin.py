from django.contrib import admin

from .models import StaffEvaluation

@admin.register(StaffEvaluation)
class StaffEvaluationAdmin(admin.ModelAdmin):
    list_display = ["id", "reviewer", "reviewee", "evaluation_date", "rating_score"]
    list_filter = ["evaluation_date", "rating_score"]
    search_fields = ["reviewer__email", "reviewee__email", "comments"]
    ordering = ["-evaluation_date"]
