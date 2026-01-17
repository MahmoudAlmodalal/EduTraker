from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied

from teacher.models import Assignment, Teacher
from accounts.models import CustomUser


def assignment_list(*, teacher: Teacher, filters: dict) -> QuerySet[Assignment]:
    """
    Return a QuerySet of Assignments for a specific teacher with optional filtering.
    
    Args:
        teacher: The Teacher instance to filter assignments by
        filters: Dictionary of filter criteria
    
    Returns:
        QuerySet of Assignment objects
    """
    qs = Assignment.objects.filter(created_by=teacher).select_related('created_by__user')
    
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


def assignment_get(*, assignment_id: int, actor: CustomUser) -> Assignment:
    """
    Retrieve a single Assignment by ID with ownership verification.
    
    Args:
        assignment_id: The ID of the assignment to retrieve
        actor: The user making the request
    
    Returns:
        Assignment object
    
    Raises:
        Http404: If assignment not found
        PermissionDenied: If actor is not the owner of the assignment
    """
    assignment = get_object_or_404(
        Assignment.objects.select_related('created_by__user'),
        id=assignment_id
    )
    
    # Verify ownership - only the teacher who created the assignment can access it
    if not hasattr(actor, 'teacher_profile') or assignment.created_by != actor.teacher_profile:
        raise PermissionDenied("You don't have permission to access this assignment.")
    
    return assignment
