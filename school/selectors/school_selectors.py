from typing import Optional

from school.models import School
from accounts.models import Role, CustomUser
from django.core.exceptions import PermissionDenied
from rest_framework.exceptions import NotFound
from accounts.policies.user_policies import _has_school_access


def get_school(*, actor: CustomUser, school_id: int) -> School:
    school = School.objects.filter(id=school_id, is_active=True).first()
    if not school:
        raise NotFound("School not found")

    if not _has_school_access(actor, school):
        raise PermissionDenied("You are not allowed to access this school")

    return school


def list_schools_for_actor(*, actor: CustomUser, work_stream_id: Optional[int] = None):
    qs = School.objects.filter(is_active=True)

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
