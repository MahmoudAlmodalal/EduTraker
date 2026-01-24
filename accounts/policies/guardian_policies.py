
from accounts.models import CustomUser

from guardian.models import Guardian
from accounts.models import Role
def can_access_guardian(*, actor: CustomUser, guardian: Guardian) -> bool:
    """Pure boolean check: can the actor access this guardian profile?"""
    if actor.role == Role.ADMIN:
        return True

    if actor.role == Role.MANAGER_WORKSTREAM:
        return guardian.user.school and guardian.user.school.work_stream_id == actor.work_stream_id

    if actor.role in [Role.MANAGER_SCHOOL, Role.SECRETARY, Role.TEACHER]:
        return guardian.user.school_id == actor.school_id

    if actor.role == Role.GUARDIAN:
        return actor.id == guardian.user_id

    return False


def can_manage_guardians_in_school(*, actor: CustomUser) -> bool:
    """Who can create/update/deactivate guardians generally (school-scoped)."""
    return actor.role in [Role.ADMIN, Role.MANAGER_WORKSTREAM, Role.MANAGER_SCHOOL, Role.SECRETARY]