from accounts.models import Role, CustomUser

# Note: We use type hinting with strings or local imports for School to avoid early circular imports
# though usually policies are safe as they are used in services/selectors.

ROLE_CREATION_MATRIX = {
    Role.ADMIN: [
        Role.ADMIN,
        Role.MANAGER_WORKSTREAM,
        Role.MANAGER_SCHOOL,
        Role.TEACHER,
        Role.SECRETARY,
        Role.GUARDIAN,
        Role.STUDENT,
        Role.GUEST,
    ],
    Role.MANAGER_WORKSTREAM: [
        Role.MANAGER_SCHOOL,
        Role.TEACHER,
        Role.SECRETARY,
        Role.GUARDIAN,
        Role.STUDENT,
        Role.GUEST,
    ],
    Role.MANAGER_SCHOOL: [
        Role.TEACHER,
        Role.SECRETARY,
        Role.GUARDIAN,
        Role.STUDENT,
        Role.GUEST,
    ],
    Role.TEACHER: [
        Role.GUARDIAN,
        Role.STUDENT,
        Role.GUEST,
    ],
    Role.SECRETARY: [
        Role.GUARDIAN,
        Role.STUDENT,
        Role.GUEST,
    ],
}


def can_access_user(*, actor: CustomUser, target: CustomUser) -> bool:
    """Check if actor has permission to access the target user."""
    if actor.role == Role.ADMIN:
        return True

    if actor.role == Role.MANAGER_WORKSTREAM:
        return target.work_stream_id == actor.work_stream_id

    if actor.role == Role.MANAGER_SCHOOL:
        return target.school_id == actor.school_id

    if actor.role in [Role.TEACHER, Role.SECRETARY]:
        return target.role in [Role.GUARDIAN, Role.STUDENT] and target.school_id == actor.school_id

    return False


def _has_school_access(user: CustomUser, school) -> bool:
    """Check if user has access to perform operations on the given school."""
    if user.role == Role.ADMIN:
        return True
    if user.role == Role.MANAGER_WORKSTREAM:
        return school.work_stream_id == user.work_stream_id
    if user.role in [Role.MANAGER_SCHOOL, Role.TEACHER, Role.SECRETARY]:
        return school.id == user.school_id
    return False


def _can_manage_school(user: CustomUser, school) -> bool:
    """Check if user can manage students/enrollments in the given school."""
    if user.role == Role.ADMIN:
        return True
    if user.role == Role.MANAGER_WORKSTREAM:
        return school.work_stream_id == user.work_stream_id
    if user.role in [Role.MANAGER_SCHOOL, Role.TEACHER, Role.SECRETARY]:
        return user.school_id == school.id
    return False


def _can_create_in_workstream(user: CustomUser, work_stream_id: int) -> bool:
    """Check if user can create schools in the given workstream."""
    if user.role == Role.ADMIN:
        return True
    if user.role == Role.MANAGER_WORKSTREAM:
        return user.work_stream_id == work_stream_id
    return False
