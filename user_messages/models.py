from django.db import models


class Message(models.Model):
    """
    Messages between users.
    Schema: Messages table
    """
    sender = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.CASCADE,
        related_name="sent_messages",
        help_text="User who sent the message"
    )
    receiver = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.CASCADE,
        related_name="received_messages",
        help_text="User who received the message"
    )
    subject = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        help_text="Message subject"
    )
    body = models.TextField(help_text="Message body/content")
    sent_at = models.DateTimeField(auto_now_add=True, help_text="When the message was sent")
    is_read = models.BooleanField(default=False, help_text="Whether the message has been read")
    read_at = models.DateTimeField(null=True, blank=True, help_text="When the message was read")
    
    class Meta:
        db_table = "messages"
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        ordering = ["-sent_at"]
        indexes = [
            models.Index(fields=["receiver", "is_read"]),
            models.Index(fields=["sender", "sent_at"]),
        ]
    
    def __str__(self):
        return f"{self.sender.email} → {self.receiver.email}: {self.subject or '(No Subject)'}"
