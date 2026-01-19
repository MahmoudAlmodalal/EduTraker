from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

from accounts.models import CustomUser, Role
from guardian.models import Guardian, GuardianStudentLink
from accounts.policies.user_policies import _has_school_access


def guardian_list(*, filters: dict, user: CustomUser, include_inactive: bool = False) -> QuerySet[Guardian]:
    """Return a QuerySet of Guardians filtered by user role and optional filters."""
    if include_inactive and user.role == Role.ADMIN:
        qs = Guardian.all_objects.select_related('user', 'user__school')
    else:
        qs = Guardian.objects.select_related('user', 'user__school')

    # Role-based filtering
    if user.role == Role.ADMIN:
        pass
    elif user.role == Role.MANAGER_WORKSTREAM:
        qs = qs.filter(user__school__work_stream_id=user.work_stream_id)
    elif user.role in [Role.MANAGER_SCHOOL, Role.SECRETARY]:
        qs = qs.filter(user__school_id=user.school_id)
    else:
        qs = qs.filter(user_id=user.id)

    # Apply filters
    if school_id := filters.get("school_id"):
        qs = qs.filter(user__school_id=school_id)

    if search := filters.get("search"):
        qs = qs.filter(user__full_name__icontains=search)

    return qs


def guardian_get(*, guardian_id: int, actor: CustomUser, include_inactive: bool = False) -> Guardian:
    """Retrieve a single Guardian by ID with permission check."""
    if include_inactive and actor.role == Role.ADMIN:
        base_qs = Guardian.all_objects
    else:
        base_qs = Guardian.objects

    guardian = get_object_or_404(
        base_qs.select_related('user', 'user__school'),
        user_id=guardian_id
    )

    if not _has_school_access(actor, guardian.user.school):
        if actor.id != guardian.user_id:
            raise PermissionDenied("You don't have permission to access this guardian profile.")

    return guardian


def guardian_student_list(*, guardian_id: int, actor: CustomUser) -> QuerySet[GuardianStudentLink]:
    """List students linked to a guardian."""
    guardian = guardian_get(guardian_id=guardian_id, actor=actor)
    return GuardianStudentLink.objects.filter(guardian=guardian).select_related('student', 'student__user')
