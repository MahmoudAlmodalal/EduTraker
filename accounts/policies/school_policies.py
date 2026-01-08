# accounts/policies/school_policies.py

from accounts.models import Role, CustomUser
from accounts.policies.user_policies import _has_school_access, _can_create_in_workstream


def can_create_school(*, actor: CustomUser, work_stream_id: int) -> bool:
    return _can_create_in_workstream(actor, work_stream_id)


def can_update_school(*, actor: CustomUser, school) -> bool:
    return _has_school_access(actor, school)


def can_deactivate_school(*, actor: CustomUser, school) -> bool:
    # stricter than update: MANAGER_SCHOOL cannot deactivate
    if actor.role == Role.MANAGER_SCHOOL:
        return False
    return _has_school_access(actor, school)
