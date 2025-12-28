from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator


class School(models.Model):
    """
    School entity within a workstream.
    Schema: Schools table
    """
    school_name = models.CharField(
        max_length=255,
        help_text="School name"
    )
    work_stream = models.ForeignKey(
        'workstream.WorkStream',
        on_delete=models.CASCADE,
        related_name="schools",
        help_text="Workstream this school belongs to"
    )
    manager = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_schools",
        help_text="School manager"
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
        max_length=20,
        help_text="Academic year code (e.g., 2025/2026)"
    )
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="academic_years",
        help_text="School this academic year belongs to"
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
    name = models.CharField(max_length=50, help_text="Grade name (e.g., Grade 1, Kindergarten)")
    numeric_level = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Numeric level for ordering"
    )
    min_age = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="Minimum age for this grade"
    )
    max_age = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="Maximum age for this grade"
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
    course_code = models.CharField(
        max_length=50,
        help_text="Course code"
    )
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="courses",
        help_text="School offering this course"
    )
    grade = models.ForeignKey(
        Grade,
        on_delete=models.CASCADE,
        related_name="courses",
        help_text="Grade level for this course"
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
        help_text="School this classroom belongs to"
    )
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name="classrooms",
        help_text="Academic year for this classroom"
    )
    grade = models.ForeignKey(
        Grade,
        on_delete=models.CASCADE,
        related_name="classrooms",
        help_text="Grade level for this classroom"
    )
    homeroom_teacher = models.ForeignKey(
        'teacher.Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="homeroom_classrooms",
        help_text="Homeroom teacher for this classroom"
    )
    
    class Meta:
        db_table = "class_rooms"
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


class Secretary(models.Model):
    """
    Secretary/Registrar profile linked to User.
    Schema: Secretaries table
    """
    user = models.OneToOneField(
        'accounts.CustomUser',
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="secretary_profile",
        help_text="User account for this secretary/registrar"
    )
    department = models.CharField(
        max_length=100,
        help_text="Department this secretary belongs to"
    )
    office_number = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Office number"
    )
    hire_date = models.DateField(help_text="Date of hire")
    
    class Meta:
        db_table = "secretaries"
        verbose_name = "Secretary/Registrar"
        verbose_name_plural = "Secretaries/Registrars"
        ordering = ["user__full_name"]
    
    def __str__(self):
        return f"{self.user.full_name} ({self.user.email}) - {self.department}"


class StaffEvaluation(models.Model):
    """
    Staff evaluation records.
    Schema: Staff_Evaluations table
    """
    reviewer = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.CASCADE,
        related_name="reviewer_evaluations",
        help_text="User who performed the evaluation"
    )
    reviewee = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.CASCADE,
        related_name="reviewee_evaluations",
        help_text="User being evaluated"
    )
    evaluation_date = models.DateField(help_text="Date of evaluation")
    rating_score = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="Rating score"
    )
    comments = models.TextField(null=True, blank=True, help_text="Evaluation comments")
    
    class Meta:
        db_table = "staff_evaluations"
        verbose_name = "Staff Evaluation"
        verbose_name_plural = "Staff Evaluations"
        ordering = ["-evaluation_date"]
    
    def __str__(self):
        return f"{self.reviewer.email} → {self.reviewee.email} ({self.evaluation_date})"
