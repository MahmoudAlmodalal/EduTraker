from django.conf import settings
from django.db import models


class Student(models.Model):
    """
    Student profile linked to User.
    """
    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("graduated", "Graduated"),
        ("transferred", "Transferred"),
        ("suspended", "Suspended"),
    ]
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="student_profile",
        help_text="User account for this student"
    )
    school = models.ForeignKey(
        "manager.School",
        on_delete=models.CASCADE,
        related_name="students",
        help_text="School this student belongs to"
    )
    grade = models.ForeignKey(
        "manager.Grade",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students",
        help_text="Current grade level"
    )
    date_of_birth = models.DateField(help_text="Student date of birth")
    admission_date = models.DateField(help_text="Date of admission")
    current_status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default="active",
        help_text="Current enrollment status"
    )
    address = models.TextField(null=True, blank=True, help_text="Student address")
    medical_notes = models.TextField(null=True, blank=True, help_text="Medical information/notes")
    
    class Meta:
        db_table = "student"
        verbose_name = "Student"
        verbose_name_plural = "Students"
        ordering = ["user__full_name"]
    
    def __str__(self):
        return f"{self.user.full_name} ({self.user.email})"


class StudentEnrollment(models.Model):
    """
    Student enrollment in a classroom for an academic year.
    """
    STATUS_CHOICES = [
        ("enrolled", "Enrolled"),
        ("completed", "Completed"),
        ("withdrawn", "Withdrawn"),
        ("transferred", "Transferred"),
    ]
    
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="enrollments",
        help_text="Enrolled student"
    )
    class_room = models.ForeignKey(
        "teacher.ClassRoom",
        on_delete=models.CASCADE,
        related_name="enrollments",
        help_text="Classroom student is enrolled in"
    )
    academic_year = models.ForeignKey(
        "manager.AcademicYear",
        on_delete=models.CASCADE,
        related_name="enrollments",
        help_text="Academic year for this enrollment"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        null=True,
        blank=True,
        help_text="Enrollment status"
    )
    
    class Meta:
        db_table = "student_enrollment"
        verbose_name = "Student Enrollment"
        verbose_name_plural = "Student Enrollments"
        constraints = [
            models.UniqueConstraint(
                fields=["student", "class_room"],
                name="unique_student_classroom"
            )
        ]
        ordering = ["academic_year", "class_room", "student"]
    
    def __str__(self):
        return f"{self.student.user.full_name} - {self.class_room.classroom_name} ({self.academic_year.academic_year_code})"
