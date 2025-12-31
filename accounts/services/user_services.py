from django.db import transaction
from accounts.models import CustomUser
from accounts.selectors.user_selectors import user_list as selector_user_list
from accounts.models import Role
from accounts.policies.user_policies import ROLE_CREATION_MATRIX
from django.core.exceptions import PermissionDenied
@transaction.atomic
def user_create(
    *,
    creator: CustomUser,
    email: str,
    full_name: str,
    password: str,
    role: str,
    work_stream=None,
    school=None,
) -> CustomUser:

    allowed_roles = ROLE_CREATION_MATRIX.get(creator.role, [])
    if role not in allowed_roles:
        raise PermissionDenied("You are not allowed to create this role.")

    # Scope enforcement
    if creator.role == Role.MANAGER_WORKSTREAM:
        if work_stream != creator.work_stream_id:
            raise PermissionDenied("Invalid work stream assignment.")

    if creator.role == Role.MANAGER_SCHOOL:
        if school != creator.school_id:
            raise PermissionDenied("Invalid school assignment.")

    if creator.role in [Role.TEACHER, Role.SECRETARY]:
        if school != creator.school_id:
            raise PermissionDenied(
                "Secretary/Teacher can only create users in their own school."
            )
    

    user = CustomUser(
        email=email,
        full_name=full_name,
        role=role,
        work_stream_id=work_stream,
        school_id=school,
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

@transaction.atomic
def user_deactivate(*, user: CustomUser) -> CustomUser:
    """
    Sets is_active=False (do not delete the record).
    """
    user.is_active = False
    user.save()
    return user
def can_access_user(*, actor: CustomUser, target: CustomUser) -> bool:
    if actor.role == Role.ADMIN:
        return True

    if actor.role == Role.MANAGER_WORKSTREAM:
        return target.work_stream_id == actor.work_stream_id

    if actor.role == Role.MANAGER_SCHOOL:
        return target.school_id == actor.school_id

    if actor.role in [Role.TEACHER, Role.SECRETARY]:
        return target.role in [Role.GUARDIAN, Role.STUDENT] and target.school_id == actor.school_id

    return False
