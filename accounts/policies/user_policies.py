from accounts.models import Role, CustomUser

ROLE_CREATION_MATRIX = {
    Role.ADMIN: [
        Role.ADMIN,
        Role.MANAGER_WORKSTREAM,
        Role.MANAGER_SCHOOL,
        Role.TEACHER,
        Role.SECRETARY,
        Role.GUARDIAN,
        Role.STUDENT,
    ],
    Role.MANAGER_WORKSTREAM: [
        Role.MANAGER_SCHOOL,
        Role.TEACHER,
        Role.SECRETARY,
        Role.GUARDIAN,
        Role.STUDENT,
    ],
    Role.MANAGER_SCHOOL: [
        Role.TEACHER,
        Role.SECRETARY,
        Role.GUARDIAN,
        Role.STUDENT,
    ],
    Role.TEACHER: [
        Role.GUARDIAN,
        Role.STUDENT,
    ],
    Role.SECRETARY: [
        Role.GUARDIAN,
        Role.STUDENT,
    ],
}
def can_access_user(*, actor: CustomUser, target: CustomUser) -> bool:
    if actor.role == Role.ADMIN:
        return True

    if actor.role == Role.MANAGER_WORKSTREAM:
        return target.work_stream_id == actor.work_stream_id

    if actor.role == Role.MANAGER_SCHOOL:
        return target.school_id == actor.school_id

    if actor.role in [Role.TEACHER, Role.SECRETARY]:
        return target.role in [Role.GUARDIAN, Role.STUDENT] and target.school_id == actor.school_id

    return False
