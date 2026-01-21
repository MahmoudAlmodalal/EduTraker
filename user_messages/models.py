import uuid
from django.db import models
from accounts.models import SoftDeleteModel


class Message(SoftDeleteModel):
    """
    Messages between users with threading support.
    Schema: Messages table (aligned with SRS)
    """
    sender = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.CASCADE,
        related_name="sent_messages",
        help_text="User who sent the message"
    )
    recipients = models.ManyToManyField(
        'accounts.CustomUser',
        related_name="received_messages",
        through="MessageReceipt",
        through_fields=("message", "recipient"),
        help_text="Users who received the message"
    )
    
    # Message content
    subject = models.CharField(
        max_length=200,
        blank=True,
        default="",
        help_text="Message subject"
    )
    body = models.TextField(help_text="Message body/content")
    attachments = models.JSONField(
        default=list,
        blank=True,
        help_text="List of attachment URLs"
    )
    
    # Threading
    parent_message = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="replies",
        help_text="Parent message if this is a reply"
    )
    thread_id = models.UUIDField(
        default=uuid.uuid4,
        db_index=True,
        help_text="Thread identifier for grouping messages"
    )
    
    # Metadata
    sent_at = models.DateTimeField(auto_now_add=True, help_text="When the message was sent")
    is_draft = models.BooleanField(default=False, help_text="Whether this is a draft message")
    
    class Meta:
        db_table = "messages"
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        ordering = ["-sent_at"]
        indexes = [
            models.Index(fields=["thread_id", "sent_at"], name="idx_messages_thread"),
            models.Index(fields=["sender", "sent_at"], name="idx_messages_sender_sent"),
        ]
    
    def __str__(self):
        return f"{self.sender.email}: {self.subject or '(No Subject)'}"


class MessageReceipt(SoftDeleteModel):
    """
    Tracks message read status per recipient.
    Schema: Message_Receipts table (aligned with SRS)
    """
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="receipts",
        help_text="The message"
    )
    recipient = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.CASCADE,
        related_name="message_receipts",
        help_text="The recipient"
    )
    is_read = models.BooleanField(default=False, help_text="Whether the message has been read")
    read_at = models.DateTimeField(null=True, blank=True, help_text="When the message was read")
    is_deleted = models.BooleanField(default=False, help_text="Whether the recipient deleted this message")
    
    class Meta:
        db_table = "message_receipts"
        verbose_name = "Message Receipt"
        verbose_name_plural = "Message Receipts"
        unique_together = ["message", "recipient"]
        indexes = [
            models.Index(fields=["recipient", "is_read"], name="idx_receipt_recipient_read"),
        ]
    
    def __str__(self):
        status = "Read" if self.is_read else "Unread"
        return f"{self.message.subject} -> {self.recipient.email} ({status})"
