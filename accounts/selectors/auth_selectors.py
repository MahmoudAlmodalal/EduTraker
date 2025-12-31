from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from accounts.models import CustomUser
from typing import Optional


def authenticate_user(*, email: str, password: str) -> Optional[CustomUser]:
    """
    Authenticate user with email and password.
    Returns user if credentials are valid, None otherwise.
    """
    user = authenticate(username=email, password=password)
    
    if user is None:
        raise ValidationError("Invalid email or password.")
    
    if not user.is_active:
        raise ValidationError("This account has been deactivated.")
    
    return user


def get_user_by_email(*, email: str) -> Optional[CustomUser]:
    """
    Get user by email address.
    """
    try:
        return CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        return None