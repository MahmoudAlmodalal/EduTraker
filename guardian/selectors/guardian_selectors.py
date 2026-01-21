from django.db.models import Prefetch
from django.shortcuts import get_object_or_404

from guardian.models import Guardian, GuardianStudentLink


def guardian_get_by_user_id(*, user_id: int) -> Guardian:
    return get_object_or_404(
        Guardian.objects.select_related("user"),
        user_id=user_id,
    )


def guardian_list_qs():
    return (
        Guardian.objects
        .select_related("user")
        .prefetch_related(
            Prefetch(
                "student_links",
                queryset=GuardianStudentLink.objects.select_related("student__user"),
            )
        )
        .all()
    )


def guardian_student_link_get(*, guardian_user_id: int, student_id: int) -> GuardianStudentLink:
    return get_object_or_404(
        GuardianStudentLink.objects.select_related("guardian__user", "student__user"),
        guardian_id=guardian_user_id,
        student_id=student_id,
    )


def guardian_student_links_qs(*, guardian_user_id: int):
    return (
        GuardianStudentLink.objects
        .select_related("guardian__user", "student__user")
        .filter(guardian_id=guardian_user_id)
        .all()
    )
