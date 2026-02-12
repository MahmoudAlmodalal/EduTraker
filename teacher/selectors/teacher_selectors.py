from django.db.models import QuerySet
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

from accounts.models import CustomUser, Role
from teacher.models import Teacher
from accounts.policies.user_policies import _has_school_access


def teacher_list(*, filters: dict, user: CustomUser, include_inactive: bool = False) -> QuerySet[Teacher]:
    """Return a QuerySet of Teachers filtered by user role and optional filters."""
    if include_inactive and user.role in [Role.ADMIN, Role.MANAGER_WORKSTREAM, Role.MANAGER_SCHOOL, Role.SECRETARY]:
        qs = Teacher.all_objects.select_related('user', 'user__school')
    else:
        qs = Teacher.objects.select_related('user', 'user__school')

    # Role-based filtering
    if user.role == Role.ADMIN:
        pass  # Full access
    elif user.role == Role.MANAGER_WORKSTREAM:
        qs = qs.filter(user__school__work_stream_id=user.work_stream_id)
    elif user.role in [Role.MANAGER_SCHOOL, Role.SECRETARY]:
        qs = qs.filter(user__school_id=user.school_id)
    else:
        # Teachers might only see themselves or colleagues? Usually Admin/Manager role is for listing.
        # For simplicity, if not one of above, filter to self
        qs = qs.filter(user_id=user.id)

    # Apply optional filters
    if school_id := filters.get("school_id"):
        qs = qs.filter(user__school_id=school_id)

    if specialization := filters.get("specialization"):
        qs = qs.filter(specialization__icontains=specialization)

    if search := filters.get("search"):
        qs = qs.filter(Q(user__full_name__icontains=search) | Q(user__email__icontains=search))

    return qs


def teacher_get(*, teacher_id: int, actor: CustomUser, include_inactive: bool = False) -> Teacher:
    """Retrieve a single Teacher by ID with permission check."""
    if include_inactive and actor.role in [Role.ADMIN, Role.MANAGER_WORKSTREAM, Role.MANAGER_SCHOOL, Role.SECRETARY]:
        base_qs = Teacher.all_objects
    else:
        base_qs = Teacher.objects

    teacher = get_object_or_404(
        base_qs.select_related('user', 'user__school'),
        user_id=teacher_id
    )

    if not _has_school_access(actor, teacher.user.school):
        # Allow teachers to see their own profile
        if actor.id != teacher.user_id:
            raise PermissionDenied("You don't have permission to access this teacher profile.")

    return teacher
