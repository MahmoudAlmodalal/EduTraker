from django.utils import timezone
from django.core.exceptions import ValidationError
from rest_framework.exceptions import PermissionDenied

from accounts.models import CustomUser, Role
from accounts.policies.academic_year_policies import can_manage_academic_year
from school.models import AcademicYear, School


def _build_academic_year_code(*, start_date, end_date) -> str:
    start_year = start_date.year
    end_year = end_date.year

    if start_year == end_year:
        return str(start_year)

    return f"{end_year}/{start_year}"



def _validate_dates(*, start_date, end_date) -> None:
    today = timezone.localdate()

    if start_date < today:
        raise ValidationError("start_date must be today or later.")

    if end_date < today:
        raise ValidationError("end_date must be today or later.")

    if end_date < start_date:
        raise ValidationError("end_date must be >= start_date.")


def create_academic_year(*, actor: CustomUser, school: School, start_date, end_date) -> AcademicYear:
    if not can_manage_academic_year(actor=actor, school=school):
        raise PermissionDenied("Not allowed to create academic years for this school.")

    _validate_dates(start_date=start_date, end_date=end_date)

    code = _build_academic_year_code(start_date=start_date, end_date=end_date)

    return AcademicYear.objects.create(
        school=school,
        start_date=start_date,
        end_date=end_date,
        academic_year_code=code,
        is_active=True,
    )


def update_academic_year(*, actor: CustomUser, academic_year: AcademicYear, start_date=None, end_date=None) -> AcademicYear:
    if not can_manage_academic_year(actor=actor, school=academic_year.school):
        raise PermissionDenied("Not allowed to update academic years for this school.")

    new_start = start_date if start_date is not None else academic_year.start_date
    new_end = end_date if end_date is not None else academic_year.end_date

    _validate_dates(start_date=new_start, end_date=new_end)

    academic_year.start_date = new_start
    academic_year.end_date = new_end
    academic_year.academic_year_code = _build_academic_year_code(start_date=new_start, end_date=new_end)

    academic_year.save(update_fields=["start_date", "end_date", "academic_year_code"])
    return academic_year


def deactivate_academic_year(*, actor: CustomUser, academic_year: AcademicYear) -> AcademicYear:
    if not can_manage_academic_year(actor=actor, school=academic_year.school):
        raise PermissionDenied("Not allowed to deactivate academic years for this school.")

    if not academic_year.is_active:
        raise ValidationError("Academic year already deactivated.")

    academic_year.deactivate(user=actor)
    return academic_year


def activate_academic_year(*, actor: CustomUser, academic_year: AcademicYear) -> AcademicYear:
    if not can_manage_academic_year(actor=actor, school=academic_year.school):
        raise PermissionDenied("Not allowed to activate academic years for this school.")

    if academic_year.is_active:
        raise ValidationError("Academic year is already active.")

    academic_year.activate()
    return academic_year
