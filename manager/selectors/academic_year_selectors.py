"""AcademicYear selectors for querying AcademicYear models."""
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

from school.models import AcademicYear
from accounts.models import CustomUser
from accounts.policies.user_policies import _has_school_access


def academic_year_list(*, school_id: int, filters: dict) -> QuerySet[AcademicYear]:
    """Return a QuerySet of AcademicYears for a specific school."""
    qs = AcademicYear.objects.filter(school_id=school_id)

    if academic_year_code := filters.get("academic_year_code"):
        qs = qs.filter(academic_year_code__icontains=academic_year_code)

    return qs


def academic_year_get(*, academic_year_id: int, school_id: int, actor: CustomUser) -> AcademicYear:
    """Retrieve a single AcademicYear by ID with permission check."""
    academic_year = get_object_or_404(AcademicYear, id=academic_year_id, school_id=school_id)

    if not _has_school_access(actor, academic_year.school):
        raise PermissionDenied("You don't have permission to access academic years for this school.")

    return academic_year