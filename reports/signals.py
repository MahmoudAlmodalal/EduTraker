from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import UserLoginHistory, ActivityLog
from accounts.models import CustomUser
from school.models import School
from workstream.models import WorkStream
from student.models import Student
from teacher.models import Teacher

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def _log_user_login_sync(user, ip_address, user_agent):
    """Fallback logger when Celery is unavailable."""
    UserLoginHistory.objects.create(
        user=user,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    ActivityLog.objects.create(
        actor=user,
        action_type='LOGIN',
        entity_type='User',
        entity_id=str(user.id),
        description=f"User {user.email} logged in",
        ip_address=ip_address,
    )


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Log user login asynchronously."""
    try:
        ip = get_client_ip(request) if request else None
        user_agent = request.META.get('HTTP_USER_AGENT', '') if request else ''
        
        # Import the async task
        from .tasks import log_user_login_async
        
        try:
            # Queue the task asynchronously - this returns immediately
            log_user_login_async.delay(
                user_id=user.id,
                ip_address=ip,
                user_agent=user_agent,
                email=user.email
            )
        except Exception:
            # Celery/broker not available: write synchronously so login history is not lost.
            _log_user_login_sync(user, ip, user_agent)
        
    except Exception as e:
        # Prevent login failure if task queuing fails
        print(f"Error queuing login logging task: {e}")

@receiver(post_save, sender=School)
def log_school_changes(sender, instance, created, **kwargs):
    if created:
        # Trying to find the actor is tricky in signals without request middleware
        # For now we might record it as system action or try to fetch from thread locals if available
        # But to keep it simple, we'll just log the event
        ActivityLog.objects.create(
            action_type='CREATE',
            entity_type='School',
            entity_id=str(instance.id),
            description=f"New school created: {instance.school_name}"
        )

@receiver(post_save, sender=WorkStream)
def log_workstream_changes(sender, instance, created, **kwargs):
    if created:
        ActivityLog.objects.create(
            action_type='CREATE',
            entity_type='Workstream',
            entity_id=str(instance.id),
            description=f"New workstream created: {instance.name if hasattr(instance, 'name') else str(instance)}"
        )

# We can add more specific logging here as needed
