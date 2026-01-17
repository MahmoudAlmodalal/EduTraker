import uuid
from datetime import date
from decimal import Decimal
from typing import Optional

from django.db import transaction
from rest_framework.exceptions import ValidationError, PermissionDenied

from teacher.models import Assignment, Teacher
from accounts.models import CustomUser


def _generate_assignment_code() -> str:
    """Generate a unique assignment code."""
    return f"ASN-{uuid.uuid4().hex[:8].upper()}"


@transaction.atomic
def assignment_create(
    *,
    creator: CustomUser,
    title: str,
    exam_type: str,
    full_mark: Decimal,
    assignment_code: Optional[str] = None,
    description: Optional[str] = None,
    due_date: Optional[date] = None,
) -> Assignment:
    """
    Create a new Assignment.
    
    Args:
        creator: The user creating the assignment (must be a teacher)
        title: Assignment title
        exam_type: Type of assignment/exam
        full_mark: Full marks for this assignment
        assignment_code: Optional assignment code (auto-generated if not provided)
        description: Optional assignment description
        due_date: Optional due date
    
    Returns:
        Assignment: The created assignment
    
    Raises:
        PermissionDenied: If creator is not a teacher
        ValidationError: If validation fails
    """
    # Verify creator is a teacher
    if not hasattr(creator, 'teacher_profile'):
        raise PermissionDenied("Only teachers can create assignments.")
    
    teacher = creator.teacher_profile
    
    # Generate assignment code if not provided
    if not assignment_code:
        assignment_code = _generate_assignment_code()
    
    # Check for duplicate assignment code for this teacher
    if Assignment.objects.filter(created_by=teacher, assignment_code=assignment_code).exists():
        raise ValidationError({"assignment_code": "This assignment code already exists for your assignments."})
    
    # Validate exam_type
    valid_types = [choice[0] for choice in Assignment.EXAM_TYPE_CHOICES]
    if exam_type not in valid_types:
        raise ValidationError({
            "exam_type": f"Invalid type. Must be one of: {', '.join(valid_types)}"
        })
    
    assignment = Assignment(
        assignment_code=assignment_code,
        created_by=teacher,
        title=title,
        description=description,
        due_date=due_date,
        exam_type=exam_type,
        full_mark=full_mark,
    )
    
    assignment.full_clean()
    assignment.save()
    
    return assignment


@transaction.atomic
def assignment_update(
    *,
    assignment: Assignment,
    actor: CustomUser,
    data: dict
) -> Assignment:
    """
    Update an existing Assignment.
    
    Args:
        assignment: The assignment to update
        actor: The user making the update
        data: Dictionary of fields to update
    
    Returns:
        Assignment: The updated assignment
    
    Raises:
        PermissionDenied: If actor is not the owner of the assignment
        ValidationError: If validation fails
    """
    # Verify ownership
    if not hasattr(actor, 'teacher_profile') or assignment.created_by != actor.teacher_profile:
        raise PermissionDenied("You don't have permission to update this assignment.")
    
    # Check for duplicate assignment code if updating
    if "assignment_code" in data:
        new_code = data["assignment_code"]
        if Assignment.objects.filter(
            created_by=assignment.created_by,
            assignment_code=new_code
        ).exclude(id=assignment.id).exists():
            raise ValidationError({"assignment_code": "This assignment code already exists for your assignments."})
        assignment.assignment_code = new_code
    
    # Update other fields
    if "title" in data:
        assignment.title = data["title"]
    
    if "description" in data:
        assignment.description = data["description"]
    
    if "due_date" in data:
        assignment.due_date = data["due_date"]
    
    if "exam_type" in data:
        valid_types = [choice[0] for choice in Assignment.EXAM_TYPE_CHOICES]
        if data["exam_type"] not in valid_types:
            raise ValidationError({
                "exam_type": f"Invalid type. Must be one of: {', '.join(valid_types)}"
            })
        assignment.exam_type = data["exam_type"]
    
    if "full_mark" in data:
        assignment.full_mark = data["full_mark"]
    
    assignment.full_clean()
    assignment.save()
    
    return assignment


@transaction.atomic
def assignment_delete(*, assignment: Assignment, actor: CustomUser) -> None:
    """
    Delete an Assignment.
    
    Args:
        assignment: The assignment to delete
        actor: The user making the request
    
    Raises:
        PermissionDenied: If actor is not the owner of the assignment
    """
    # Verify ownership
    if not hasattr(actor, 'teacher_profile') or assignment.created_by != actor.teacher_profile:
        raise PermissionDenied("You don't have permission to delete this assignment.")
    
    assignment.delete()
