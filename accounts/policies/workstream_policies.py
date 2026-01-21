from accounts.models import CustomUser, Role
from workstream.models import WorkStream


def can_create_workstream(*, actor: CustomUser) -> bool:
    """
    Only ADMIN can create workstreams.
    """
    return actor.role == Role.ADMIN


def can_view_workstream(*, actor: CustomUser, workstream: WorkStream) -> bool:
    """
    Who can view a workstream:
    - ADMIN: all
    - MANAGER_WORKSTREAM: own workstream
    - MANAGER_SCHOOL: own workstream
    """
    if actor.role == Role.ADMIN:
        return True

    if actor.role in {Role.MANAGER_WORKSTREAM, Role.MANAGER_SCHOOL}:
        return actor.work_stream_id == workstream.id

    return False


def allowed_update_fields_for_workstream(
    *, actor: CustomUser, workstream: WorkStream
) -> list[str]:
    """
    Returns list of fields the actor is allowed to update.
    Empty list means no permission.
    """
    if actor.role == Role.ADMIN:
        return ["workstream_name", "description", "capacity", "is_active", "manager"]

    if actor.role == Role.MANAGER_WORKSTREAM:
        if actor.work_stream_id == workstream.id:
            return ["description"]

    return []


def can_deactivate_workstream(*, actor: CustomUser, workstream: WorkStream) -> bool:
    """
    Only ADMIN can deactivate workstreams.
    """
    return actor.role == Role.ADMIN