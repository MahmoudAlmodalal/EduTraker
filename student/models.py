from django.db import models


class Student(models.Model):
    """
    Student profile linked to User.
    Schema: Students table
    Note: school_id and grade_id removed - use user.school and student_enrollments
    """
    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("graduated", "Graduated"),
        ("transferred", "Transferred"),
        ("suspended", "Suspended"),
    ]
    
    user = models.OneToOneField(
        'accounts.CustomUser',
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="student_profile",
        help_text="User account for this student"
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "students"
        verbose_name = "Student"
        verbose_name_plural = "Students"
        ordering = ["user__full_name"]
        indexes = [
            models.Index(fields=["current_status"], name="idx_students_status"),
            models.Index(fields=["date_of_birth"], name="idx_students_dob"),
        ]
    
    def __str__(self):
        return f"{self.user.full_name} ({self.user.email})"


class StudentEnrollment(models.Model):
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
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
