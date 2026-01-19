from django.db import transaction
from rest_framework.exceptions import ValidationError, PermissionDenied
from django.utils import timezone
from typing import Optional
from decimal import Decimal

from teacher.models import Mark, Teacher, Assignment
from student.models import Student
from accounts.models import CustomUser, Role


@transaction.atomic
def mark_record(
    *,
    teacher: Teacher,
    student: Student,
    assignment: Assignment,
    score: Decimal,
    feedback: Optional[str] = None
) -> Mark:
    """
    Record or update a mark for a student.
    """
    # Permission check: Teacher must be the owner of the assignment
    if assignment.created_by != teacher:
        raise PermissionDenied("You can only grade assignments you created.")

    if score > assignment.full_mark:
        raise ValidationError({"score": f"Score cannot exceed full mark ({assignment.full_mark})."})

    mark, created = Mark.objects.get_or_create(
        student=student,
        assignment=assignment,
        defaults={'score': score, 'feedback': feedback, 'graded_by': teacher, 'graded_at': timezone.now()}
    )

    if not created:
        mark.score = score
        mark.feedback = feedback
        mark.graded_by = teacher
        mark.graded_at = timezone.now()
        mark.is_active = True
        mark.save()

    return mark


@transaction.atomic
def mark_deactivate(*, mark: Mark, actor: CustomUser) -> None:
    """
    Deactivate a mark.
    """
    is_owner = hasattr(actor, 'teacher_profile') and mark.graded_by == actor.teacher_profile
    if not (is_owner or actor.role == Role.ADMIN):
        raise PermissionDenied("You don't have permission to deactivate this mark.")

    if not mark.is_active:
        raise ValidationError("Mark already deactivated.")

    mark.deactivate(user=actor)


@transaction.atomic
def mark_activate(*, mark: Mark, actor: CustomUser) -> None:
    """
    Activate a mark.
    """
    if actor.role not in [Role.ADMIN, Role.MANAGER_WORKSTREAM, Role.MANAGER_SCHOOL]:
        raise PermissionDenied("You don't have permission to activate marks.")

    if mark.is_active:
        raise ValidationError("Mark is already active.")

    mark.activate()
