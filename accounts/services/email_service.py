"""
Email service for sending transactional emails.
"""

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)


def send_password_reset_email(*, user, uid: str, token: str) -> bool:
    """
    Send password reset email to user.

    Args:
        user: The user requesting password reset
        uid: URL-safe base64 encoded user ID
        token: Password reset token

    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        # Build the reset URL
        frontend_url = settings.FRONTEND_URL.rstrip('/')
        reset_url = f"{frontend_url}/password-reset/confirm?uid={uid}&token={token}"

        # Context for the email template
        context = {
            'user_name': user.full_name or user.email.split('@')[0],
            'user_email': user.email,
            'reset_url': reset_url,
            'frontend_url': frontend_url,
            'expiry_hours': settings.PASSWORD_RESET_TIMEOUT // 3600,
        }

        # Render HTML email
        html_content = render_to_string('emails/password_reset.html', context)
        text_content = strip_tags(html_content)

        # Create email
        subject = 'Reset Your EduTraker Password'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [user.email]

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=to_email,
        )
        email.attach_alternative(html_content, "text/html")

        # Send email
        email.send(fail_silently=False)

        logger.info(f"Password reset email sent to {user.email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send password reset email to {user.email}: {str(e)}")
        return False


def send_welcome_email(*, user, temporary_password: str = None) -> bool:
    """
    Send welcome email to newly created user.

    Args:
        user: The newly created user
        temporary_password: Optional temporary password (for manager-created users)

    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        frontend_url = settings.FRONTEND_URL.rstrip('/')

        context = {
            'user_name': user.full_name or user.email.split('@')[0],
            'user_email': user.email,
            'temporary_password': temporary_password,
            'login_url': f"{frontend_url}/login/portal",
            'frontend_url': frontend_url,
        }

        html_content = render_to_string('emails/welcome.html', context)
        text_content = strip_tags(html_content)

        subject = 'Welcome to EduTraker'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [user.email]

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=to_email,
        )
        email.attach_alternative(html_content, "text/html")

        email.send(fail_silently=False)

        logger.info(f"Welcome email sent to {user.email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send welcome email to {user.email}: {str(e)}")
        return False
