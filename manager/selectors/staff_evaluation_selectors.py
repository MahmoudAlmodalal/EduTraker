from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

from manager.models import StaffEvaluation
from accounts.models import CustomUser, Role


def staff_evaluation_list(*, filters: dict, user: CustomUser) -> QuerySet[StaffEvaluation]:
    """Return a QuerySet of StaffEvaluations filtered by user role and optional filters."""
    qs = StaffEvaluation.objects.select_related('reviewer', 'reviewee')

    # Role-based filtering
    if user.role == Role.ADMIN:
        pass
    elif user.role == Role.MANAGER_WORKSTREAM:
        qs = qs.filter(reviewee__school__work_stream_id=user.work_stream_id)
    elif user.role == Role.MANAGER_SCHOOL:
        qs = qs.filter(reviewee__school_id=user.school_id)
    else:
        # Others can only see evaluations where they are the reviewee
        qs = qs.filter(reviewee=user)

    # Apply optional filters
    if reviewee_id := filters.get("reviewee_id"):
        qs = qs.filter(reviewee_id=reviewee_id)

    if reviewer_id := filters.get("reviewer_id"):
        qs = qs.filter(reviewer_id=reviewer_id)

    if start_date := filters.get("start_date"):
        qs = qs.filter(evaluation_date__gte=start_date)

    if end_date := filters.get("end_date"):
        qs = qs.filter(evaluation_date__lte=end_date)

    return qs


def staff_evaluation_get(*, evaluation_id: int, actor: CustomUser) -> StaffEvaluation:
    """Retrieve a single StaffEvaluation by ID with permission check."""
    evaluation = get_object_or_404(
        StaffEvaluation.objects.select_related('reviewer', 'reviewee', 'reviewee__school'),
        id=evaluation_id
    )

    # Permission check
    if actor.role == Role.ADMIN:
        pass
    elif actor.role == Role.MANAGER_WORKSTREAM:
        if evaluation.reviewee.school.work_stream_id != actor.work_stream_id:
            raise PermissionDenied("Access denied.")
    elif actor.role == Role.MANAGER_SCHOOL:
        if evaluation.reviewee.school_id != actor.school_id:
            raise PermissionDenied("Access denied.")
    elif actor.id != evaluation.reviewee_id:
        raise PermissionDenied("Access denied.")

    return evaluation
