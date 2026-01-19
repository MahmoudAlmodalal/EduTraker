from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class School(models.Model):
    """
    School within a workstream.
    Schema: Schools table
    """
    school_name = models.CharField(max_length=255)
    work_stream = models.ForeignKey(
        "workstream.WorkStream",
        on_delete=models.CASCADE,
        related_name="schools",
    )
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_schools",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "schools"
        ordering = ["school_name"]
        indexes = [
            models.Index(fields=["manager"], name="idx_schools_manager"),
        ]

    def __str__(self):
        return self.school_name


class AcademicYear(models.Model):
    """
    Academic year for a school.
    Schema: Academic_years table
    """
    academic_year_code = models.CharField(
        max_length=20, help_text="Academic year code (e.g., 2025/2026)"
    )
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="academic_years",
        help_text="School this academic year belongs to",
    )
    start_date = models.DateField(help_text="Academic year start date")
    end_date = models.DateField(help_text="Academic year end date")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "academic_years"
        verbose_name = "Academic Year"
        verbose_name_plural = "Academic Years"
        ordering = ["-academic_year_code"]
        constraints = [
            models.UniqueConstraint(
                fields=["school", "academic_year_code"],
                name="unique_school_academic_year_code",
            )
        ]
        indexes = [
            models.Index(fields=["school", "is_active"], name="idx_academic_years_active"),
        ]

    def __str__(self):
        return f"{self.academic_year_code} - {self.school.school_name}"


class Grade(models.Model):
    """
    Grade/level in the educational system.
    Schema: Grades table
    """
    name = models.CharField(
        max_length=50, help_text="Grade name (e.g., Grade 1, Kindergarten)"
    )
    numeric_level = models.IntegerField(
        validators=[MinValueValidator(1)], help_text="Numeric level for ordering"
    )
    min_age = models.IntegerField(
        validators=[MinValueValidator(0)], help_text="Minimum age for this grade"
    )
    max_age = models.IntegerField(
        validators=[MinValueValidator(0)], help_text="Maximum age for this grade"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "grades"
        verbose_name = "Grade"
        verbose_name_plural = "Grades"
        ordering = ["numeric_level"]
        constraints = [
            models.UniqueConstraint(fields=["name"], name="unique_grade_name"),
            models.UniqueConstraint(fields=["numeric_level"], name="unique_numeric_level"),
        ]

    def __str__(self):
        return self.name


class Course(models.Model):
    """
    Course offered in a school for a specific grade.
    Schema: Courses table
    """
    course_code = models.CharField(max_length=50, help_text="Course code")
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="courses",
        help_text="School offering this course",
    )
    grade = models.ForeignKey(
        Grade,
        on_delete=models.CASCADE,
        related_name="courses",
        help_text="Grade level for this course",
    )
    name = models.CharField(max_length=150, help_text="Course name")
    description = models.TextField(null=True, blank=True, help_text="Course description")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "courses"
        verbose_name = "Course"
        verbose_name_plural = "Courses"
        ordering = ["course_code", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["school", "course_code"],
                name="unique_school_course_code",
            )
        ]
        indexes = [
            models.Index(fields=["grade"], name="idx_courses_grade"),
        ]

    def __str__(self):
        return f"{self.course_code} - {self.name}"


class ClassRoom(models.Model):
    """
    Classroom for a specific grade in an academic year.
    Schema: Class_rooms table
    """
    classroom_name = models.CharField(max_length=100, help_text="Classroom name")
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="classrooms",
        help_text="School this classroom belongs to",
    )
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name="classrooms",
        help_text="Academic year for this classroom",
    )
    grade = models.ForeignKey(
        Grade,
        on_delete=models.CASCADE,
        related_name="classrooms",
        help_text="Grade level for this classroom",
    )
    homeroom_teacher = models.ForeignKey(
        "teacher.Teacher",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="homeroom_classrooms",
        help_text="Homeroom teacher for this classroom",
    )
    capacity = models.IntegerField(null=True, blank=True, help_text="Classroom capacity")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "class_rooms"
        verbose_name = "Classroom"
        verbose_name_plural = "Classrooms"
        constraints = [
            models.UniqueConstraint(
                fields=["school", "academic_year", "classroom_name"],
                name="unique_school_year_classroom",
            )
        ]
        ordering = ["academic_year", "grade", "classroom_name"]
        indexes = [
            models.Index(fields=["grade"], name="idx_classrooms_grade"),
            models.Index(fields=["homeroom_teacher"], name="idx_classrooms_teacher"),
        ]

    def __str__(self):
        return f"{self.classroom_name} - {self.grade.name} ({self.academic_year.academic_year_code})"
