from django.contrib import admin
from .models import Workstream, StaffEvaluation, DepartmentActivityReport


@admin.register(Workstream)
class WorkstreamAdmin(admin.ModelAdmin):
    list_display = ["name", "manager", "capacity", "created_by", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["name", "manager__email"]
    readonly_fields = ["created_at"]


@admin.register(StaffEvaluation)
class StaffEvaluationAdmin(admin.ModelAdmin):
    list_display = ["teacher", "manager", "workstream", "score", "period_start", "period_end", "created_at"]
    list_filter = ["created_at", "workstream", "score"]
    search_fields = ["teacher__email", "manager__email"]
    readonly_fields = ["created_at"]


@admin.register(DepartmentActivityReport)
class DepartmentActivityReportAdmin(admin.ModelAdmin):
    list_display = ["workstream", "manager", "date", "attendance_rate", "generated_at"]
    list_filter = ["date", "workstream", "generated_at"]
    search_fields = ["workstream__name", "manager__email"]
    readonly_fields = ["generated_at"]