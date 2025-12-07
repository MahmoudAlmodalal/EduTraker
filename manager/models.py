from django.conf import settings
from django.db import models


class Workstream(models.Model):
    """
    Logical work unit managed by a Manager (SRS: workstreams, departments).
    """
    name = models.CharField(max_length=255, unique=True)
    capacity = models.PositiveIntegerField(help_text="Maximum number of students / classes this workstream can handle.")
    description = models.TextField(blank=True)
    manager = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name='managed_workstream',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User account for the manager of this workstream."
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='created_workstreams',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Admin who created this workstream."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class StaffEvaluation(models.Model):
    """
    Manager → Teacher evaluation (US-Manager-003).
    """
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='staff_evaluations',
        on_delete=models.CASCADE
    )
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='teacher_evaluations',
        on_delete=models.CASCADE
    )
    workstream = models.ForeignKey(
        Workstream,
        related_name='evaluations',
        on_delete=models.CASCADE
    )
    period_start = models.DateField()
    period_end = models.DateField()
    score = models.DecimalField(max_digits=4, decimal_places=2, help_text="Overall performance score (e.g. 0–10).")
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class DepartmentActivityReport(models.Model):
    """
    Daily workstream/department monitoring summary (US-Manager-001/002).
    """
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='department_reports',
        on_delete=models.CASCADE
    )
    workstream = models.ForeignKey(
        Workstream,
        related_name='activity_reports',
        on_delete=models.CASCADE
    )
    date = models.DateField()
    attendance_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Daily student attendance rate (0–100)."
    )
    notes = models.TextField(blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("workstream", "date")
        ordering = ["-date"]

    def __str__(self):
        return f"{self.workstream} - {self.date}"