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

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Log user login."""
    try:
        ip = get_client_ip(request) if request else None
        user_agent = request.META.get('HTTP_USER_AGENT', '') if request else ''
        
        UserLoginHistory.objects.create(
            user=user,
            ip_address=ip,
            user_agent=user_agent
        )
        
        # Also log to ActivityLog
        ActivityLog.objects.create(
            actor=user,
            action_type='LOGIN',
            entity_type='User',
            entity_id=str(user.id),
            description=f"User {user.email} logged in",
            ip_address=ip
        )
    except Exception as e:
        # Prevent login failure if logging fails
        print(f"Error logging login: {e}")

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
