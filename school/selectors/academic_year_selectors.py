from rest_framework.exceptions import NotFound, PermissionDenied
from django.db.models import QuerySet
from typing import Optional

from accounts.models import CustomUser, Role
from accounts.policies.academic_year_policies import can_manage_academic_year
from school.models import AcademicYear


def list_academic_years(
    *,
    actor: CustomUser,
    school_id: Optional[int] = None,
    include_inactive: bool = False,
) -> QuerySet[AcademicYear]:
    """
    List academic years based on actor's permissions.
    """
    if include_inactive:
        qs = AcademicYear.all_objects.select_related("school")
    else:
        qs = AcademicYear.objects.select_related("school")

    # Role-based filtering
    if actor.role == Role.ADMIN:
        pass  # Full access
    elif actor.role == Role.MANAGER_WORKSTREAM:
        qs = qs.filter(school__work_stream_id=actor.work_stream_id)
    elif actor.role in [Role.MANAGER_SCHOOL, Role.TEACHER, Role.SECRETARY]:
        qs = qs.filter(school_id=actor.school_id)
    else:
        qs = qs.none()

    # Apply filters
    if school_id is not None:
        qs = qs.filter(school_id=school_id)

    return qs.order_by('-start_date')


def get_academic_year(*, actor: CustomUser, academic_year_id: int, include_inactive: bool = False) -> AcademicYear:
    """
    Get a specific academic year by ID with permission check.
    """
    if include_inactive:
        base_qs = AcademicYear.all_objects
    else:
        base_qs = AcademicYear.objects

    ay = base_qs.select_related("school").filter(
        id=academic_year_id,
    ).first()

    if not ay:
        raise NotFound("Academic year not found")

    if not can_manage_academic_year(actor=actor, school=ay.school):
        raise PermissionDenied("You are not allowed to access this academic year")

    return ay
