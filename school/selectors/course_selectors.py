from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

from school.models import Course
from accounts.models import CustomUser
from accounts.policies.user_policies import _has_school_access


def course_list(*, school_id: int, actor: CustomUser, filters: dict, include_inactive: bool = False) -> QuerySet[Course]:
    """Return a QuerySet of Courses for a specific school and grade."""
    if include_inactive:
        qs = Course.all_objects.select_related('grade').filter(school_id=school_id)
    else:
        qs = Course.objects.select_related('grade').filter(school_id=school_id)

    if name := filters.get("name"):
        qs = qs.filter(name__icontains=name)

    if grade_id := filters.get("grade_id"):
        qs = qs.filter(grade_id=grade_id)

    if course_code := filters.get("course_code"):
        qs = qs.filter(course_code__icontains=course_code)

    return qs


def course_get(*, course_id: int, school_id: int, actor: CustomUser, include_inactive: bool = False) -> Course:
    """Retrieve a single Course by ID with permission check."""
    if include_inactive:
        base_qs = Course.all_objects
    else:
        base_qs = Course.objects

    course = get_object_or_404(base_qs, id=course_id, school_id=school_id)

    if not _has_school_access(actor, course.school):
        raise PermissionDenied("You don't have permission to access courses for this school.")

    return course
