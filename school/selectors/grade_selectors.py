from django.shortcuts import get_object_or_404
from school.models import Grade
from accounts.models import CustomUser, Role

from django.db.models import QuerySet

def grade_list(*, actor: CustomUser, filters: dict, include_inactive: bool = False) -> QuerySet[Grade]:
    """Return a QuerySet of all Grades with optional filters."""
    if include_inactive and actor.role == Role.ADMIN:
        qs = Grade.all_objects.all()
    else:
        qs = Grade.objects.all()

    if name := filters.get("name"):
        qs = qs.filter(name__icontains=name)

    if numeric_level := filters.get("numeric_level"):
        qs = qs.filter(numeric_level=numeric_level)

    return qs


def grade_get(*, actor: CustomUser, grade_id: int, include_inactive: bool = False) -> Grade:
    """Retrieve a single Grade by ID."""
    if include_inactive and actor.role == Role.ADMIN:
        base_qs = Grade.all_objects
    else:
        base_qs = Grade.objects
    
    return get_object_or_404(base_qs, id=grade_id)