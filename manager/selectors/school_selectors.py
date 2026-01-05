"""
School selectors for querying School, AcademicYear, Grade, Course, and ClassRoom models.

All database queries are centralized here. Selectors apply role-based filtering
and use get_object_or_404 for single-object retrieval.
"""
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

from accounts.models import CustomUser, Role
from manager.models import School


def school_list(*, filters: dict, user: CustomUser) -> QuerySet[School]:
    """Return a QuerySet of Schools filtered by user role and optional filters."""
    qs = School.objects.select_related('work_stream', 'manager').all()

    # Role-based filtering
    if user.role == Role.ADMIN:
        # Full access
        pass
    elif user.role == Role.MANAGER_WORKSTREAM:
        # Only schools in workstream(s) they manage
        qs = qs.filter(work_stream_id=user.work_stream_id)
    elif user.role == Role.MANAGER_SCHOOL:
        # Only the school they manage
        qs = qs.filter(id=user.school_id)
    else:
        # No access for other roles
        qs = qs.none()

    # Apply optional filters
    if name := filters.get("name"):
        qs = qs.filter(school_name__icontains=name)

    if work_stream_id := filters.get("work_stream_id"):
        qs = qs.filter(work_stream_id=work_stream_id)

    if manager_id := filters.get("manager_id"):
        qs = qs.filter(manager_id=manager_id)

    return qs


def school_get(*, school_id: int, actor: CustomUser) -> School:
    """Retrieve a single School by ID with permission check using get_object_or_404."""
    # Build base queryset with role-based filtering
    qs = School.objects.select_related('work_stream', 'manager')

    if actor.role == Role.ADMIN:
        # Full access
        pass
    elif actor.role == Role.MANAGER_WORKSTREAM:
        qs = qs.filter(work_stream_id=actor.work_stream_id)
    elif actor.role == Role.MANAGER_SCHOOL:
        qs = qs.filter(id=actor.school_id)
    else:
        raise PermissionDenied("You don't have permission to access schools.")

    return get_object_or_404(qs, id=school_id)









