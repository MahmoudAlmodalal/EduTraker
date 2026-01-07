from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

from accounts.models import CustomUser
from student.models import StudentEnrollment
from student.selectors.student_selectors import can_access_student, student_get


def enrollment_get(*, enrollment_id: int, actor: CustomUser) -> StudentEnrollment:
    """Retrieve a single StudentEnrollment by ID with permission check."""
    enrollment = get_object_or_404(
        StudentEnrollment.objects.select_related(
            'student', 'student__user', 'student__school',
            'class_room', 'academic_year'
        ),
        id=enrollment_id
    )

    # Check if actor can access the linked student
    if not can_access_student(actor=actor, student=enrollment.student):
        raise PermissionDenied("Access denied. You don't have permission to view this enrollment.")

    return enrollment

def student_enrollment_list(*, student_id: int, actor: CustomUser) -> QuerySet[StudentEnrollment]:
    """Return a QuerySet of StudentEnrollments for a specific student."""
    # Validate actor can access the student
    student_get(student_id=student_id, actor=actor)

    return StudentEnrollment.objects.select_related(
        'class_room', 'class_room__grade', 'academic_year'
    ).filter(student_id=student_id)