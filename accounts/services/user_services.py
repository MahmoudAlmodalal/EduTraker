from django.db import transaction
from accounts.models import CustomUser, Role
from accounts.policies.user_policies import ROLE_CREATION_MATRIX
from accounts.selectors.user_selectors import user_get_by_email
from rest_framework.exceptions import ValidationError, PermissionDenied as DRFPermissionDenied
from typing import Optional
from workstream.models import WorkStream


@transaction.atomic
def user_create(
    *,
    creator: CustomUser,
    email: str,
    full_name: str,
    password: str,
    role: str,
    work_stream_id: Optional[int] = None,
    school_id: Optional[int] = None,
) -> CustomUser:
    """
    Create a new CustomUser with hashed password.
    
    Validates:
    - Email uniqueness
    - Role creation permissions based on creator's role
    - Scope enforcement (workstream/school assignment)
    
    If profile_data is provided, creates the corresponding role profile
    (Secretary, Teacher, Student, Guardian).
    """
    # Check email uniqueness
    if user_get_by_email(email=email):
        raise ValidationError({"email": "A user with this email already exists."})
    
    # Check role creation permission
    allowed_roles = ROLE_CREATION_MATRIX.get(creator.role, [])
    if role not in allowed_roles:
        raise DRFPermissionDenied(
            f"You are not allowed to create users with role '{role}'."
        )

    # Scope enforcement
    if creator.role == Role.MANAGER_WORKSTREAM:
        if work_stream_id != creator.work_stream_id:
            raise DRFPermissionDenied("Invalid work stream assignment.")

    if creator.role == Role.MANAGER_SCHOOL:
        if school_id != creator.school_id:
            raise DRFPermissionDenied("Invalid school assignment.")

    if creator.role in [Role.TEACHER, Role.SECRETARY]:
        if school_id != creator.school_id:
            raise DRFPermissionDenied(
                "Secretary/Teacher can only create users in their own school."
            )
    
    user = CustomUser(
        email=email,
        full_name=full_name,
        role=role,
        work_stream_id=work_stream_id,
        school_id=school_id,
    )

    user.set_password(password)
    user.full_clean()
    user.save()

    return user



@transaction.atomic
def user_update(*, user: CustomUser, data: dict) -> CustomUser:
    """
    Update user fields.
    """
    email = data.get('email')
    if email and email != user.email:
        if user_get_by_email(email=email):
            raise ValidationError({"email": "A user with this email already exists."})

    password = data.pop('password', None)
    
    for field, value in data.items():
        setattr(user, field, value)
    
    if password:
        user.set_password(password)
        
    user.full_clean()
    user.save()
    return user


@transaction.atomic
def user_delete(*, user: CustomUser) -> None:
    """
    Delete a user record.
    """
    user.delete()


@transaction.atomic
def user_deactivate(*, user: CustomUser) -> CustomUser:
    """
    Deactivate a user (set is_active=False).
    """
    user.is_active = False
    user.save()
    return user

@transaction.atomic
def user_activate(*, user: CustomUser) -> CustomUser:
    """
    Activate a user (set is_active=True).
    Check workstream capacity if user belongs to one.
    """
    if user.is_active:
        return user
        
    user.is_active = True   
    user.save()
    return user
