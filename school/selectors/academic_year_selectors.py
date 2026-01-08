from rest_framework.exceptions import NotFound, PermissionDenied

from accounts.models import CustomUser
from accounts.policies.academic_year_policies import can_manage_academic_year
from school.models import AcademicYear


def get_academic_year(*, actor: CustomUser, academic_year_id: int) -> AcademicYear:
    ay = AcademicYear.objects.select_related("school").filter(
        id=academic_year_id,
        is_active=True,
    ).first()

    if not ay:
        raise NotFound("Academic year not found")

    if not can_manage_academic_year(actor=actor, school=ay.school):
        raise PermissionDenied("You are not allowed to access this academic year")

    return ay
