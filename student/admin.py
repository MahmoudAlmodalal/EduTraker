from django.contrib import admin
from .models import Student, StudentEnrollment


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ["user", "school", "grade", "current_status", "admission_date"]
    list_filter = ["current_status", "school", "grade"]
    search_fields = ["user__email", "user__full_name", "school__school_name"]
    ordering = ["user__full_name"]


@admin.register(StudentEnrollment)
class StudentEnrollmentAdmin(admin.ModelAdmin):
    list_display = ["student", "class_room", "academic_year", "status"]
    list_filter = ["status", "academic_year", "class_room"]
    search_fields = ["student__user__email", "student__user__full_name", "class_room__classroom_name"]
    ordering = ["academic_year", "class_room", "student"]
