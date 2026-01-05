from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from manager.models import Grade

def grade_list(*, filters: dict) -> QuerySet[Grade]:
    """Return a QuerySet of all Grades with optional filters."""
    qs = Grade.objects.all()

    if name := filters.get("name"):
        qs = qs.filter(name__icontains=name)

    if numeric_level := filters.get("numeric_level"):
        qs = qs.filter(numeric_level=numeric_level)

    return qs


def grade_get(*, grade_id: int) -> Grade:
    """Retrieve a single Grade by ID."""
    return get_object_or_404(Grade, id=grade_id)