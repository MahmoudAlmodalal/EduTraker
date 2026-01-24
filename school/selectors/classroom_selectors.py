from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

from school.models import ClassRoom
from accounts.models import CustomUser, Role
from accounts.policies.user_policies import _has_school_access


def classroom_list(
    *, school_id: int, academic_year_id: int, actor: CustomUser, filters: dict, include_inactive: bool = False
) -> QuerySet[ClassRoom]:
    """Return a QuerySet of ClassRooms for a specific school and academic year."""
    if include_inactive and actor.role == Role.ADMIN:
        qs = ClassRoom.all_objects.select_related('grade', 'homeroom_teacher').filter(
            school_id=school_id,
            academic_year_id=academic_year_id
        )
    else:
        qs = ClassRoom.objects.select_related('grade', 'homeroom_teacher').filter(
            school_id=school_id,
            academic_year_id=academic_year_id
        )

    if classroom_name := filters.get("classroom_name"):
        qs = qs.filter(classroom_name__icontains=classroom_name)

    if grade_id := filters.get("grade_id"):
        qs = qs.filter(grade_id=grade_id)

    return qs


def classroom_get(
    *, classroom_id: int, school_id: int, academic_year_id: int, actor: CustomUser, include_inactive: bool = False
) -> ClassRoom:
    """Retrieve a single ClassRoom by ID with permission check."""
    if include_inactive:
        base_qs = ClassRoom.all_objects
    else:
        base_qs = ClassRoom.objects

    classroom = get_object_or_404(
        base_qs, 
        id=classroom_id, 
        school_id=school_id, 
        academic_year_id=academic_year_id
    )

    if not _has_school_access(actor, classroom.school):
        raise PermissionDenied("You don't have permission to access classrooms for this school.")

    return classroom