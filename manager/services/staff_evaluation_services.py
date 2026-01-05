from django.db import transaction
from django.core.exceptions import PermissionDenied
from rest_framework.exceptions import ValidationError
from datetime import date

from accounts.models import CustomUser, Role
from manager.models import StaffEvaluation


@transaction.atomic
def staff_evaluation_create(
    *,
    reviewer: CustomUser,
    reviewee_id: int,
    evaluation_date: date,
    rating_score: int,
    comments: str = None
) -> StaffEvaluation:
    """
    Create a new StaffEvaluation.

    Authorization:
        - ADMIN or MANAGER_WORKSTREAM or MANAGER_SCHOOL with access to reviewee's school
    """
    # Validate reviewee exists
    try:
        reviewee = CustomUser.objects.get(id=reviewee_id)
    except CustomUser.DoesNotExist:
        raise ValidationError({"reviewee_id": "Reviewee not found."})

    # Authorization check
    if reviewer.role == Role.ADMIN:
        pass
    elif reviewer.role == Role.MANAGER_WORKSTREAM:
        if reviewee.school.work_stream_id != reviewer.work_stream_id:
            raise PermissionDenied("Permission denied.")
    elif reviewer.role == Role.MANAGER_SCHOOL:
        if reviewee.school_id != reviewer.school_id:
            raise PermissionDenied("Permission denied.")
    else:
        raise PermissionDenied("Only managers or admins can create evaluations.")

    # Validate rating score
    if rating_score < 0:
        raise ValidationError({"rating_score": "Rating score cannot be negative."})

    evaluation = StaffEvaluation(
        reviewer=reviewer,
        reviewee=reviewee,
        evaluation_date=evaluation_date,
        rating_score=rating_score,
        comments=comments,
    )

    evaluation.full_clean()
    evaluation.save()

    return evaluation


@transaction.atomic
def staff_evaluation_update(
    *,
    evaluation: StaffEvaluation,
    actor: CustomUser,
    data: dict
) -> StaffEvaluation:
    """
    Update a staff evaluation.
    """
    # Only reviewer or higher management can update
    if actor.id != evaluation.reviewer_id and actor.role not in [Role.ADMIN, Role.MANAGER_WORKSTREAM, Role.MANAGER_SCHOOL]:
        raise PermissionDenied("Permission denied.")

    if "rating_score" in data:
        if data["rating_score"] < 0:
            raise ValidationError({"rating_score": "Rating score cannot be negative."})
        evaluation.rating_score = data["rating_score"]

    if "comments" in data:
        evaluation.comments = data["comments"]

    if "evaluation_date" in data:
        evaluation.evaluation_date = data["evaluation_date"]

    evaluation.full_clean()
    evaluation.save()

    return evaluation


@transaction.atomic
def staff_evaluation_delete(*, evaluation: StaffEvaluation, actor: CustomUser) -> None:
    """
    Delete a staff evaluation.
    """
    if actor.id != evaluation.reviewer_id and actor.role != Role.ADMIN:
        raise PermissionDenied("Only the reviewer or an admin can delete an evaluation.")

    evaluation.delete()
