from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied

from teacher.models import Assignment, Teacher
from accounts.models import CustomUser, Role


def assignment_list(*, actor: CustomUser, filters: dict, include_inactive: bool = False) -> QuerySet[Assignment]:
    """Return a QuerySet of Assignments with optional filtering and RBAC."""
    if include_inactive and actor.role == Role.ADMIN:
        qs = Assignment.all_objects.select_related('created_by__user')
    else:
        qs = Assignment.objects.select_related('created_by__user')
    
    # RBAC filtering
    if actor.role == Role.ADMIN:
        pass  # Full access
    elif actor.role == Role.MANAGER_WORKSTREAM:
        qs = qs.filter(created_by__user__school__work_stream_id=actor.work_stream_id)
    elif actor.role in [Role.MANAGER_SCHOOL, Role.SECRETARY]:
        qs = qs.filter(created_by__user__school_id=actor.school_id)
    elif actor.role == Role.TEACHER:
        # Teachers see their own assignments
        qs = qs.filter(created_by__user_id=actor.id)
    else:
        qs = qs.none()

    # Filter by exam type
    if exam_type := filters.get("exam_type"):
        qs = qs.filter(exam_type=exam_type)
    
    # Filter by due date range
    if due_date_from := filters.get("due_date_from"):
        qs = qs.filter(due_date__gte=due_date_from)
    
    if due_date_to := filters.get("due_date_to"):
        qs = qs.filter(due_date__lte=due_date_to)
    
    # Filter by title (partial match)
    if title := filters.get("title"):
        qs = qs.filter(title__icontains=title)
    
    return qs.order_by('-due_date', 'title')


def assignment_get(*, assignment_id: int, actor: CustomUser, include_inactive: bool = False) -> Assignment:
    """Retrieve a single Assignment by ID with permission check."""
    if include_inactive and actor.role == Role.ADMIN:
        base_qs = Assignment.all_objects
    else:
        base_qs = Assignment.objects

    assignment = get_object_or_404(
        base_qs.select_related('created_by__user', 'created_by__user__school'),
        id=assignment_id
    )
    
    # Permission check
    if actor.role == Role.ADMIN:
        return assignment
    
    if actor.role == Role.MANAGER_WORKSTREAM:
        if assignment.created_by.user.school.work_stream_id == actor.work_stream_id:
            return assignment
            
    if actor.role in [Role.MANAGER_SCHOOL, Role.SECRETARY]:
        if assignment.created_by.user.school_id == actor.school_id:
            return assignment

    if actor.role == Role.TEACHER:
        if assignment.created_by.user_id == actor.id:
            return assignment
            
    raise PermissionDenied("You don't have permission to access this assignment.")
