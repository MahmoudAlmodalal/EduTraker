from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class School(models.Model):
    """
    School entity within a workstream.
    Schema: Schools table
    """

    school_name = models.CharField(max_length=255, help_text="School name")
    work_stream = models.ForeignKey(
        "workstream.WorkStream",
        on_delete=models.CASCADE,
        related_name="schools",
        help_text="Workstream this school belongs to",
    )
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_schools",
        help_text="School manager",
    )

    class Meta:
        db_table = "schools"
        verbose_name = "School"
        verbose_name_plural = "Schools"
        ordering = ["school_name"]

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

    class Meta:
        db_table = "academic_years"
        verbose_name = "Academic Year"
        verbose_name_plural = "Academic Years"
        ordering = ["-academic_year_code"]

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

    class Meta:
        db_table = "grades"
        verbose_name = "Grade"
        verbose_name_plural = "Grades"
        ordering = ["numeric_level"]

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

    class Meta:
        db_table = "courses"
        verbose_name = "Course"
        verbose_name_plural = "Courses"
        ordering = ["course_code", "name"]

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

    def __str__(self):
        return f"{self.classroom_name} - {self.grade.name} ({self.academic_year.academic_year_code})"
