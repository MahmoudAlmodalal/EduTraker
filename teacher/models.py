from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class Course(models.Model):
    """
    Course offered in a school for a specific grade.
    """
    course_code = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique course code"
    )
    school = models.ForeignKey(
        "manager.School",
        on_delete=models.CASCADE,
        related_name="courses",
        help_text="School offering this course"
    )
    grade = models.ForeignKey(
        "manager.Grade",
        on_delete=models.CASCADE,
        related_name="courses",
        help_text="Grade level for this course"
    )
    name = models.CharField(max_length=150, help_text="Course name")
    
    class Meta:
        db_table = "course"
        verbose_name = "Course"
        verbose_name_plural = "Courses"
        ordering = ["course_code", "name"]
    
    def __str__(self):
        return f"{self.course_code} - {self.name}"


class Teacher(models.Model):
    """
    Teacher profile linked to User.
    """
    EMPLOYMENT_STATUS_CHOICES = [
        ("full_time", "Full Time"),
        ("part_time", "Part Time"),
        ("contract", "Contract"),
        ("substitute", "Substitute"),
    ]
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
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
        db_table = "teacher"
        verbose_name = "Teacher"
        verbose_name_plural = "Teachers"
        ordering = ["user__full_name"]
    
    def __str__(self):
        return f"{self.user.full_name} ({self.user.email})"


class ClassRoom(models.Model):
    """
    Classroom for a specific grade in an academic year.
    """
    classroom_name = models.CharField(max_length=50, help_text="Classroom name")
    school = models.ForeignKey(
        "manager.School",
        on_delete=models.CASCADE,
        related_name="classrooms",
        help_text="School this classroom belongs to"
    )
    academic_year = models.ForeignKey(
        "manager.AcademicYear",
        on_delete=models.CASCADE,
        related_name="classrooms",
        help_text="Academic year for this classroom"
    )
    grade = models.ForeignKey(
        "manager.Grade",
        on_delete=models.CASCADE,
        related_name="classrooms",
        help_text="Grade level for this classroom"
    )
    homeroom_teacher = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="homeroom_classrooms",
        help_text="Homeroom teacher for this classroom"
    )
    
    class Meta:
        db_table = "classroom"
        verbose_name = "Classroom"
        verbose_name_plural = "Classrooms"
        constraints = [
            models.UniqueConstraint(
                fields=["school", "academic_year", "classroom_name"],
                name="unique_school_year_classroom"
            )
        ]
        ordering = ["academic_year", "grade", "classroom_name"]
    
    def __str__(self):
        return f"{self.classroom_name} - {self.grade.name} ({self.academic_year.academic_year_code})"


class CourseAllocation(models.Model):
    """
    Allocation of a course to a classroom with a teacher.
    """
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="allocations",
        help_text="Course being allocated"
    )
    class_room = models.ForeignKey(
        ClassRoom,
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
        db_table = "course_allocation"
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
        unique=True,
        help_text="Unique assignment code"
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
        db_table = "assignment"
        verbose_name = "Assignment"
        verbose_name_plural = "Assignments"
        ordering = ["-due_date", "title"]
    
    def __str__(self):
        return f"{self.assignment_code} - {self.title}"


class LearningMaterial(models.Model):
    """
    Learning materials uploaded for courses.
    """
    material_code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique material code"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="learning_materials",
        help_text="Course this material belongs to"
    )
    classroom = models.ForeignKey(
        ClassRoom,
        on_delete=models.CASCADE,
        related_name="learning_materials",
        help_text="Classroom this material is for"
    )
    academic_year = models.ForeignKey(
        "manager.AcademicYear",
        on_delete=models.CASCADE,
        related_name="learning_materials",
        help_text="Academic year for this material"
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="uploaded_materials",
        help_text="User who uploaded this material"
    )
    title = models.CharField(max_length=150, help_text="Material title")
    description = models.TextField(null=True, blank=True, help_text="Material description")
    file_url = models.CharField(max_length=255, help_text="URL/path to the material file")
    
    class Meta:
        db_table = "learning_material"
        verbose_name = "Learning Material"
        verbose_name_plural = "Learning Materials"
        ordering = ["-academic_year", "course", "title"]
    
    def __str__(self):
        return f"{self.material_code} - {self.title}"


class Mark(models.Model):
    """
    Marks/scores for students on assignments.
    """
    student = models.ForeignKey(
        "student.Student",
        on_delete=models.CASCADE,
        related_name="marks",
        help_text="Student who received this mark"
    )
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
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
        db_table = "mark"
        verbose_name = "Mark"
        verbose_name_plural = "Marks"
        ordering = ["-assignment__due_date", "student"]
    
    def __str__(self):
        assignment_str = self.assignment.title if self.assignment else "N/A"
        return f"{self.student.user.full_name} - {assignment_str}: {self.score}"


class Attendance(models.Model):
    """
    Student attendance records.
    """
    STATUS_CHOICES = [
        ("present", "Present"),
        ("absent", "Absent"),
        ("late", "Late"),
        ("excused", "Excused"),
    ]
    
    student = models.ForeignKey(
        "student.Student",
        on_delete=models.CASCADE,
        related_name="attendances",
        help_text="Student attendance record"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="attendances",
        help_text="Course for this attendance"
    )
    class_room = models.ForeignKey(
        ClassRoom,
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
