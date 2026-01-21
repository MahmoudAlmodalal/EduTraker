from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from accounts.models import SoftDeleteModel


class Teacher(SoftDeleteModel):
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
        indexes = [
            models.Index(fields=["specialization"], name="idx_teachers_specialization"),
        ]
    
    def __str__(self):
        return f"{self.user.full_name} ({self.user.email})"


class CourseAllocation(SoftDeleteModel):
    """
    Allocation of a course to a classroom with a teacher.
    Schema: Course_Allocations table
    """
    course = models.ForeignKey(
        'school.Course',
        on_delete=models.CASCADE,
        related_name="allocations",
        help_text="Course being allocated"
    )
    class_room = models.ForeignKey(
        'school.ClassRoom',
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
    academic_year = models.ForeignKey(
        'school.AcademicYear',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="course_allocations",
        help_text="Academic year for this allocation"
    )
    
    class Meta:
        db_table = "course_allocations"
        verbose_name = "Course Allocation"
        verbose_name_plural = "Course Allocations"
        constraints = [
            models.UniqueConstraint(
                fields=["course", "class_room", "academic_year"],
                name="unique_course_classroom_year"
            )
        ]
        ordering = ["course", "class_room"]
        indexes = [
            models.Index(fields=["teacher"], name="idx_allocation_teacher"),
            models.Index(fields=["academic_year"], name="idx_allocation_year"),
        ]
    
    def __str__(self):
        return f"{self.course.name} - {self.class_room.classroom_name} ({self.teacher.user.full_name})"


class Assignment(SoftDeleteModel):
    """
    Assignment or exam created by a teacher.
    Schema: Assignments table (aligned with SRS)
    """
    EXAM_TYPE_CHOICES = [
        ("homework", "Homework"),
        ("quiz", "Quiz"),
        ("midterm", "Midterm Exam"),
        ("final", "Final Exam"),
        ("project", "Project"),
        ("participation", "Class Participation"),
        ("assignment", "Assignment"),
    ]
    
    assignment_code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Assignment code"
    )
    course_allocation = models.ForeignKey(
        CourseAllocation,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="assignments",
        help_text="Course allocation this assignment belongs to"
    )
    created_by = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="assignments",
        help_text="Teacher who created this assignment"
    )
    title = models.CharField(max_length=200, help_text="Assignment title")
    description = models.TextField(null=True, blank=True, help_text="Assignment description")
    
    # Assignment details
    assignment_type = models.CharField(
        max_length=50,
        choices=EXAM_TYPE_CHOICES,
        default="assignment",
        help_text="Type of assignment/exam"
    )
    # Keep exam_type for backwards compatibility
    exam_type = models.CharField(
        max_length=50,
        choices=EXAM_TYPE_CHOICES,
        null=True,
        blank=True,
        help_text="Type of assignment/exam (deprecated, use assignment_type)"
    )
    full_mark = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="Full marks for this assignment"
    )
    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("1.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Weight for grading calculation"
    )
    
    # Dates
    assigned_date = models.DateField(null=True, blank=True, help_text="Date assignment was assigned")
    due_date = models.DateTimeField(null=True, blank=True, help_text="Due date and time")
    
    # Resources
    instructions_url = models.URLField(
        blank=True,
        default="",
        help_text="URL to instructions"
    )
    attachments = models.JSONField(
        default=list,
        blank=True,
        help_text="List of attachment file URLs"
    )
    
    is_published = models.BooleanField(default=False, help_text="Whether the assignment is published")
    
    class Meta:
        db_table = "assignments"
        verbose_name = "Assignment"
        verbose_name_plural = "Assignments"
        ordering = ["-due_date", "title"]
        indexes = [
            models.Index(fields=["due_date"], name="idx_assignments_due_date"),
            models.Index(fields=["is_published"], name="idx_assignments_published"),
            models.Index(fields=["assigned_date"], name="idx_assignments_assigned"),
        ]
    
    def __str__(self):
        return f"{self.assignment_code} - {self.title}"


class LearningMaterial(SoftDeleteModel):
    """
    Learning materials uploaded for courses.
    Schema: Learning_materials table
    """
    material_code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Material code"
    )
    course = models.ForeignKey(
        'school.Course',
        on_delete=models.CASCADE,
        related_name="learning_materials",
        help_text="Course this material belongs to"
    )
    classroom = models.ForeignKey(
        'school.ClassRoom',
        on_delete=models.CASCADE,
        related_name="learning_materials",
        help_text="Classroom this material is for"
    )
    academic_year = models.ForeignKey(
        'school.AcademicYear',
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
    file_type = models.CharField(max_length=50, null=True, blank=True, help_text="File type/extension")
    file_size = models.IntegerField(null=True, blank=True, help_text="File size in bytes")
    
    class Meta:
        db_table = "learning_materials"
        verbose_name = "Learning Material"
        verbose_name_plural = "Learning Materials"
        ordering = ["-academic_year", "course", "title"]
        indexes = [
            models.Index(fields=["course", "academic_year"], name="idx_materials_course_year"),
        ]
    
    def __str__(self):
        return f"{self.material_code} - {self.title}"


class LessonPlan(SoftDeleteModel):
    """
    Weekly or daily lesson plans created by teachers.
    Schema: Lesson_plans table (aligned with SRS FR-CM-001)
    """
    course = models.ForeignKey(
        'school.Course',
        on_delete=models.CASCADE,
        related_name="lesson_plans",
        help_text="Course this lesson plan is for"
    )
    classroom = models.ForeignKey(
        'school.ClassRoom',
        on_delete=models.CASCADE,
        related_name="lesson_plans",
        help_text="Classroom this lesson plan is for"
    )
    academic_year = models.ForeignKey(
        'school.AcademicYear',
        on_delete=models.CASCADE,
        related_name="lesson_plans",
        help_text="Academic year for this lesson plan"
    )
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="lesson_plans",
        help_text="Teacher who created this lesson plan"
    )
    title = models.CharField(max_length=200, help_text="Lesson title")
    content = models.TextField(help_text="Detailed lesson content/procedure")
    objectives = models.TextField(null=True, blank=True, help_text="Learning objectives")
    resources_needed = models.TextField(null=True, blank=True, help_text="Resources/materials needed")
    date_planned = models.DateField(help_text="Date when this lesson is planned to be taught")
    is_published = models.BooleanField(default=False, help_text="Whether the lesson plan is visible to others")

    class Meta:
        db_table = "lesson_plans"
        verbose_name = "Lesson Plan"
        verbose_name_plural = "Lesson Plans"
        ordering = ["-date_planned", "title"]
        indexes = [
            models.Index(fields=["teacher", "date_planned"], name="idx_lesson_plans_teacher_date"),
            models.Index(fields=["course", "academic_year"], name="idx_lesson_plans_course_year"),
        ]

    def __str__(self):
        return f"{self.title} ({self.date_planned})"


class Mark(SoftDeleteModel):
    """
    Marks/scores for students on assignments (Grade in SRS).
    Schema: Marks table (aligned with SRS Grade model)
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
    # Grade information
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Score/mark received"
    )
    max_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="Maximum possible score (defaults to assignment.full_mark)"
    )
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Calculated percentage score"
    )
    letter_grade = models.CharField(
        max_length=2,
        blank=True,
        default="",
        help_text="Letter grade (A, B, C, etc.)"
    )
    # Metadata
    feedback = models.TextField(null=True, blank=True, help_text="Teacher comments/feedback")
    graded_by = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="graded_marks",
        help_text="Teacher who graded this"
    )
    graded_at = models.DateTimeField(null=True, blank=True, help_text="When this was graded")
    is_final = models.BooleanField(
        default=False,
        help_text="Whether this grade is finalized/locked"
    )
    
    class Meta:
        db_table = "marks"
        verbose_name = "Mark"
        verbose_name_plural = "Marks"
        ordering = ["-assignment__due_date", "student"]
        constraints = [
            models.UniqueConstraint(
                fields=["student", "assignment"],
                name="unique_student_assignment"
            )
        ]
        indexes = [
            models.Index(fields=["assignment"], name="idx_marks_assignment"),
        ]
    
    def __str__(self):
        return f"{self.student.user.full_name} - {self.assignment.title}: {self.score}"


class Attendance(SoftDeleteModel):
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
    course_allocation = models.ForeignKey(
        CourseAllocation,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="attendances",
        help_text="Course allocation for this attendance"
    )
    date = models.DateField(help_text="Attendance date")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        help_text="Attendance status"
    )
    note = models.TextField(null=True, blank=True, help_text="Additional notes")
    recorded_by = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recorded_attendances",
        help_text="Teacher who recorded this attendance"
    )
    
    class Meta:
        db_table = "attendance"
        verbose_name = "Attendance"
        verbose_name_plural = "Attendances"
        ordering = ["-date", "student"]
        constraints = [
            models.UniqueConstraint(
                fields=["student", "course_allocation", "date"],
                name="unique_student_allocation_date"
            )
        ]
        indexes = [
            models.Index(fields=["date"], name="idx_attendance_date"),
            models.Index(fields=["status"], name="idx_attendance_status"),
        ]
    
    def __str__(self):
        return f"{self.student.user.full_name} - {self.course_allocation.course.name} ({self.date}): {self.status}"
