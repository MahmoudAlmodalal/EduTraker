from django.db import transaction
from django.core.exceptions import PermissionDenied
from rest_framework.exceptions import ValidationError

from accounts.models import CustomUser, Role
from manager.models import Grade


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
        - ADMIN only (grades are global entities)

    Raises:
        PermissionDenied: If creator is not admin
        ValidationError: If validation fails
    """
    # Authorization: admin only
    if creator.role != Role.ADMIN:
        raise PermissionDenied("Only admins can create grades.")

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
    """
    if actor.role != Role.ADMIN:
        raise PermissionDenied("Only admins can update grades.")

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
def grade_delete(*, grade: Grade, actor: CustomUser) -> None:
    """
    Delete a Grade.
    """
    if actor.role != Role.ADMIN:
        raise PermissionDenied("Only admins can delete grades.")

    grade.delete()