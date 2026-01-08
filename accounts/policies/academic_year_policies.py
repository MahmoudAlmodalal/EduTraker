from accounts.models import Role, CustomUser


def can_manage_academic_year(*, actor: CustomUser, school) -> bool:
    """
    Only MANAGER_WORKSTREAM can manage academic years,
    and only for schools inside their workstream.
    """
    if actor.role != Role.MANAGER_WORKSTREAM:
        return False

    return actor.work_stream_id is not None and school.work_stream_id == actor.work_stream_id
