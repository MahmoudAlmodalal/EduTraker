"""
Notification services for creating and mutating Notification models.

All business logic, permission checks, and workflows are centralized here.
Services use @transaction.atomic for data-modifying operations.
"""
from django.db import transaction
from django.utils import timezone
from typing import Optional

from accounts.models import CustomUser
from notifications.models import Notification
from notifications.selectors.notification_selectors import notification_get


@transaction.atomic
def notification_mark_read(
    *,
    notification_id: int,
    user: CustomUser
) -> Notification:
    """
    Mark a notification as read.
    
    Args:
        notification_id: The ID of the notification to mark as read
        user: The user marking the notification as read
    
    Returns:
        Updated Notification object
        
    Raises:
        Http404: If notification not found
        PermissionDenied: If user doesn't have access
    """
    notification = notification_get(notification_id=notification_id, user=user)
    
    if not notification.is_read:
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save(update_fields=['is_read', 'read_at', 'updated_at'])
    
    return notification


@transaction.atomic
def notification_create(
    *,
    recipient: CustomUser,
    title: str,
    message: str,
    notification_type: str = "system",
    sender: Optional[CustomUser] = None,
    action_url: str = "",
    related_object_type: str = "",
    related_object_id: Optional[int] = None
) -> Notification:
    """
    Create a new notification.
    
    Args:
        recipient: The user receiving the notification
        title: Notification title
        message: Notification body/content
        notification_type: Type of notification (default: "system")
        sender: Optional user who created this notification
        action_url: Optional URL for action
        related_object_type: Optional type of related object
        related_object_id: Optional ID of related object
    
    Returns:
        Created Notification object
    """
    notification = Notification(
        recipient=recipient,
        sender=sender,
        title=title,
        message=message,
        notification_type=notification_type,
        action_url=action_url,
        related_object_type=related_object_type,
        related_object_id=related_object_id,
    )
    
    notification.full_clean()
    notification.save()
    
    return notification

@transaction.atomic
def notification_mark_all_read(
    *,
    user: CustomUser
) -> int:
    """
    Mark all unread notifications as read for the specified user.
    
    Returns:
        Number of notifications marked as read
    """
    unread_notifications = Notification.objects.filter(
        recipient=user,
        is_read=False,
        is_active=True
    )
    
    count = unread_notifications.count()
    if count > 0:
        unread_notifications.update(
            is_read=True,
            read_at=timezone.now(),
            updated_at=timezone.now()
        )
    
    return count
