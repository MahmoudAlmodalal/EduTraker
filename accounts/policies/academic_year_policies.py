from accounts.models import Role, CustomUser


def can_manage_academic_year(*, actor: CustomUser, school) -> bool:
    """
    ADMIN, MANAGER_WORKSTREAM, or MANAGER_SCHOOL can manage academic years.
    - Admins can manage any school's academic years.
    - Workstream Managers can manage schools inside their workstream.
    - School Managers can manage academic years for their own school.
    """
    if actor.role == Role.ADMIN:
        return True

    if actor.role == Role.MANAGER_WORKSTREAM:
        return actor.work_stream_id is not None and school.work_stream_id == actor.work_stream_id

    if actor.role == Role.MANAGER_SCHOOL:
        return actor.school_id is not None and actor.school_id == school.id

    return False
