from django.db import transaction
from accounts.models import CustomUser
from accounts.selectors.user_selectors import user_list as selector_user_list

@transaction.atomic
def user_create(*, email: str, full_name: str, password: str, role: str, **extra_fields) -> CustomUser:
    """
    Handles user creation and password hashing.
    """
    user = CustomUser(
        email=email,
        full_name=full_name,
        role=role,
        **extra_fields
    )
    user.set_password(password)
    user.full_clean()
    user.save()
    return user


@transaction.atomic
def user_update(*, user: CustomUser, data: dict) -> CustomUser:
    """
    Handles updating user fields.
    """
    password = data.pop('password', None)
    
    for field, value in data.items():
        setattr(user, field, value)
    
    if password:
        user.set_password(password)
        
    user.full_clean()
    user.save()
    return user


@transaction.atomic
def user_delete(*, user: CustomUser):
    """
    Handles deleting the user record.
    """
    user.delete()


def user_list(*, filters: dict = None, user: CustomUser):
    """
    Handles list logic (delegates to selector).
    """
    return selector_user_list(filters=filters, user=user)


@transaction.atomic
def user_deactivate(*, user: CustomUser) -> CustomUser:
    """
    Sets is_active=False (do not delete the record).
    """
    user.is_active = False
    user.save()
    return user
