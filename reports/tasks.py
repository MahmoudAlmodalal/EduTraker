from celery import shared_task
from .models import UserLoginHistory, ActivityLog
from accounts.models import CustomUser
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def log_user_login_async(self, user_id, ip_address, user_agent, email):
    """
    Asynchronously log user login to UserLoginHistory and ActivityLog.
    
    Args:
        user_id: ID of the user who logged in
        ip_address: IP address of the login request
        user_agent: User agent string from the request
        email: Email of the user (for logging purposes)
    """
    try:
        # Fetch the user object
        user = CustomUser.objects.get(id=user_id)
        
        # Create UserLoginHistory record
        UserLoginHistory.objects.create(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Create ActivityLog record
        ActivityLog.objects.create(
            actor=user,
            action_type='LOGIN',
            entity_type='User',
            entity_id=str(user_id),
            description=f"User {email} logged in",
            ip_address=ip_address
        )
        
        logger.info(f"Successfully logged login for user {email} (ID: {user_id})")
        
    except CustomUser.DoesNotExist:
        logger.error(f"User with ID {user_id} not found for login logging")
        # Don't retry if user doesn't exist
        return
        
    except Exception as e:
        logger.error(f"Error logging login for user {email}: {str(e)}")
        # Retry the task
        raise self.retry(exc=e)
