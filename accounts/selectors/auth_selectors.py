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

    if not normalized_email or not password:
        raise ValidationError("Invalid email or password.")

    user = CustomUser.all_objects.select_related("work_stream", "school").filter(email=normalized_email).first()
    if user is None or not user.check_password(password):
        raise ValidationError("Invalid email or password.")

    if not user.is_active:
        raise ValidationError("This account has been deactivated.")

    return user
