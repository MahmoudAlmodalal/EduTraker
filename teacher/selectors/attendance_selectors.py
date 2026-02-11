from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from datetime import date

from teacher.models import Attendance, Teacher
from accounts.models import CustomUser, Role
from guardian.models import GuardianStudentLink


def attendance_list(*, actor: CustomUser, filters: dict, include_inactive: bool = False) -> QuerySet[Attendance]:
    """Return a QuerySet of Attendance records with filtering and RBAC."""
    if include_inactive and actor.role == Role.ADMIN:
        qs = Attendance.all_objects.select_related('student__user', 'course_allocation__course', 'recorded_by__user')
    else:
        qs = Attendance.objects.select_related('student__user', 'course_allocation__course', 'recorded_by__user')

    # RBAC
    if actor.role == Role.ADMIN:
        pass
    elif actor.role == Role.MANAGER_WORKSTREAM:
        qs = qs.filter(student__user__school__work_stream_id=actor.work_stream_id)
    elif actor.role in [Role.MANAGER_SCHOOL, Role.SECRETARY]:
        qs = qs.filter(student__user__school_id=actor.school_id)
    elif actor.role == Role.TEACHER:
        qs = qs.filter(recorded_by__user_id=actor.id)
    elif actor.role == Role.STUDENT:
        qs = qs.filter(student__user_id=actor.id)
    elif actor.role == Role.GUARDIAN:
        linked_student_ids = GuardianStudentLink.objects.filter(
            guardian_id=actor.id
        ).values_list('student_id', flat=True)
        qs = qs.filter(student_id__in=linked_student_ids)
    else:
        qs = qs.none()

    # Filters
    if student_id := filters.get("student_id"):
        qs = qs.filter(student_id=student_id)
        
    if course_allocation_id := filters.get("course_allocation_id"):
        qs = qs.filter(course_allocation_id=course_allocation_id)

    if date_from := filters.get("date_from"):
        qs = qs.filter(date__gte=date_from)
        
    if date_to := filters.get("date_to"):
        qs = qs.filter(date__lte=date_to)

    if status := filters.get("status"):
        qs = qs.filter(status=status)

    return qs.order_by('-date', 'student__user__full_name')


def attendance_get(*, attendance_id: int, actor: CustomUser, include_inactive: bool = False) -> Attendance:
    """Retrieve a single Attendance record by ID with permission check."""
    if include_inactive and actor.role == Role.ADMIN:
        base_qs = Attendance.all_objects
    else:
        base_qs = Attendance.objects

    attendance = get_object_or_404(
        base_qs.select_related('student__user', 'course_allocation__course', 'recorded_by__user'),
        id=attendance_id
    )
    
    # Permission Check
    if actor.role == Role.ADMIN:
        return attendance
        
    if actor.role == Role.MANAGER_WORKSTREAM:
        if attendance.student.user.school.work_stream_id == actor.work_stream_id:
            return attendance
            
    if actor.role in [Role.MANAGER_SCHOOL, Role.SECRETARY]:
        if attendance.student.user.school_id == actor.school_id:
            return attendance

    if actor.role == Role.TEACHER:
        if attendance.recorded_by.user_id == actor.id:
            return attendance
            
    if actor.role == Role.STUDENT:
        if attendance.student.user_id == actor.id:
            return attendance
    
    if actor.role == Role.GUARDIAN:
        if GuardianStudentLink.objects.filter(guardian_id=actor.id, student_id=attendance.student_id).exists():
            return attendance

    raise PermissionDenied("You don't have permission to access this attendance record.")
