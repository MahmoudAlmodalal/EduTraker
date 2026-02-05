"""
Utility functions for activity logging
"""
from .models import ActivityLog


def get_client_ip(request):
    """Extract client IP from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_activity(
    actor,
    action_type,
    entity_type,
    description,
    entity_id=None,
    request=None
):
    """
    Log an activity to the ActivityLog model.

    Args:
        actor: User who performed the action (can be None for system actions)
        action_type: Type of action ('CREATE', 'UPDATE', 'DELETE', 'EXPORT', etc.)
        entity_type: Type of entity affected (e.g., 'Manager', 'Report', 'Student')
        description: Human-readable description
        entity_id: ID of the entity (optional)
        request: HTTP request object to extract IP (optional)

    Returns:
        ActivityLog instance

    Example:
        log_activity(
            actor=request.user,
            action_type='CREATE',
            entity_type='Manager',
            description=f'Created manager: {manager.full_name}',
            entity_id=manager.id,
            request=request
        )
    """
    try:
        ip_address = None
        if request:
            ip_address = get_client_ip(request)

        activity = ActivityLog.objects.create(
            actor=actor,
            action_type=action_type.upper(),
            entity_type=entity_type,
            entity_id=str(entity_id) if entity_id else None,
            description=description,
            ip_address=ip_address
        )
        return activity
    except Exception as e:
        # Don't let logging errors break the main functionality
        print(f"Error logging activity: {e}")
        return None
