from django.db import transaction
from rest_framework.exceptions import ValidationError
from django.core.exceptions import PermissionDenied
from typing import Optional

from accounts.models import CustomUser, Role
from accounts.services.user_services import user_create
from guardian.models import Guardian, GuardianStudentLink
from school.models import School
from student.models import Student
from accounts.policies.user_policies import _has_school_access, _can_manage_school


@transaction.atomic
def guardian_create(
    *,
    creator: CustomUser,
    email: str,
    full_name: str,
    password: str,
    school_id: int,
    phone_number: Optional[str] = None,
) -> Guardian:
    """
    Create a new Guardian with their CustomUser account.
    """
    # Validate school exists
    try:
        school = School.objects.get(id=school_id)
    except School.DoesNotExist:
        raise ValidationError({"school_id": "School not found."})
    
    # Authorization check
    if not _can_manage_school(creator, school):
        raise PermissionDenied("You don't have permission to create guardians for this school.")

    # Create the user account
    user = user_create(
        creator=creator,
        email=email,
        full_name=full_name,
        password=password,
        role=Role.GUARDIAN,
        school_id=school_id,
    )
    
    # Create the guardian profile
    guardian = Guardian(
        user=user,
        phone_number=phone_number,
    )
    
    guardian.full_clean()
    guardian.save()
    return guardian


@transaction.atomic
def guardian_update(*, guardian: Guardian, actor: CustomUser, data: dict) -> Guardian:
    """
    Update guardian profile fields.
    """
    if not _has_school_access(actor, guardian.user.school):
        if actor.id != guardian.user_id:
            raise PermissionDenied("You don't have permission to update this guardian.")

    for field, value in data.items():
        if hasattr(guardian, field):
            setattr(guardian, field, value)
    
    guardian.full_clean()
    guardian.save()
    return guardian


@transaction.atomic
def guardian_deactivate(*, guardian: Guardian, actor: CustomUser) -> None:
    """
    Deactivate a guardian (soft delete).
    """
    if not _can_manage_school(actor, guardian.user.school):
        raise PermissionDenied("You don't have permission to deactivate this guardian.")

    if not guardian.is_active:
        raise ValidationError("Guardian already deactivated.")

    # Deactivate associated user
    guardian.user.deactivate(user=actor)

    # Deactivate guardian profile
    guardian.deactivate(user=actor)


@transaction.atomic
def guardian_activate(*, guardian: Guardian, actor: CustomUser) -> None:
    """
    Activate a guardian.
    """
    if actor.role not in [Role.ADMIN, Role.MANAGER_WORKSTREAM, Role.MANAGER_SCHOOL]:
        raise PermissionDenied("You don't have permission to activate guardians.")

    if not _can_manage_school(actor, guardian.user.school):
        raise PermissionDenied("You don't have permission to activate guardians for this school.")

    if guardian.is_active:
        raise ValidationError("Guardian is already active.")

    # Activate associated user
    guardian.user.activate()

    # Activate guardian profile
    guardian.activate()


@transaction.atomic
def guardian_student_link_create(
    *,
    actor: CustomUser,
    guardian: Guardian,
    student: Student,
    relationship_type: str
) -> GuardianStudentLink:
    """
    Link a guardian to a student.
    """
    if not _can_manage_school(actor, guardian.user.school):
        raise PermissionDenied("You don't have permission to manage this guardian link.")

    if guardian.user.school_id != student.user.school_id:
        raise ValidationError("Guardian and student must belong to the same school.")

    link, created = GuardianStudentLink.objects.get_or_create(
        guardian=guardian,
        student=student,
        defaults={'relationship_type': relationship_type}
    )

    if not created:
        link.relationship_type = relationship_type
        link.is_active = True
        link.save()
    return link


@transaction.atomic
def guardian_student_link_deactivate(*, link: GuardianStudentLink, actor: CustomUser) -> None:
    """
    Deactivate a guardian-student link.
    """
    if not _can_manage_school(actor, link.guardian.user.school):
        raise PermissionDenied("You don't have permission to deactivate this link.")

    link.deactivate(user=actor)
