from accounts.models import Role

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
