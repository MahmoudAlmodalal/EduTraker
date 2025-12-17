from django.conf import settings
from django.db import models


class Notification(models.Model):
    """
    System notifications with different scopes.
    """
    SCOPE_TYPE_CHOICES = [
        ("Workstream", "Workstream"),
        ("School", "School"),
        ("User", "User"),
    ]
    
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_notifications",
        help_text="User who created this notification"
    )
    scope_type = models.CharField(
        max_length=20,
        choices=SCOPE_TYPE_CHOICES,
        db_index=True,
        help_text="Scope type for this notification"
    )
    scope_id = models.IntegerField(
        db_index=True,
        help_text="ID of the scope entity (workstream, school, or user)"
    )
    title = models.CharField(max_length=150, help_text="Notification title")
    body = models.TextField(help_text="Notification body/content")
    created_at = models.DateTimeField(auto_now_add=True, help_text="When the notification was created")
    
    class Meta:
        db_table = "notification"
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["scope_type", "scope_id"]),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.scope_type}: {self.scope_id})"
