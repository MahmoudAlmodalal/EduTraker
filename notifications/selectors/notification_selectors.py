"""
Notification selectors for querying Notification models.

All database queries are centralized here. Selectors apply filtering
and use get_object_or_404 for single-object retrieval.
"""
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

from accounts.models import CustomUser
from notifications.models import Notification


def notification_list(
    *,
    user: CustomUser,
    filters: dict = None
) -> QuerySet[Notification]:
    """
    Return a QuerySet of Notifications for the specified user.
    
    Args:
        user: The user whose notifications to retrieve
        filters: Optional dict with 'is_read' and 'notification_type' keys
    
    Returns:
        QuerySet of Notification objects ordered by created_at descending
    """
    filters = filters or {}
    
    qs = Notification.objects.filter(
        recipient=user,
        is_active=True
    ).select_related('recipient', 'sender')
    
    # Apply optional filters
    if filters.get('is_read') is not None:
        qs = qs.filter(is_read=filters['is_read'])
    
    if filters.get('notification_type') is not None:
        qs = qs.filter(notification_type=filters['notification_type'])
    
    return qs.order_by('-created_at')


def notification_get(
    *,
    notification_id: int,
    user: CustomUser
) -> Notification:
    """
    Retrieve a single Notification by ID with permission check.
    
    Args:
        notification_id: The ID of the notification to retrieve
        user: The user requesting the notification
    
    Returns:
        Notification object
        
    Raises:
        Http404: If notification not found
        PermissionDenied: If user doesn't have access to this notification
    """
    notification = get_object_or_404(
        Notification.objects.select_related('recipient', 'sender'),
        pk=notification_id,
        is_active=True
    )
    
    # Permission check: user must be the recipient
    if notification.recipient_id != user.id:
        raise PermissionDenied("You don't have permission to access this notification.")
    
    return notification
