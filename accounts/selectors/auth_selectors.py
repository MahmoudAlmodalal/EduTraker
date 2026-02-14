from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from accounts.models import CustomUser
from typing import Optional


def authenticate_user(*, email: str, password: str) -> Optional[CustomUser]:
    """
    Authenticate user with email and password.
    Returns user if credentials are valid, None otherwise.
    Optimized with select_related to prefetch work_stream and school.
    """
    normalized_email = (email or "").strip()
    user = authenticate(username=normalized_email, password=password)
    
    if user is None:
        raise ValidationError("Invalid email or password.")

    if not user.is_active:
        raise ValidationError("This account has been deactivated.")

    # Optimize by prefetching related objects to avoid N+1 queries
    # when serializing user data in the login response
    user = CustomUser.objects.select_related('work_stream', 'school').get(pk=user.pk)

    return user
