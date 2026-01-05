from django.db import transaction
from django.core.exceptions import PermissionDenied
from rest_framework.exceptions import ValidationError

from accounts.models import CustomUser
from manager.models import School, AcademicYear
from accounts.policies.user_policies import _has_school_access


@transaction.atomic
def academic_year_create(
    *,
    creator: CustomUser,
    school_id: int,
    academic_year_code: str,
    start_date,
    end_date
) -> AcademicYear:
    """
    Create a new AcademicYear for a school.

    Authorization:
        - User must have permission to manage the school

    Raises:
        PermissionDenied: If creator lacks permission
        ValidationError: If validation fails (dates, unique code)
    """
    # Validate school exists
    try:
        school = School.objects.get(id=school_id)
    except School.DoesNotExist:
        raise ValidationError({"school_id": "School not found."})

    # Authorization check
    if not _has_school_access(creator, school):
        raise PermissionDenied("You don't have permission to create academic years for this school.")

    # Validate dates
    if start_date >= end_date:
        raise ValidationError({"start_date": "Start date must be before end date."})

    # Validate unique academic_year_code per school
    if AcademicYear.objects.filter(
        school_id=school_id, academic_year_code=academic_year_code
    ).exists():
        raise ValidationError({"academic_year_code": "This academic year code already exists for this school."})

    academic_year = AcademicYear(
        school=school,
        academic_year_code=academic_year_code,
        start_date=start_date,
        end_date=end_date,
    )

    academic_year.full_clean()
    academic_year.save()

    return academic_year


@transaction.atomic
def academic_year_update(
    *,
    academic_year: AcademicYear,
    actor: CustomUser,
    data: dict
) -> AcademicYear:
    """
    Update an existing AcademicYear.
    """
    if not _has_school_access(actor, academic_year.school):
        raise PermissionDenied("You don't have permission to update academic years for this school.")

    if "academic_year_code" in data:
        new_code = data["academic_year_code"]
        if AcademicYear.objects.filter(
            school=academic_year.school, academic_year_code=new_code
        ).exclude(id=academic_year.id).exists():
            raise ValidationError({"academic_year_code": "This academic year code already exists for this school."})
        academic_year.academic_year_code = new_code

    if "start_date" in data:
        academic_year.start_date = data["start_date"]

    if "end_date" in data:
        academic_year.end_date = data["end_date"]

    if academic_year.start_date >= academic_year.end_date:
        raise ValidationError({"start_date": "Start date must be before end date."})

    academic_year.full_clean()
    academic_year.save()

    return academic_year


@transaction.atomic
def academic_year_delete(*, academic_year: AcademicYear, actor: CustomUser) -> None:
    """
    Delete an AcademicYear.
    """
    if not _has_school_access(actor, academic_year.school):
        raise PermissionDenied("You don't have permission to delete academic years for this school.")

    academic_year.delete()