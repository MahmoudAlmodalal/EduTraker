from django.db import models
from accounts.models import CustomUser


class SupportTicket(models.Model):
    """
    Support ticket system for tracking user issues and requests.
    """
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed'),
    ]
    
    ticket_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        help_text="Auto-generated ticket ID (e.g., TKT-001)"
    )
    subject = models.CharField(max_length=255, help_text="Ticket subject")
    description = models.TextField(help_text="Detailed description of the issue")
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        db_index=True
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='open',
        db_index=True
    )
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_tickets',
        help_text="User who created the ticket"
    )
    assigned_to = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets',
        help_text="Admin user assigned to resolve the ticket"
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "support_tickets"
        verbose_name = "Support Ticket"
        verbose_name_plural = "Support Tickets"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "priority"], name="idx_ticket_status_priority"),
            models.Index(fields=["created_by"], name="idx_ticket_creator"),
            models.Index(fields=["created_at"], name="idx_ticket_created"),
        ]
    
    def save(self, *args, **kwargs):
        if not self.ticket_id:
            # Generate ticket ID
            last_ticket = SupportTicket.objects.order_by('-id').first()
            if last_ticket and last_ticket.ticket_id:
                try:
                    last_num = int(last_ticket.ticket_id.split('-')[1])
                    new_num = last_num + 1
                except (IndexError, ValueError):
                    new_num = 1
            else:
                new_num = 1
            self.ticket_id = f"TKT-{new_num:03d}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.ticket_id}: {self.subject}"
