from typing import Optional
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

from accounts.models import CustomUser, Role
from guardian.models import Guardian, GuardianStudentLink
from accounts.policies.guardian_policies import can_access_guardian, can_manage_guardians_in_school

def guardian_list(*, filters: dict, user: CustomUser, include_inactive: bool = False) -> QuerySet[Guardian]:
    """Return a QuerySet of Guardians filtered by user role and optional filters."""
    if include_inactive and user.role == Role.ADMIN:
        qs = Guardian.all_objects.select_related("user", "user__school", "user__school__work_stream")
    else:
        qs = Guardian.objects.select_related("user", "user__school", "user__school__work_stream")

    # Role-based filtering
    if user.role == Role.ADMIN:
        pass
    elif user.role == Role.MANAGER_WORKSTREAM:
        qs = qs.filter(user__school__work_stream_id=user.work_stream_id)
    elif user.role in [Role.MANAGER_SCHOOL, Role.SECRETARY, Role.TEACHER]:
        qs = qs.filter(user__school_id=user.school_id)
    elif user.role == Role.GUARDIAN:
        qs = qs.filter(user_id=user.id)
    else:
        qs = qs.none()

    # Apply filters
    if school_id := filters.get("school_id"):
        qs = qs.filter(user__school_id=school_id)

    if search := filters.get("search"):
        qs = qs.filter(user__full_name__icontains=search)

    return qs


def guardian_get(*, guardian_id: int, actor: CustomUser, include_inactive: bool = False) -> Guardian:
    """Retrieve a single Guardian by ID with permission check."""
    base_qs = Guardian.all_objects if (include_inactive and actor.role == Role.ADMIN) else Guardian.objects

    guardian = get_object_or_404(
        base_qs.select_related("user", "user__school", "user__school__work_stream"),
        user_id=guardian_id,
    )

    if not can_access_guardian(actor=actor, guardian=guardian):
        raise PermissionDenied("Access denied. You don't have permission to view this guardian.")

    return guardian


def guardian_student_list(*, guardian_id: int, actor: CustomUser) -> QuerySet[GuardianStudentLink]:
    """List students linked to a guardian."""
    guardian = guardian_get(guardian_id=guardian_id, actor=actor)
    return (
        GuardianStudentLink.objects
        .filter(guardian=guardian)
        .select_related("student", "student__user", "guardian", "guardian__user")
        .order_by("-created_at")
    )


def guardian_student_link_get(*, link_id: int, actor: CustomUser) -> GuardianStudentLink:
    """Get a single guardian-student link with access check."""
    link = get_object_or_404(
        GuardianStudentLink.objects.select_related(
            "guardian", "guardian__user", "guardian__user__school",
            "student", "student__user",
        ),
        id=link_id,
    )

    # Management access: staff in the guardian's school/workstream, or guardian self (read-only)
    if actor.role == Role.GUARDIAN and actor.id == link.guardian.user_id:
        return link

    if actor.role == Role.ADMIN:
        return link

    if actor.role == Role.MANAGER_WORKSTREAM:
        if link.guardian.user.school and link.guardian.user.school.work_stream_id == actor.work_stream_id:
            return link

    if actor.role in [Role.MANAGER_SCHOOL, Role.SECRETARY, Role.TEACHER]:
        if link.guardian.user.school_id == actor.school_id:
            return link

    raise PermissionDenied("Access denied. You don't have permission to access this link.")
