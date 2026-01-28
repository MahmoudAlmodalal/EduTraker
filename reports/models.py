from django.db import models
from accounts.models import CustomUser

class UserLoginHistory(models.Model):
    """
    Tracks user login history for security and analytics.
    """
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='login_history',
        help_text="User who logged in"
    )
    login_time = models.DateTimeField(auto_now_add=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True, help_text="Browser/Client info")
    
    class Meta:
        db_table = "user_login_history"
        verbose_name = "User Login History"
        verbose_name_plural = "User Login Histories"
        ordering = ["-login_time"]
        indexes = [
            models.Index(fields=["user", "login_time"], name="idx_login_user_time"),
            models.Index(fields=["login_time"], name="idx_login_time"),
        ]
        
    def __str__(self):
        return f"{self.user.email} logged in at {self.login_time}"


class ActivityLog(models.Model):
    """
    Tracks significant system activities (Audit Log).
    """
    ACTION_TYPES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('EXPORT', 'Export'),
        ('approve', 'Approve'),
        ('reject', 'Reject'),
        ('other', 'Other'),
    ]
    
    actor = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activity_logs',
        help_text="User who performed the action"
    )
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES, db_index=True)
    entity_type = models.CharField(max_length=50, help_text="Type of object affected (e.g. School, User)")
    entity_id = models.CharField(max_length=50, null=True, blank=True, help_text="ID of the affected object")
    description = models.TextField(help_text="Human readable description of the action")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = "activity_logs"
        verbose_name = "Activity Log"
        verbose_name_plural = "Activity Logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["action_type"], name="idx_activity_action"),
            models.Index(fields=["actor"], name="idx_activity_actor"),
            models.Index(fields=["created_at"], name="idx_activity_created"),
        ]
        
    def __str__(self):
        return f"{self.actor} {self.action_type} {self.entity_type} at {self.created_at}"
