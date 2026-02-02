from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

from accounts.models import CustomUser, Role
from student.models import StudentEnrollment
from student.selectors.student_selectors import can_access_student, student_get


def enrollment_get(*, enrollment_id: int, actor: CustomUser, include_inactive: bool = False) -> StudentEnrollment:
    """Retrieve a single StudentEnrollment by ID with permission check."""
    if include_inactive:
        base_qs = StudentEnrollment.all_objects
    else:
        base_qs = StudentEnrollment.objects

    enrollment = get_object_or_404(
        base_qs.select_related(
            'student', 'student__user', 'student__user__school',
            'class_room', 'academic_year'
        ),
        id=enrollment_id
    )

    # Check if actor can access the linked student
    if not can_access_student(actor=actor, student=enrollment.student):
        raise PermissionDenied("Access denied. You don't have permission to view this enrollment.")

    return enrollment


def student_enrollment_list(*, student_id: int, actor: CustomUser, include_inactive: bool = False) -> QuerySet[StudentEnrollment]:
    """Return a QuerySet of StudentEnrollments for a specific student."""
    # Validate actor can access the student
    student_get(student_id=student_id, actor=actor, include_inactive=include_inactive)

    if include_inactive and actor.role == Role.ADMIN:
        qs = StudentEnrollment.all_objects
    else:
        qs = StudentEnrollment.objects

    return qs.select_related(
        'class_room', 'class_room__grade', 'academic_year'
    ).filter(student_id=student_id)


def enrollment_list(*, filters: dict, actor: CustomUser, include_inactive: bool = False) -> QuerySet[StudentEnrollment]:
    """Return a QuerySet of StudentEnrollments filtered by actor role and optional filters."""
    if include_inactive and actor.role == Role.ADMIN:
        qs = StudentEnrollment.all_objects
    else:
        qs = StudentEnrollment.objects

    qs = qs.select_related(
        'student', 'student__user', 'student__user__school',
        'class_room', 'class_room__grade', 'academic_year'
    )

    # Role-based filtering
    if actor.role == Role.ADMIN:
        pass
    elif actor.role == Role.MANAGER_WORKSTREAM:
        qs = qs.filter(student__user__school__work_stream_id=actor.work_stream_id)
    elif actor.role in [Role.MANAGER_SCHOOL, Role.TEACHER, Role.SECRETARY]:
        qs = qs.filter(student__user__school_id=actor.school_id)
    else:
        qs = qs.none()

    # Apply optional filters
    if status := filters.get("status"):
        qs = qs.filter(status=status)
    
    if student_id := filters.get("student_id"):
        qs = qs.filter(student_id=student_id)

    return qs