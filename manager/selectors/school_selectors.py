"""
School selectors for querying School, AcademicYear, Grade, Course, and ClassRoom models.

All database queries are centralized here. Selectors apply role-based filtering
and use get_object_or_404 for single-object retrieval.
"""
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

from accounts.models import CustomUser, Role
from manager.models import School, AcademicYear, Grade, Course, ClassRoom


def school_list(*, filters: dict, user: CustomUser) -> QuerySet[School]:
    """Return a QuerySet of Schools filtered by user role and optional filters."""
    qs = School.objects.select_related('work_stream', 'manager').all()

    # Role-based filtering
    if user.role == Role.ADMIN:
        # Full access
        pass
    elif user.role == Role.MANAGER_WORKSTREAM:
        # Only schools in workstream(s) they manage
        qs = qs.filter(work_stream_id=user.work_stream_id)
    elif user.role == Role.MANAGER_SCHOOL:
        # Only the school they manage
        qs = qs.filter(id=user.school_id)
    else:
        # No access for other roles
        qs = qs.none()

    # Apply optional filters
    if name := filters.get("name"):
        qs = qs.filter(school_name__icontains=name)

    if work_stream_id := filters.get("work_stream_id"):
        qs = qs.filter(work_stream_id=work_stream_id)

    if manager_id := filters.get("manager_id"):
        qs = qs.filter(manager_id=manager_id)

    return qs


def school_get(*, school_id: int, actor: CustomUser) -> School:
    """Retrieve a single School by ID with permission check using get_object_or_404."""
    # Build base queryset with role-based filtering
    qs = School.objects.select_related('work_stream', 'manager')

    if actor.role == Role.ADMIN:
        # Full access
        pass
    elif actor.role == Role.MANAGER_WORKSTREAM:
        qs = qs.filter(work_stream_id=actor.work_stream_id)
    elif actor.role == Role.MANAGER_SCHOOL:
        qs = qs.filter(id=actor.school_id)
    else:
        raise PermissionDenied("You don't have permission to access schools.")

    return get_object_or_404(qs, id=school_id)


def academic_year_list(*, school_id: int, filters: dict) -> QuerySet[AcademicYear]:
    """Return a QuerySet of AcademicYears for a specific school."""
    qs = AcademicYear.objects.filter(school_id=school_id)

    if academic_year_code := filters.get("academic_year_code"):
        qs = qs.filter(academic_year_code__icontains=academic_year_code)

    return qs


def grade_list(*, filters: dict) -> QuerySet[Grade]:
    """Return a QuerySet of all Grades with optional filters."""
    qs = Grade.objects.all()

    if name := filters.get("name"):
        qs = qs.filter(name__icontains=name)

    if numeric_level := filters.get("numeric_level"):
        qs = qs.filter(numeric_level=numeric_level)

    return qs


def course_list(*, school_id: int, filters: dict) -> QuerySet[Course]:
    """Return a QuerySet of Courses for a specific school."""
    qs = Course.objects.select_related('grade').filter(school_id=school_id)

    if course_code := filters.get("course_code"):
        qs = qs.filter(course_code__icontains=course_code)

    if name := filters.get("name"):
        qs = qs.filter(name__icontains=name)

    if grade_id := filters.get("grade_id"):
        qs = qs.filter(grade_id=grade_id)

    return qs


def classroom_list(
    *, school_id: int, academic_year_id: int, filters: dict
) -> QuerySet[ClassRoom]:
    """Return a QuerySet of ClassRooms for a specific school and academic year."""
    qs = ClassRoom.objects.select_related('grade', 'homeroom_teacher').filter(
        school_id=school_id,
        academic_year_id=academic_year_id
    )

    if classroom_name := filters.get("classroom_name"):
        qs = qs.filter(classroom_name__icontains=classroom_name)

    if grade_id := filters.get("grade_id"):
        qs = qs.filter(grade_id=grade_id)

    return qs
