from django.db import transaction
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError, PermissionDenied
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import CustomUser, Role
from student.services.student_services import student_create
from workstream.models import WorkStream
from accounts.selectors.auth_selectors import authenticate_user
from accounts.selectors.user_selectors import user_get_by_email
from typing import Dict


def validate_workstream_access(*, user: CustomUser, workstream_id: int) -> bool:
    """
    Validate if user has access to the specified workstream.
    """
    if user.role == "admin":
        return True
    
    if user.work_stream_id == workstream_id:
        return True
    
    return False
    
def generate_tokens_for_user(user: CustomUser) -> Dict[str, str]:
    """
    Generate JWT access and refresh tokens for a user.
    """
    refresh = RefreshToken.for_user(user)
    
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@transaction.atomic
def portal_register(
    *,
    email: str,
    full_name: str,
    password: str,
) -> CustomUser:
    """
    Register a new user in the portal with GUEST role by default.
    This is for admin/workstream manager registration.
    """
    # Check if email already exists
    if user_get_by_email(email=email):
        raise ValidationError("A user with this email already exists.")
    
    # Create user with GUEST role
    user = CustomUser(
        email=email,
        full_name=full_name,
        role=Role.GUEST,
    )
    
    user.set_password(password)
    user.full_clean()
    user.save()
    
    return user


def portal_login(
    *,
    email: str,
    password: str,
) -> Dict:
    """
    Login for portal users (Admin, Workstream Managers).
    Only allows admin and manager roles to login.
    """
    user = authenticate_user(email=email, password=password)
    
    # Check if user has appropriate role for portal login
    allowed_roles = [
        Role.ADMIN,
        Role.MANAGER_WORKSTREAM,
    ]
    
    if user.role not in allowed_roles:
        raise PermissionDenied(
            "Only administrators and Workstream managers can login to the portal."
        )
    
    tokens = generate_tokens_for_user(user)
    
    return {
        'user': user,
        'tokens': tokens,
    }


@transaction.atomic
def workstream_register_user(
    *,
    workstream_id: int,
    email: str,
    full_name: str,
    password: str,
) -> CustomUser:
    """
    Register a new user in a specific workstream with STUDENT role by default.
    The Student profile with school/grade info can be added later by a manager.
    """
    # Check if email already exists
    if user_get_by_email(email=email):
        raise ValidationError("A user with this email already exists.")
    
    # Validate workstream exists and is active
    try:
        workstream = WorkStream.objects.get(id=workstream_id, is_active=True)
    except WorkStream.DoesNotExist:
        raise ValidationError("Workstream not found.")
    
    # Check workstream capacity
    current_users_count = CustomUser.objects.filter(
        work_stream=workstream,
        is_active=True
    ).count()

    if current_users_count >= workstream.capacity:
        raise ValidationError(
            "This workstream has reached the maximum number of users."
        )
    
    # Create user with STUDENT role and assign to workstream
    user = CustomUser(
        email=email,
        full_name=full_name,
        role=Role.STUDENT,
        work_stream=workstream,
    )
    
    user.set_password(password)
    user.full_clean()
    user.save()
    
    return user


def workstream_login(
    *,
    workstream_id: int,
    email: str,
    password: str,
) -> Dict:
    """
    Login for workstream users (Students, Teachers, Guardians, etc.).
    Validates that user belongs to the specified workstream.
    """
    user = authenticate_user(email=email, password=password)
    
    # Validate user belongs to this workstream
    if not validate_workstream_access(user=user, workstream_id=workstream_id):
        raise PermissionDenied(
            "You do not have access to this workstream."
        )
    
    tokens = generate_tokens_for_user(user)
    
    return {
        'user': user,
        'tokens': tokens,
    }


def logout_user(*, refresh_token: str) -> bool:
    """
    Logout user by blacklisting their refresh token.
    """
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
        return True
    except Exception:
        raise ValidationError("Invalid or expired refresh token.")


def request_password_reset(*, email: str) -> Dict:
    """
    Request a password reset for a user.
    Sends an email with the reset link in production.
    In debug mode, also returns the token for testing purposes.
    """
    from django.conf import settings
    from django.contrib.auth.tokens import default_token_generator
    from django.utils.http import urlsafe_base64_encode
    from django.utils.encoding import force_bytes
    from accounts.services.email_service import send_password_reset_email

    user = user_get_by_email(email=email)

    if not user:
        # Don't reveal whether the email exists
        return {'message': 'If this email exists, a password reset link has been sent.'}

    if not user.is_active:
        return {'message': 'If this email exists, a password reset link has been sent.'}

    # Generate a password reset token
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    # Send the password reset email
    email_sent = send_password_reset_email(user=user, uid=uid, token=token)

    response = {
        'message': 'If this email exists, a password reset link has been sent.',
    }

    # In DEBUG mode, also return the token for development/testing
    if settings.DEBUG:
        response['uid'] = uid
        response['token'] = token
        response['email_sent'] = email_sent

    return response


def reset_password(*, uid: str, token: str, new_password: str) -> bool:
    """
    Reset user's password using the reset token.
    """
    from django.contrib.auth.tokens import default_token_generator
    from django.utils.http import urlsafe_base64_decode
    
    try:
        user_id = urlsafe_base64_decode(uid).decode()
        user = CustomUser.objects.get(pk=user_id)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        raise ValidationError("Invalid reset link.")
    
    if not default_token_generator.check_token(user, token):
        raise ValidationError("Invalid or expired reset token.")
    
    user.set_password(new_password)
    user.save()
    
    return True
