from django.contrib import admin
from .models import SystemConfiguration, WorkStream, School, AcademicYear, Grade, StaffEvaluation


@admin.register(SystemConfiguration)
class SystemConfigurationAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "config_key", "config_value"]
    list_filter = ["school"]
    search_fields = ["config_key", "config_value"]
    ordering = ["school", "config_key"]


@admin.register(WorkStream)
class WorkStreamAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "manager", "max_user", "is_active"]
    list_filter = ["is_active", "manager"]
    search_fields = ["name", "description", "manager__email"]
    ordering = ["name"]


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ["id", "school_name", "work_stream", "manager"]
    list_filter = ["work_stream", "manager"]
    search_fields = ["school_name", "work_stream__name"]
    ordering = ["school_name"]


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ["id", "academic_year_code", "school", "start_date", "end_date"]
    list_filter = ["school", "start_date"]
    search_fields = ["academic_year_code", "school__school_name"]
    ordering = ["-academic_year_code"]


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "numeric_level", "min_age", "max_age"]
    list_filter = ["numeric_level"]
    search_fields = ["name"]
    ordering = ["numeric_level"]


@admin.register(StaffEvaluation)
class StaffEvaluationAdmin(admin.ModelAdmin):
    list_display = ["id", "reviewer", "reviewee", "evaluation_date", "rating_score"]
    list_filter = ["evaluation_date", "rating_score"]
    search_fields = ["reviewer__email", "reviewee__email", "comments"]
    ordering = ["-evaluation_date"]
