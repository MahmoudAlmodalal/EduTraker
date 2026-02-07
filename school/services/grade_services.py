from django.db import transaction
from django.core.exceptions import PermissionDenied
from rest_framework.exceptions import ValidationError

from accounts.models import CustomUser, Role
from school.models import Grade


@transaction.atomic
def grade_create(
    *,
    creator: CustomUser,
    name: str,
    numeric_level: int,
    min_age: int,
    max_age: int
) -> Grade:
    """
    Create a new Grade (global).

    Authorization:
        - ADMIN, MANAGER_WORKSTREAM, or MANAGER_SCHOOL

    Raises:
        PermissionDenied: If creator lacks permission
        ValidationError: If validation fails
    """
    # Authorization: admins and managers
    if creator.role not in [Role.ADMIN, Role.MANAGER_WORKSTREAM, Role.MANAGER_SCHOOL]:
        raise PermissionDenied("Only admins and managers can create grades.")

    # Validate age range
    if min_age > max_age:
        raise ValidationError({"min_age": "Minimum age must be less than or equal to maximum age."})

    # Validate unique numeric_level
    if Grade.objects.filter(numeric_level=numeric_level).exists():
        raise ValidationError({"numeric_level": "A grade with this numeric level already exists."})

    grade = Grade(
        name=name,
        numeric_level=numeric_level,
        min_age=min_age,
        max_age=max_age,
    )

    grade.full_clean()
    grade.save()

    return grade


@transaction.atomic
def grade_update(
    *,
    grade: Grade,
    actor: CustomUser,
    data: dict
) -> Grade:
    """
    Update an existing Grade.
    
    Authorization:
        - ADMIN, MANAGER_WORKSTREAM, or MANAGER_SCHOOL
    """
    if actor.role not in [Role.ADMIN, Role.MANAGER_WORKSTREAM, Role.MANAGER_SCHOOL]:
        raise PermissionDenied("Only admins and managers can update grades.")

    if "name" in data:
        grade.name = data["name"]

    if "numeric_level" in data:
        new_level = data["numeric_level"]
        if Grade.objects.filter(numeric_level=new_level).exclude(id=grade.id).exists():
            raise ValidationError({"numeric_level": "A grade with this numeric level already exists."})
        grade.numeric_level = new_level

    if "min_age" in data:
        grade.min_age = data["min_age"]

    if "max_age" in data:
        grade.max_age = data["max_age"]

    if grade.min_age > grade.max_age:
        raise ValidationError({"min_age": "Minimum age must be less than or equal to maximum age."})

    grade.full_clean()
    grade.save()

    return grade


@transaction.atomic
def grade_deactivate(*, grade: Grade, actor: CustomUser) -> None:
    """
    Deactivate a Grade (soft delete).
    
    Authorization:
        - ADMIN, MANAGER_WORKSTREAM, or MANAGER_SCHOOL
    """
    if actor.role not in [Role.ADMIN, Role.MANAGER_WORKSTREAM, Role.MANAGER_SCHOOL]:
        raise PermissionDenied("Only admins and managers can deactivate grades.")

    if not grade.is_active:
        raise ValidationError("Grade already deactivated.")

    grade.deactivate(user=actor)


@transaction.atomic
def grade_activate(*, grade: Grade, actor: CustomUser) -> None:
    """
    Activate a Grade.
    
    Authorization:
        - ADMIN, MANAGER_WORKSTREAM, or MANAGER_SCHOOL
    """
    if actor.role not in [Role.ADMIN, Role.MANAGER_WORKSTREAM, Role.MANAGER_SCHOOL]:
        raise PermissionDenied("Only admins and managers can activate grades.")

    if grade.is_active:
        raise ValidationError("Grade is already active.")

    grade.activate()