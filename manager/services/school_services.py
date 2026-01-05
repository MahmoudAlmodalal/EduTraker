"""
School services for creating, updating, and deleting School-related entities.

All business logic, validation, and permission enforcement is centralized here.
Services use @transaction.atomic for data-modifying operations.
"""
from django.db import transaction
from django.core.exceptions import PermissionDenied
from rest_framework.exceptions import ValidationError

from accounts.models import CustomUser, Role
from accounts.policies.user_policies import _has_school_access, _can_create_in_workstream
from manager.models import School
from workstream.models import WorkStream


@transaction.atomic
def school_create(
    *,
    creator: CustomUser,
    school_name: str,
    work_stream_id: int,
    manager_id: int
) -> School:
    """
    Create a new School.

    Authorization:
        - ADMIN/SUPERADMIN: can create in any workstream
        - WORKSTREAM manager: can create only in their workstream

    Raises:
        PermissionDenied: If creator lacks permission
        ValidationError: If validation fails (unique constraints, invalid references)
    """
    # Validate workstream exists
    try:
        work_stream = WorkStream.objects.get(id=work_stream_id)
    except WorkStream.DoesNotExist:
        raise ValidationError({"work_stream_id": "WorkStream not found."})

    # Authorization check
    if not _can_create_in_workstream(creator, work_stream_id):
        raise PermissionDenied("You don't have permission to create schools in this workstream.")

    # Validate manager exists and has correct role
    try:
        manager = CustomUser.objects.get(id=manager_id)
    except CustomUser.DoesNotExist:
        raise ValidationError({"manager_id": "Manager user not found."})

    if manager.role != Role.MANAGER_SCHOOL:
        raise ValidationError({"manager_id": "Assigned manager must have MANAGER_SCHOOL role."})

    # Validate unique school name within workstream
    if School.objects.filter(
        school_name__iexact=school_name, work_stream_id=work_stream_id
    ).exists():
        raise ValidationError({"school_name": "A school with this name already exists in the workstream."})

    school = School(
        school_name=school_name,
        work_stream=work_stream,
        manager=manager,
    )

    school.full_clean()
    school.save()

    return school


@transaction.atomic
def school_update(*, school: School, actor: CustomUser, data: dict) -> School:
    """
    Update an existing School.

    Authorization:
        - ADMIN: can update any school
        - WORKSTREAM manager: can update schools in their workstream
        - SCHOOL manager: can update only their own school

    Raises:
        PermissionDenied: If actor lacks permission
        ValidationError: If validation fails
    """
    # Authorization check
    if not _has_school_access(actor, school):
        raise PermissionDenied("You don't have permission to update this school.")

    # Validate and apply updates
    if "school_name" in data:
        new_name = data["school_name"]
        # Check unique constraint
        if School.objects.filter(
            school_name__iexact=new_name,
            work_stream_id=school.work_stream_id
        ).exclude(id=school.id).exists():
            raise ValidationError({"school_name": "A school with this name already exists in the workstream."})
        school.school_name = new_name

    if "work_stream_id" in data:
        # Only admin can change workstream
        if actor.role != Role.ADMIN:
            raise PermissionDenied("Only admins can change the workstream of a school.")
        try:
            work_stream = WorkStream.objects.get(id=data["work_stream_id"])
            school.work_stream = work_stream
        except WorkStream.DoesNotExist:
            raise ValidationError({"work_stream_id": "WorkStream not found."})

    if "manager_id" in data:
        try:
            manager = CustomUser.objects.get(id=data["manager_id"])
            if manager.role != Role.MANAGER_SCHOOL:
                raise ValidationError({"manager_id": "Assigned manager must have MANAGER_SCHOOL role."})
            school.manager = manager
        except CustomUser.DoesNotExist:
            raise ValidationError({"manager_id": "Manager user not found."})

    school.full_clean()
    school.save()

    return school


@transaction.atomic
def school_delete(*, school: School, actor: CustomUser) -> None:
    """
    Delete a School.

    Authorization:
        - ADMIN: can delete any school
        - WORKSTREAM manager: can delete schools in their workstream
        - SCHOOL manager: can delete only their own school

    Raises:
        PermissionDenied: If actor lacks permission
    """
    if not _has_school_access(actor, school):
        raise PermissionDenied("You don't have permission to delete this school.")

    school.delete()
