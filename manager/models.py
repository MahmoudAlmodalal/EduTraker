from django.db import models
from django.core.validators import MinValueValidator



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
