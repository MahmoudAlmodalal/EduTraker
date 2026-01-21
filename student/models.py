from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from accounts.models import SoftDeleteModel


class Student(SoftDeleteModel):
    """
    Student profile linked to User.
    Schema: Students table (maps to SRS StudentProfile)
    """
    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("graduated", "Graduated"),
        ("transferred", "Transferred"),
        ("withdrawn", "Withdrawn"),
    ]
    
    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    ]
    
    user = models.OneToOneField(
        'accounts.CustomUser',
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="student_profile",
        help_text="User account for this student"
    )
    student_id = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        help_text="Student ID number"
    )
    date_of_birth = models.DateField(help_text="Student date of birth")
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        null=True,
        blank=True,
        help_text="Student gender"
    )
    grade = models.ForeignKey(
        'school.Grade',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students",
        help_text="Current grade level"
    )
    grade_level = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        help_text="Current grade level (integer fallback)"
    )
    admission_date = models.DateField(help_text="Date of admission")
    enrollment_status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default="active",
        help_text="Current enrollment status"
    )
    # Keep current_status for backwards compatibility, will be deprecated
    current_status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default="active",
        help_text="Current enrollment status (deprecated, use enrollment_status)"
    )
    # Academic tracking
    current_gpa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Current GPA"
    )
    total_absences = models.IntegerField(
        default=0,
        help_text="Total absences count"
    )
    # Personal information
    address = models.TextField(null=True, blank=True, help_text="Student address")
    national_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="National ID number"
    )
    emergency_contact = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Emergency contact info"
    )
    medical_notes = models.TextField(null=True, blank=True, help_text="Medical information/notes")
    
    class Meta:
        db_table = "students"
        verbose_name = "Student"
        verbose_name_plural = "Students"
        ordering = ["user__full_name"]
        indexes = [
            models.Index(fields=["enrollment_status"], name="idx_students_enrollment_status"),
            models.Index(fields=["date_of_birth"], name="idx_students_dob"),
            models.Index(fields=["student_id"], name="idx_students_student_id"),
        ]
    
    def __str__(self):
        return f"{self.user.full_name} ({self.user.email})"


class StudentEnrollment(SoftDeleteModel):
    """
    Student enrollment in a classroom for an academic year.
    Schema: Student_enrollments table
    """
    STATUS_CHOICES = [
        ("active", "Active"),
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
        'school.ClassRoom',
        on_delete=models.CASCADE,
        related_name="enrollments",
        help_text="Classroom student is enrolled in"
    )
    academic_year = models.ForeignKey(
        'school.AcademicYear',
        on_delete=models.CASCADE,
        related_name="enrollments",
        help_text="Academic year for this enrollment"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active",
        help_text="Enrollment status"
    )
    enrollment_date = models.DateField(null=True, blank=True, help_text="Date of enrollment")
    completion_date = models.DateField(null=True, blank=True, help_text="Date of completion")
    
    class Meta:
        db_table = "student_enrollments"
        verbose_name = "Student Enrollment"
        verbose_name_plural = "Student Enrollments"
        constraints = [
            models.UniqueConstraint(
                fields=["student", "class_room", "academic_year"],
                name="unique_student_classroom_year"
            )
        ]
        ordering = ["academic_year", "class_room", "student"]
        indexes = [
            models.Index(fields=["status"], name="idx_enrollment_status"),
            models.Index(fields=["academic_year"], name="idx_enrollment_year"),
        ]
    
    def __str__(self):
        return f"{self.student.user.full_name} - {self.class_room.classroom_name} ({self.academic_year.academic_year_code})"
