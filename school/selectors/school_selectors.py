from typing import Optional

from school.models import School
from accounts.models import Role, CustomUser
from django.core.exceptions import PermissionDenied
from rest_framework.exceptions import NotFound
from accounts.policies.user_policies import _has_school_access


def school_get(*, actor: CustomUser, school_id: int, include_inactive: bool = False) -> School:
    """Retrieve a single School by ID with permission check."""
    if include_inactive:
        school = School.all_objects.filter(id=school_id).first()
    else:
        school = School.objects.filter(id=school_id).first()

    if not school:
        raise NotFound("School not found")

    if not _has_school_access(actor, school):
        raise PermissionDenied("You are not allowed to access this school")

    return school


def school_list(*, actor: CustomUser, work_stream_id: Optional[int] = None, include_inactive: bool = False):
    """List schools accessible to the actor with filtering and RBAC."""
    if include_inactive and actor.role == Role.ADMIN:
        qs = School.all_objects.all()
    else:
        qs = School.objects.all()

    if actor.role == Role.ADMIN:
        if work_stream_id:
            qs = qs.filter(work_stream_id=work_stream_id)
        return qs

    if actor.role == Role.MANAGER_WORKSTREAM:
        qs = qs.filter(work_stream_id=actor.work_stream_id)
        if work_stream_id:
            qs = qs.filter(work_stream_id=work_stream_id)
        return qs
        
    if actor.role == Role.MANAGER_SCHOOL:
        return qs.filter(id=actor.school_id)
        
    return qs.none()
