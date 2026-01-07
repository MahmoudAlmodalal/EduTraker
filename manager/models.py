from django.db import models
from django.core.validators import MinValueValidator


class ManagerProfile(models.Model):
    """
    Manager profile linked to User.
    Schema: Managers table
    """
    user = models.OneToOneField(
        'accounts.CustomUser',
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="manager_profile",
        help_text="User account for this manager"
    )
    hire_date = models.DateField(help_text="Date of hire")
    department = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Department this manager oversees"
    )
    office_location = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Office location"
    )
    
    class Meta:
        db_table = "managers"
        verbose_name = "Manager"
        verbose_name_plural = "Managers"
        ordering = ["user__full_name"]
    
    def __str__(self):
        return f"{self.user.full_name} ({self.user.email})"


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
