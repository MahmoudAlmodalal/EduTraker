from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator


class SystemConfiguration(models.Model):
    """
    System-wide or school-specific configuration settings.
    """
    school = models.ForeignKey(
        "School",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="configurations",
        help_text="School-specific config (null for global)"
    )
    config_key = models.CharField(max_length=100, help_text="Configuration key")
    config_value = models.TextField(help_text="Configuration value")
    
    class Meta:
        db_table = "system_configuration"
        verbose_name = "System Configuration"
        verbose_name_plural = "System Configurations"
        constraints = [
            models.UniqueConstraint(
                fields=["school", "config_key"],
                name="unique_school_config_key"
            )
        ]
        indexes = [
            models.Index(fields=["school", "config_key"]),
        ]
    
    def __str__(self):
        scope = self.school.school_name if self.school else "Global"
        return f"{scope}: {self.config_key}"


class WorkStream(models.Model):
    """
    Workstream managed by a manager.
    """
    name = models.CharField(max_length=100, help_text="Workstream name")
    description = models.CharField(max_length=255, null=True, blank=True)
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="managed_workstreams",
        help_text="Manager of this workstream"
    )
    max_user = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Maximum number of users"
    )
    is_active = models.BooleanField(default=True, help_text="Whether this workstream is active")
    
    class Meta:
        db_table = "workstream"
        verbose_name = "Workstream"
        verbose_name_plural = "Workstreams"
        ordering = ["name"]
    
    def __str__(self):
        return self.name


class School(models.Model):
    """
    School entity within a workstream.
    """
    school_name = models.CharField(
        max_length=100,
        unique=True,
        help_text="School name"
    )
    work_stream = models.ForeignKey(
        WorkStream,
        on_delete=models.CASCADE,
        related_name="schools",
        help_text="Workstream this school belongs to"
    )
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_schools",
        help_text="School manager"
    )
    
    class Meta:
        db_table = "school"
        verbose_name = "School"
        verbose_name_plural = "Schools"
        ordering = ["school_name"]
    
    def __str__(self):
        return self.school_name


class AcademicYear(models.Model):
    """
    Academic year for a school.
    """
    academic_year_code = models.CharField(
        max_length=9,
        unique=True,
        db_index=True,
        help_text="Academic year code (e.g., 2024-2025)"
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
        db_table = "academic_year"
        verbose_name = "Academic Year"
        verbose_name_plural = "Academic Years"
        ordering = ["-academic_year_code"]
    
    def __str__(self):
        return f"{self.academic_year_code} - {self.school.school_name}"


class Grade(models.Model):
    """
    Grade/level in the educational system.
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
        db_table = "grade"
        verbose_name = "Grade"
        verbose_name_plural = "Grades"
        ordering = ["numeric_level"]
    
    def __str__(self):
        return self.name


class StaffEvaluation(models.Model):
    """
    Staff evaluation records.
    """
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviewer_evaluations",
        help_text="User who performed the evaluation"
    )
    reviewee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
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
        db_table = "staff_evaluation"
        verbose_name = "Staff Evaluation"
        verbose_name_plural = "Staff Evaluations"
        ordering = ["-evaluation_date"]
    
    def __str__(self):
        return f"{self.reviewer.email} → {self.reviewee.email} ({self.evaluation_date})"
