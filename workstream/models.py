from django.db import models
from django.core.validators import MinValueValidator
from accounts.models import SoftDeleteModel


class WorkStream(SoftDeleteModel):
    """
    Workstream managed by a manager.
    Schema: Work_streams table
    """
    name = models.CharField(max_length=255, help_text="Workstream name")
    description = models.TextField(null=True, blank=True, help_text="Workstream description")
    manager = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_workstreams",
        help_text="Manager of this workstream"
    )
    max_user = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Maximum number of users"
    )
    
    class Meta:
        db_table = "work_streams"
        verbose_name = "Workstream"
        verbose_name_plural = "Workstreams"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["manager"], name="idx_work_streams_manager"),
        ]
    
    def __str__(self):
        return self.name
