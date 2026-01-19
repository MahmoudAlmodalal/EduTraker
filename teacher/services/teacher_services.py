from django.db import transaction
from datetime import date
from rest_framework.exceptions import ValidationError
from django.core.exceptions import PermissionDenied
from typing import Optional

from accounts.models import CustomUser, Role
from accounts.services.user_services import user_create
from teacher.models import Teacher
from school.models import School
from accounts.policies.user_policies import _has_school_access, _can_manage_school


@transaction.atomic
def teacher_create(
    *,
    creator: CustomUser,
    email: str,
    full_name: str,
    password: str,
    school_id: int,
    hire_date: date,
    employment_status: str,
    specialization: Optional[str] = None,
    highest_degree: Optional[str] = None,
    years_of_experience: Optional[int] = None,
    office_location: Optional[str] = None,
) -> Teacher:
    """
    Create a new Teacher with their CustomUser account.
    """
    # Validate school exists
    try:
        school = School.objects.get(id=school_id)
    except School.DoesNotExist:
        raise ValidationError({"school_id": "School not found."})
    
    # Authorization check
    if not _can_manage_school(creator, school):
        raise PermissionDenied("You don't have permission to create teachers for this school.")

    # Validate employment_status
    valid_statuses = ["full_time", "part_time", "contract", "substitute"]
    if employment_status not in valid_statuses:
        raise ValidationError({
            "employment_status": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        })
    
    # Determine work_stream from school
    work_stream_id = school.work_stream_id
    
    # Create the user account
    user = user_create(
        creator=creator,
        email=email,
        full_name=full_name,
        password=password,
        role=Role.TEACHER,
        work_stream_id=work_stream_id,
        school_id=school_id,
    )
    
    # Create the teacher profile
    teacher = Teacher(
        user=user,
        specialization=specialization,
        hire_date=hire_date,
        employment_status=employment_status,
        highest_degree=highest_degree,
        years_of_experience=years_of_experience,
        office_location=office_location,
    )
    
    teacher.full_clean()
    teacher.save()
    
    return teacher


@transaction.atomic
def teacher_update(*, teacher: Teacher, actor: CustomUser, data: dict) -> Teacher:
    """
    Update teacher profile fields.
    """
    if not _has_school_access(actor, teacher.user.school):
        if actor.id != teacher.user_id:
            raise PermissionDenied("You don't have permission to update this teacher.")

    for field, value in data.items():
        if hasattr(teacher, field):
            setattr(teacher, field, value)
    
    teacher.full_clean()
    teacher.save()
    return teacher


@transaction.atomic
def teacher_deactivate(*, teacher: Teacher, actor: CustomUser) -> None:
    """
    Deactivate a teacher (soft delete).
    """
    if not _can_manage_school(actor, teacher.user.school):
        raise PermissionDenied("You don't have permission to deactivate this teacher.")

    if not teacher.is_active:
        raise ValidationError("Teacher already deactivated.")

    # Deactivate associated user
    teacher.user.deactivate(user=actor)

    # Deactivate teacher profile
    teacher.deactivate(user=actor)


@transaction.atomic
def teacher_activate(*, teacher: Teacher, actor: CustomUser) -> None:
    """
    Activate a teacher.
    """
    if actor.role not in [Role.ADMIN, Role.MANAGER_WORKSTREAM, Role.MANAGER_SCHOOL]:
        raise PermissionDenied("You don't have permission to activate teachers.")

    if not _can_manage_school(actor, teacher.user.school):
        raise PermissionDenied("You don't have permission to activate teachers for this school.")

    if teacher.is_active:
        raise ValidationError("Teacher is already active.")

    # Activate associated user
    teacher.user.activate()

    # Activate teacher profile
    teacher.activate()
