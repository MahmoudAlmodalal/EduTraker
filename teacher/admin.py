from django.contrib import admin
from .models import (
    Teacher, CourseAllocation,
    Assignment, LearningMaterial, Mark, Attendance
)


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ["user", "specialization", "employment_status", "hire_date"]
    list_filter = ["employment_status", "hire_date"]
    search_fields = ["user__email", "user__full_name", "specialization"]
    ordering = ["user__full_name"]


@admin.register(CourseAllocation)
class CourseAllocationAdmin(admin.ModelAdmin):
    list_display = ["course", "class_room", "teacher", "academic_year", "is_active"]
    list_filter = ["academic_year", "is_active", "course", "class_room", "teacher"]
    search_fields = ["course__name", "class_room__classroom_name", "teacher__user__email"]
    ordering = ["course", "class_room"]


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ["assignment_code", "title", "course_allocation", "created_by", "exam_type", "due_date", "full_mark", "is_published"]
    list_filter = ["exam_type", "is_published", "due_date", "created_by"]
    search_fields = ["assignment_code", "title", "created_by__user__email"]
    ordering = ["-due_date", "title"]


@admin.register(LearningMaterial)
class LearningMaterialAdmin(admin.ModelAdmin):
    list_display = ["material_code", "title", "course", "classroom", "academic_year", "uploaded_by", "is_active"]
    list_filter = ["academic_year", "is_active", "course", "classroom"]
    search_fields = ["material_code", "title", "course__name", "uploaded_by__email"]
    ordering = ["-academic_year", "course", "title"]


@admin.register(Mark)
class MarkAdmin(admin.ModelAdmin):
    list_display = ["student", "assignment", "score", "graded_by", "graded_at"]
    list_filter = ["assignment", "assignment__exam_type"]
    search_fields = ["student__user__email", "student__user__full_name", "assignment__title"]
    ordering = ["-assignment__due_date", "student"]


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ["student", "course_allocation", "date", "status", "recorded_by"]
    list_filter = ["status", "date", "course_allocation__course", "course_allocation__class_room"]
    search_fields = ["student__user__email", "student__user__full_name", "course_allocation__course__name"]
    ordering = ["-date", "student"]
