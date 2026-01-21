from django.db import IntegrityError, transaction
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from guardian.models import Guardian, GuardianStudentLink
from student.models import Student

User = get_user_model()


@transaction.atomic
def guardian_create(*, user: User, phone_number: str | None = None) -> Guardian:
    guardian, created = Guardian.objects.get_or_create(
        user=user,
        defaults={"phone_number": phone_number},
    )
    if not created:
        # update phone if provided
        if phone_number is not None:
            guardian.phone_number = phone_number
            guardian.save(update_fields=["phone_number"])
    return guardian


@transaction.atomic
def guardian_update(*, guardian: Guardian, phone_number: str | None = None) -> Guardian:
    if phone_number is not None:
        guardian.phone_number = phone_number
        guardian.save(update_fields=["phone_number"])
    return guardian


@transaction.atomic
def guardian_deactivate(*, guardian: Guardian) -> Guardian:
    # Deactivate account (recommended)
    user = guardian.user
    if getattr(user, "is_active", True) is False:
        return guardian
    user.is_active = False
    user.save(update_fields=["is_active"])
    return guardian


@transaction.atomic
def guardian_reactivate(*, guardian: Guardian) -> Guardian:
    user = guardian.user
    if getattr(user, "is_active", True) is True:
        return guardian
    user.is_active = True
    user.save(update_fields=["is_active"])
    return guardian


@transaction.atomic
def guardian_student_link_create(
    *,
    guardian: Guardian,
    student: Student,
    relationship_type: str,
) -> GuardianStudentLink:
    try:
        return GuardianStudentLink.objects.create(
            guardian=guardian,
            student=student,
            relationship_type=relationship_type,
        )
    except IntegrityError:
        raise ValidationError({"detail": "This guardian is already linked to this student."})


@transaction.atomic
def guardian_student_link_update(
    *,
    link: GuardianStudentLink,
    relationship_type: str,
) -> GuardianStudentLink:
    link.relationship_type = relationship_type
    link.save(update_fields=["relationship_type"])
    return link


@transaction.atomic
def guardian_student_link_delete(*, link: GuardianStudentLink) -> None:
    link.delete()
