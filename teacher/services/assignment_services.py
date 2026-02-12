import uuid
from datetime import date
from decimal import Decimal
from typing import Optional

from django.db import transaction
from rest_framework.exceptions import ValidationError, PermissionDenied

from teacher.models import Assignment, Teacher
from accounts.models import CustomUser, Role
from accounts.policies.user_policies import _can_manage_school
from reports.utils import log_activity


def _generate_assignment_code() -> str:
    """Generate a unique assignment code."""
    return f"ASN-{uuid.uuid4().hex[:8].upper()}"


@transaction.atomic
def assignment_create(
    *,
    creator: CustomUser,
    title: str,
    exam_type: Optional[str] = None,
    assignment_type: Optional[str] = None,
    full_mark: Decimal,
    assignment_code: Optional[str] = None,
    description: Optional[str] = None,
    due_date: Optional[date] = None,
    course_allocation_id: Optional[int] = None,
) -> Assignment:
    """
    Create a new Assignment.
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
    
    final_exam_type = assignment_type or exam_type
    if not final_exam_type:
        raise ValidationError({"exam_type": "Exam type or Assignment type is required."})

    # Validate exam_type
    valid_types = [choice[0] for choice in Assignment.EXAM_TYPE_CHOICES]
    if final_exam_type not in valid_types:
        raise ValidationError({
            "exam_type": f"Invalid type. Must be one of: {', '.join(valid_types)}"
        })
    
    # Handle Course Allocation
    course_allocation = None
    if course_allocation_id:
        from teacher.models import CourseAllocation
        try:
            course_allocation = CourseAllocation.objects.get(id=course_allocation_id)
            # Optional: Check if the allocation belongs to this teacher
            if course_allocation.teacher != teacher:
                raise PermissionDenied("You can only create assignments for your own course allocations.")
        except CourseAllocation.DoesNotExist:
            raise ValidationError({"course_allocation_id": "Invalid course allocation ID."})

    assignment = Assignment(
        assignment_code=assignment_code,
        created_by=teacher,
        title=title,
        description=description,
        due_date=due_date,
        exam_type=final_exam_type,
        assignment_type=final_exam_type,
        full_mark=full_mark,
        course_allocation=course_allocation,
    )
    
    assignment.full_clean()
    assignment.save()

    log_activity(
        actor=creator,
        action_type='CREATE',
        entity_type='Assignment',
        entity_id=assignment.id,
        description=f"Created assignment '{assignment.title}' ({assignment.assignment_code})."
    )
    
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
    """
    # Verify ownership or management
    is_owner = hasattr(actor, 'teacher_profile') and assignment.created_by == actor.teacher_profile
    if not (is_owner or actor.role == Role.ADMIN):
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

    log_activity(
        actor=actor,
        action_type='UPDATE',
        entity_type='Assignment',
        entity_id=assignment.id,
        description=f"Updated assignment '{assignment.title}' ({assignment.assignment_code})."
    )
    
    return assignment


@transaction.atomic
def assignment_deactivate(*, assignment: Assignment, actor: CustomUser) -> None:
    """
    Deactivate an Assignment (soft delete).
    """
    # Verify ownership or management
    is_owner = hasattr(actor, 'teacher_profile') and assignment.created_by == actor.teacher_profile
    if not (is_owner or actor.role == Role.ADMIN):
        raise PermissionDenied("You don't have permission to deactivate this assignment.")

    if not assignment.is_active:
        raise ValidationError("Assignment already deactivated.")

    assignment.deactivate(user=actor)

    log_activity(
        actor=actor,
        action_type='UPDATE',
        entity_type='Assignment',
        entity_id=assignment.id,
        description=f"Deactivated assignment '{assignment.title}' ({assignment.assignment_code})."
    )


@transaction.atomic
def assignment_activate(*, assignment: Assignment, actor: CustomUser) -> None:
    """
    Activate an Assignment.
    """
    if actor.role not in [Role.ADMIN, Role.MANAGER_WORKSTREAM, Role.MANAGER_SCHOOL]:
        raise PermissionDenied("You don't have permission to activate assignments.")

    if assignment.is_active:
        raise ValidationError("Assignment is already active.")

    assignment.activate()

    log_activity(
        actor=actor,
        action_type='UPDATE',
        entity_type='Assignment',
        entity_id=assignment.id,
        description=f"Activated assignment '{assignment.title}' ({assignment.assignment_code})."
    )
