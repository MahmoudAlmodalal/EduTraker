from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied

from teacher.models import Mark
from accounts.models import CustomUser, Role
from guardian.models import GuardianStudentLink


def mark_list(*, actor: CustomUser, filters: dict, include_inactive: bool = False) -> QuerySet[Mark]:
    """Return a QuerySet of Marks with filtering and RBAC."""
    if include_inactive and actor.role == Role.ADMIN:
        qs = Mark.all_objects.select_related('student__user', 'assignment', 'graded_by__user')
    else:
        qs = Mark.objects.select_related('student__user', 'assignment', 'graded_by__user')

    # RBAC
    if actor.role == Role.ADMIN:
        pass
    elif actor.role == Role.MANAGER_WORKSTREAM:
        qs = qs.filter(student__user__school__work_stream_id=actor.work_stream_id)
    elif actor.role in [Role.MANAGER_SCHOOL, Role.SECRETARY]:
        qs = qs.filter(student__user__school_id=actor.school_id)
    elif actor.role == Role.TEACHER:
        qs = qs.filter(graded_by__user_id=actor.id)
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
        
    if assignment_id := filters.get("assignment_id"):
        qs = qs.filter(assignment_id=assignment_id)

    return qs.order_by('-assignment__due_date', 'student__user__full_name')


def mark_get(*, mark_id: int, actor: CustomUser, include_inactive: bool = False) -> Mark:
    """Retrieve a single Mark record by ID with permission check."""
    if include_inactive and actor.role == Role.ADMIN:
        base_qs = Mark.all_objects
    else:
        base_qs = Mark.objects

    mark = get_object_or_404(
        base_qs.select_related('student__user', 'assignment', 'graded_by__user'),
        id=mark_id
    )
    
    # Permission Check
    if actor.role == Role.ADMIN:
        return mark
        
    if actor.role == Role.MANAGER_WORKSTREAM:
        if mark.student.user.school.work_stream_id == actor.work_stream_id:
            return mark
            
    if actor.role in [Role.MANAGER_SCHOOL, Role.SECRETARY]:
        if mark.student.user.school_id == actor.school_id:
            return mark

    if actor.role == Role.TEACHER:
        if mark.graded_by.user_id == actor.id:
            return mark
            
    if actor.role == Role.STUDENT:
        if mark.student.user_id == actor.id:
            return mark
    
    if actor.role == Role.GUARDIAN:
        if GuardianStudentLink.objects.filter(guardian_id=actor.id, student_id=mark.student_id).exists():
            return mark

    raise PermissionDenied("You don't have permission to access this mark record.")
