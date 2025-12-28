from django.contrib import admin
from .models import School, AcademicYear, Grade, Course, ClassRoom, Secretary, StaffEvaluation


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


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ["id", "course_code", "name", "school", "grade"]
    list_filter = ["school", "grade"]
    search_fields = ["course_code", "name", "school__school_name"]
    ordering = ["course_code"]


@admin.register(ClassRoom)
class ClassRoomAdmin(admin.ModelAdmin):
    list_display = ["id", "classroom_name", "school", "academic_year", "grade", "homeroom_teacher"]
    list_filter = ["school", "academic_year", "grade"]
    search_fields = ["classroom_name", "school__school_name", "homeroom_teacher__user__email"]
    ordering = ["academic_year", "grade", "classroom_name"]


@admin.register(Secretary)
class SecretaryAdmin(admin.ModelAdmin):
    list_display = ["user", "department", "office_number", "hire_date"]
    list_filter = ["department", "hire_date"]
    search_fields = ["user__email", "user__full_name", "department", "office_number"]
    ordering = ["user__full_name"]


@admin.register(StaffEvaluation)
class StaffEvaluationAdmin(admin.ModelAdmin):
    list_display = ["id", "reviewer", "reviewee", "evaluation_date", "rating_score"]
    list_filter = ["evaluation_date", "rating_score"]
    search_fields = ["reviewer__email", "reviewee__email", "comments"]
    ordering = ["-evaluation_date"]
