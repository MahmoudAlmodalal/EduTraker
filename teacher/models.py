from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Teacher(models.Model):
    """
    Teacher profile linked to User.
    Schema: Teachers table
    """
    EMPLOYMENT_STATUS_CHOICES = [
        ("full_time", "Full Time"),
        ("part_time", "Part Time"),
        ("contract", "Contract"),
        ("substitute", "Substitute"),
    ]
    
    user = models.OneToOneField(
        'accounts.CustomUser',
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="teacher_profile",
        help_text="User account for this teacher"
    )
    specialization = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Teaching specialization"
    )
    hire_date = models.DateField(help_text="Date of hire")
    employment_status = models.CharField(
        max_length=50,
        choices=EMPLOYMENT_STATUS_CHOICES,
        help_text="Employment status"
    )
    highest_degree = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Highest educational degree"
    )
    years_of_experience = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Years of teaching experience"
    )
    office_location = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Office location"
    )
    
    class Meta:
        db_table = "teachers"
        verbose_name = "Teacher"
        verbose_name_plural = "Teachers"
        ordering = ["user__full_name"]
    
    def __str__(self):
        return f"{self.user.full_name} ({self.user.email})"


class CourseAllocation(models.Model):
    """
    Allocation of a course to a classroom with a teacher.
    Schema: Course_Allocations table
    """
    course = models.ForeignKey(
        'manager.Course',
        on_delete=models.CASCADE,
        related_name="allocations",
        help_text="Course being allocated"
    )
    class_room = models.ForeignKey(
        'manager.ClassRoom',
        on_delete=models.CASCADE,
        related_name="course_allocations",
        help_text="Classroom where course is taught"
    )
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="course_allocations",
        help_text="Teacher assigned to teach this course"
    )
    
    class Meta:
        db_table = "course_allocations"
        verbose_name = "Course Allocation"
        verbose_name_plural = "Course Allocations"
        constraints = [
            models.UniqueConstraint(
                fields=["course", "class_room", "teacher"],
                name="unique_course_classroom_teacher"
            )
        ]
        ordering = ["course", "class_room"]
    
    def __str__(self):
        return f"{self.course.name} - {self.class_room.classroom_name} ({self.teacher.user.full_name})"


class Assignment(models.Model):
    """
    Assignment or exam created by a teacher.
    Schema: Assignments table
    """
    EXAM_TYPE_CHOICES = [
        ("assignment", "Assignment"),
        ("quiz", "Quiz"),
        ("midterm", "Midterm Exam"),
        ("final", "Final Exam"),
        ("project", "Project"),
    ]
    
    assignment_code = models.CharField(
        max_length=50,
        help_text="Assignment code"
    )
    created_by = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="assignments",
        help_text="Teacher who created this assignment"
    )
    title = models.CharField(max_length=150, help_text="Assignment title")
    description = models.TextField(null=True, blank=True, help_text="Assignment description")
    due_date = models.DateField(null=True, blank=True, help_text="Due date")
    exam_type = models.CharField(
        max_length=50,
        choices=EXAM_TYPE_CHOICES,
        help_text="Type of assignment/exam"
    )
    full_mark = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="Full marks for this assignment"
    )
    
    class Meta:
        db_table = "assignments"
        verbose_name = "Assignment"
        verbose_name_plural = "Assignments"
        ordering = ["-due_date", "title"]
    
    def __str__(self):
        return f"{self.assignment_code} - {self.title}"


class LearningMaterial(models.Model):
    """
    Learning materials uploaded for courses.
    Schema: Learning_materials table
    """
    material_code = models.CharField(
        max_length=50,
        help_text="Material code"
    )
    course = models.ForeignKey(
        'manager.Course',
        on_delete=models.CASCADE,
        related_name="learning_materials",
        help_text="Course this material belongs to"
    )
    classroom = models.ForeignKey(
        'manager.ClassRoom',
        on_delete=models.CASCADE,
        related_name="learning_materials",
        help_text="Classroom this material is for"
    )
    academic_year = models.ForeignKey(
        'manager.AcademicYear',
        on_delete=models.CASCADE,
        related_name="learning_materials",
        help_text="Academic year for this material"
    )
    uploaded_by = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.CASCADE,
        related_name="uploaded_materials",
        help_text="User who uploaded this material"
    )
    title = models.CharField(max_length=150, help_text="Material title")
    description = models.TextField(null=True, blank=True, help_text="Material description")
    file_url = models.CharField(max_length=255, help_text="URL/path to the material file")
    
    class Meta:
        db_table = "learning_materials"
        verbose_name = "Learning Material"
        verbose_name_plural = "Learning Materials"
        ordering = ["-academic_year", "course", "title"]
    
    def __str__(self):
        return f"{self.material_code} - {self.title}"


class Mark(models.Model):
    """
    Marks/scores for students on assignments.
    Schema: Marks table
    """
    student = models.ForeignKey(
        'student.Student',
        on_delete=models.CASCADE,
        related_name="marks",
        help_text="Student who received this mark"
    )
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name="marks",
        help_text="Assignment this mark is for"
    )
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Score/mark received"
    )
    
    class Meta:
        db_table = "marks"
        verbose_name = "Mark"
        verbose_name_plural = "Marks"
        ordering = ["-assignment__due_date", "student"]
    
    def __str__(self):
        return f"{self.student.user.full_name} - {self.assignment.title}: {self.score}"


class Attendance(models.Model):
    """
    Student attendance records.
    Schema: Attendance table
    """
    STATUS_CHOICES = [
        ("present", "Present"),
        ("absent", "Absent"),
        ("late", "Late"),
        ("excused", "Excused"),
    ]
    
    student = models.ForeignKey(
        'student.Student',
        on_delete=models.CASCADE,
        related_name="attendances",
        help_text="Student attendance record"
    )
    course = models.ForeignKey(
        'manager.Course',
        on_delete=models.CASCADE,
        related_name="attendances",
        help_text="Course for this attendance"
    )
    class_room = models.ForeignKey(
        'manager.ClassRoom',
        on_delete=models.CASCADE,
        related_name="attendances",
        help_text="Classroom for this attendance"
    )
    date = models.DateField(help_text="Attendance date")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        help_text="Attendance status"
    )
    note = models.TextField(null=True, blank=True, help_text="Additional notes")
    
    class Meta:
        db_table = "attendance"
        verbose_name = "Attendance"
        verbose_name_plural = "Attendances"
        ordering = ["-date", "student"]
        indexes = [
            models.Index(fields=["date", "student"]),
            models.Index(fields=["course", "date"]),
        ]
    
    def __str__(self):
        return f"{self.student.user.full_name} - {self.course.name} ({self.date}): {self.status}"
