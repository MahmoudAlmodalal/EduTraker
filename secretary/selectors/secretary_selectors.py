from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

from secretary.models import Secretary
from accounts.models import CustomUser, Role


def secretary_list(*, filters: dict, user: CustomUser) -> QuerySet[Secretary]:
    """Return a QuerySet of Secretaries filtered by user role and optional filters."""
    qs = Secretary.objects.select_related('user', 'user__school', 'user__school__work_stream')

    # Role-based filtering
    if user.role == Role.ADMIN:
        pass
    elif user.role == Role.MANAGER_WORKSTREAM:
        qs = qs.filter(user__school__work_stream_id=user.work_stream_id)
    elif user.role == Role.MANAGER_SCHOOL:
        qs = qs.filter(user__school_id=user.school_id)
    else:
        qs = qs.none()

    # Apply optional filters
    if school_id := filters.get("school_id"):
        qs = qs.filter(user__school_id=school_id)

    if department := filters.get("department"):
        qs = qs.filter(department__icontains=department)

    if search := filters.get("search"):
        qs = qs.filter(user__full_name__icontains=search)

    return qs


def secretary_get(*, secretary_id: int, actor: CustomUser) -> Secretary:
    """Retrieve a single Secretary by ID with permission check."""
    secretary = get_object_or_404(
        Secretary.objects.select_related('user', 'user__school'),
        user_id=secretary_id
    )

    # Permission check
    if actor.role == Role.ADMIN:
        pass
    elif actor.role == Role.MANAGER_WORKSTREAM:
        if secretary.user.school.work_stream_id != actor.work_stream_id:
            raise PermissionDenied("Access denied.")
    elif actor.role == Role.MANAGER_SCHOOL:
        if secretary.user.school_id != actor.school_id:
            raise PermissionDenied("Access denied.")
    elif actor.id != secretary.user_id:
        raise PermissionDenied("Access denied.")

    return secretary
