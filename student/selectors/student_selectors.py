"""
Student selectors for querying Student and StudentEnrollment models.

All database queries are centralized here. Selectors apply role-based filtering
and use get_object_or_404 for single-object retrieval.
"""
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

from accounts.models import CustomUser, Role
from student.models import Student, StudentEnrollment
from guardian.models import GuardianStudentLink


def can_access_student(*, actor: CustomUser, student: Student) -> bool:
    """Check if actor has permission to access the given student. Returns True/False only."""
    if actor.role == Role.ADMIN:
        return True

    if actor.role == Role.MANAGER_WORKSTREAM:
        # Use user.school instead of student.school
        return student.user.school and student.user.school.work_stream_id == actor.work_stream_id

    if actor.role in [Role.MANAGER_SCHOOL, Role.TEACHER, Role.SECRETARY]:
        # Use user.school_id instead of student.school_id
        return student.user.school_id == actor.school_id

    if actor.role == Role.GUARDIAN:
        return GuardianStudentLink.objects.filter(
            guardian__user=actor, student=student
        ).exists()

    if actor.role == Role.STUDENT:
        return actor.id == student.user_id

    return False


def student_list(*, filters: dict, user: CustomUser, include_inactive: bool = False) -> QuerySet[Student]:
    """Return a QuerySet of Students filtered by user role and optional filters."""
    if include_inactive and user.role == Role.ADMIN:
        qs = Student.all_objects.select_related('user', 'user__school', 'user__school__work_stream')
    else:
        qs = Student.objects.select_related('user', 'user__school', 'user__school__work_stream')

    # Role-based filtering
    if user.role == Role.ADMIN:
        pass  # Full access
    elif user.role == Role.MANAGER_WORKSTREAM:
        qs = qs.filter(user__school__work_stream_id=user.work_stream_id)
    elif user.role in [Role.MANAGER_SCHOOL, Role.TEACHER, Role.SECRETARY]:
        qs = qs.filter(user__school_id=user.school_id)
    elif user.role == Role.GUARDIAN:
        linked_student_ids = GuardianStudentLink.objects.filter(
            guardian__user=user
        ).values_list('student_id', flat=True)
        qs = qs.filter(user_id__in=linked_student_ids)
    elif user.role == Role.STUDENT:
        qs = qs.filter(user_id=user.id)
    else:
        qs = qs.none()

    # Apply optional filters
    if school_id := filters.get("school_id"):
        qs = qs.filter(user__school_id=school_id)

    if grade_id := filters.get("grade_id"):
        qs = qs.filter(enrollments__class_room__grade_id=grade_id).distinct()

    if current_status := filters.get("current_status"):
        qs = qs.filter(current_status=current_status)

    if search := filters.get("search"):
        qs = qs.filter(user__full_name__icontains=search)

    return qs


def student_get(*, student_id: int, actor: CustomUser, include_inactive: bool = False) -> Student:
    """Retrieve a single Student by ID with permission check using get_object_or_404."""
    if include_inactive and actor.role == Role.ADMIN:
        base_qs = Student.all_objects
    else:
        base_qs = Student.objects

    student = get_object_or_404(
        base_qs.select_related('user', 'user__school', 'user__school__work_stream'),
        user_id=student_id
    )

    if not can_access_student(actor=actor, student=student):
        raise PermissionDenied("Access denied. You don't have permission to view this student.")

    return student
