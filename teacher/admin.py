from django.contrib import admin
from .models import (
    Course, Teacher, ClassRoom, CourseAllocation,
    Assignment, LearningMaterial, Mark, Attendance
)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ["course_code", "name", "school", "grade"]
    list_filter = ["school", "grade"]
    search_fields = ["course_code", "name", "school__school_name"]
    ordering = ["course_code"]


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ["user", "specialization", "employment_status", "hire_date"]
    list_filter = ["employment_status", "hire_date"]
    search_fields = ["user__email", "user__full_name", "specialization"]
    ordering = ["user__full_name"]


@admin.register(ClassRoom)
class ClassRoomAdmin(admin.ModelAdmin):
    list_display = ["classroom_name", "school", "academic_year", "grade", "homeroom_teacher"]
    list_filter = ["school", "academic_year", "grade"]
    search_fields = ["classroom_name", "school__school_name", "homeroom_teacher__user__email"]
    ordering = ["academic_year", "grade", "classroom_name"]


@admin.register(CourseAllocation)
class CourseAllocationAdmin(admin.ModelAdmin):
    list_display = ["course", "class_room", "teacher"]
    list_filter = ["course", "class_room", "teacher"]
    search_fields = ["course__name", "class_room__classroom_name", "teacher__user__email"]
    ordering = ["course", "class_room"]
    autocomplete_fields = ["course", "class_room", "teacher"]


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ["assignment_code", "title", "created_by", "exam_type", "due_date", "full_mark"]
    list_filter = ["exam_type", "due_date", "created_by"]
    search_fields = ["assignment_code", "title", "created_by__user__email"]
    ordering = ["-due_date", "title"]


@admin.register(LearningMaterial)
class LearningMaterialAdmin(admin.ModelAdmin):
    list_display = ["material_code", "title", "course", "classroom", "academic_year", "uploaded_by"]
    list_filter = ["academic_year", "course", "classroom"]
    search_fields = ["material_code", "title", "course__name", "uploaded_by__email"]
    ordering = ["-academic_year", "course", "title"]


@admin.register(Mark)
class MarkAdmin(admin.ModelAdmin):
    list_display = ["student", "assignment", "score"]
    list_filter = ["assignment", "assignment__exam_type"]
    search_fields = ["student__user__email", "student__user__full_name", "assignment__title"]
    ordering = ["-assignment__due_date", "student"]


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ["student", "course", "class_room", "date", "status"]
    list_filter = ["status", "date", "course", "class_room"]
    search_fields = ["student__user__email", "student__user__full_name", "course__name"]
    ordering = ["-date", "student"]
