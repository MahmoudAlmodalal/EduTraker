from django.db import transaction
from django.core.exceptions import PermissionDenied
from rest_framework.exceptions import ValidationError
from datetime import date

from accounts.models import CustomUser, Role
from secretary.models import Secretary
from school.models import School
from accounts.services.user_services import user_create
from accounts.policies.user_policies import _has_school_access


@transaction.atomic
def secretary_create(
    *,
    creator: CustomUser,
    email: str,
    full_name: str,
    password: str,
    school_id: int,
    department: str,
    hire_date: date,
    office_number: str = None
) -> Secretary:
    """
    Create a new Secretary with their CustomUser account.

    Authorization:
        - ADMIN or MANAGER_WORKSTREAM or MANAGER_SCHOOL with access to school

    Raises:
        PermissionDenied: If creator lacks permission
        ValidationError: If validation fails
    """
    # Validate school exists
    try:
        school = School.objects.get(id=school_id)
    except School.DoesNotExist:
        raise ValidationError({"school_id": "School not found."})

    # Authorization check
    if not _has_school_access(creator, school):
        raise PermissionDenied("You don't have permission to create secretaries for this school.")

    # Create the user account
    user = user_create(
        creator=creator,
        email=email,
        full_name=full_name,
        password=password,
        role=Role.SECRETARY,
        work_stream_id=school.work_stream_id,
        school_id=school_id,
    )

    # Create the secretary profile
    secretary = Secretary(
        user=user,
        department=department,
        hire_date=hire_date,
        office_number=office_number,
    )

    secretary.full_clean()
    secretary.save()

    return secretary


@transaction.atomic
def secretary_update(*, secretary: Secretary, actor: CustomUser, data: dict) -> Secretary:
    """
    Update a secretary's profile.
    """
    # Authorization check
    if actor.role == Role.ADMIN:
        pass
    elif actor.role == Role.MANAGER_WORKSTREAM:
        if secretary.user.school.work_stream_id != actor.work_stream_id:
            raise PermissionDenied("Permission denied.")
    elif actor.role == Role.MANAGER_SCHOOL:
        if secretary.user.school_id != actor.school_id:
            raise PermissionDenied("Permission denied.")
    elif actor.id != secretary.user_id:
         raise PermissionDenied("Permission denied.")

    # Define allowed fields based on role
    if actor.role in [Role.ADMIN, Role.MANAGER_WORKSTREAM, Role.MANAGER_SCHOOL]:
        allowed_fields = ['department', 'office_number', 'hire_date']
        allowed_user_fields = ['email', 'full_name']
    else:
        # Secretaries can only update limited fields of their own profile
        allowed_fields = ['office_number']
        allowed_user_fields = ['full_name']

    # Handle user fields
    for field in allowed_user_fields:
        if field in data:
            setattr(secretary.user, field, data[field])

    if any(f in data for f in allowed_user_fields):
        secretary.user.full_clean()
        secretary.user.save()

    # Handle secretary profile fields
    for field in allowed_fields:
        if field in data:
            setattr(secretary, field, data[field])

    secretary.full_clean()
    secretary.save()

    return secretary


@transaction.atomic
def secretary_delete(*, secretary: Secretary, actor: CustomUser) -> None:
    """
    Delete a secretary. Instructs to use deactivate instead.
    """
    raise PermissionDenied("Use deactivate endpoint instead of delete.")


@transaction.atomic
def secretary_deactivate(*, secretary: Secretary, actor: CustomUser) -> Secretary:
    """
    Deactivate a secretary account.
    """
    if actor.role not in [Role.ADMIN, Role.MANAGER_WORKSTREAM, Role.MANAGER_SCHOOL]:
        raise PermissionDenied("You don't have permission to deactivate secretaries.")

    # Permission check
    if actor.role == Role.MANAGER_WORKSTREAM:
        if secretary.user.school.work_stream_id != actor.work_stream_id:
            raise PermissionDenied("Permission denied.")
    elif actor.role == Role.MANAGER_SCHOOL:
        if secretary.user.school_id != actor.school_id:
            raise PermissionDenied("Permission denied.")

    secretary.user.is_active = False
    secretary.user.save()

    return secretary
