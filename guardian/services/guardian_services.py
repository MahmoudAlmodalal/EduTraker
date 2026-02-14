from typing import Optional
from django.db import transaction
from django.core.exceptions import PermissionDenied
from rest_framework.exceptions import ValidationError

from accounts.models import CustomUser, Role
from accounts.services.user_services import user_create
from accounts.policies.user_policies import _can_manage_school

from guardian.models import Guardian, GuardianStudentLink
from guardian.selectors.guardian_selectors import can_access_guardian
from school.models import School
from student.models import Student


# =============================================================================
# Guardian services
# =============================================================================

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
    """Create a new Guardian with their CustomUser account."""

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
        work_stream_id=school.work_stream_id,
        school_id=school_id,
    )

    # Create the guardian profile
    guardian = Guardian(user=user, phone_number=phone_number)
    guardian.full_clean()
    guardian.save()

    return guardian


@transaction.atomic
def guardian_update(*, guardian: Guardian, actor: CustomUser, data: dict) -> Guardian:
    """Update guardian profile and (optionally) associated user fields, with strict allowlists."""

    if not can_access_guardian(actor=actor, guardian=guardian):
        raise PermissionDenied("You don't have permission to update this guardian.")

    # Only staff can change user fields; guardian self can only update phone_number.
    staff_roles = [Role.ADMIN, Role.MANAGER_WORKSTREAM, Role.MANAGER_SCHOOL, Role.SECRETARY]
    is_staff = actor.role in staff_roles

    allowed_guardian_fields = ["phone_number"]

    allowed_user_fields = ["email", "full_name"]
    if actor.role == Role.ADMIN:
        allowed_user_fields.append("school_id")

    # Update user fields
    if is_staff:
        user_changed = False
        for f in allowed_user_fields:
            if f in data:
                if f == "school_id":
                    # Admin only: validate school
                    try:
                        school = School.objects.get(id=data[f])
                    except School.DoesNotExist:
                        raise ValidationError({"school_id": "School not found."})
                    guardian.user.school = school
                    guardian.user.work_stream_id = school.work_stream_id
                elif f == "email":
                    # Check email uniqueness, excluding current user
                    normalized_email = data[f].strip().lower()
                    existing_user = CustomUser.all_objects.filter(email__iexact=normalized_email).exclude(id=guardian.user.id).first()
                    if existing_user:
                        raise ValidationError({"email": "A user with this email already exists."})
                    setattr(guardian.user, f, normalized_email)
                else:
                    setattr(guardian.user, f, data[f])
                user_changed = True

        if user_changed:
            guardian.user.full_clean()
            guardian.user.save()

    # Update guardian fields
    guardian_changed = False
    for f in allowed_guardian_fields:
        if f in data:
            setattr(guardian, f, data[f])
            guardian_changed = True

    if guardian_changed:
        guardian.full_clean()
        guardian.save()

    return guardian


@transaction.atomic
def guardian_deactivate(*, guardian: Guardian, actor: CustomUser) -> None:
    """Deactivate a guardian (soft delete)."""

    if actor.role not in [Role.ADMIN, Role.MANAGER_WORKSTREAM, Role.MANAGER_SCHOOL, Role.SECRETARY]:
        raise PermissionDenied("You don't have permission to deactivate guardians.")

    if not _can_manage_school(actor, guardian.user.school):
        raise PermissionDenied("You don't have permission to deactivate this guardian.")

    if not guardian.user.is_active:
        raise ValidationError("Guardian already deactivated.")

    guardian.user.deactivate(user=actor)
    guardian.deactivate(user=actor)


@transaction.atomic
def guardian_activate(*, guardian: Guardian, actor: CustomUser) -> None:
    """Activate a guardian."""

    if actor.role not in [Role.ADMIN, Role.MANAGER_WORKSTREAM, Role.MANAGER_SCHOOL]:
        raise PermissionDenied("You don't have permission to activate guardians.")

    if not _can_manage_school(actor, guardian.user.school):
        raise PermissionDenied("You don't have permission to activate this guardian.")

    if guardian.user.is_active:
        raise ValidationError("Guardian is already active.")

    guardian.user.activate()
    guardian.activate()


# =============================================================================
# Guardian-Student link services
# =============================================================================

@transaction.atomic
def guardian_student_link_create(
    *,
    actor: CustomUser,
    guardian: Guardian,
    student: Student,
    relationship_type: str,
    is_primary: bool = False,
    can_pickup: bool = True,
) -> GuardianStudentLink:
    """Create (or reactivate/update) a guardian-student link."""

    if actor.role not in [Role.ADMIN, Role.MANAGER_WORKSTREAM, Role.MANAGER_SCHOOL, Role.SECRETARY]:
        raise PermissionDenied("You don't have permission to manage guardian links.")

    if not _can_manage_school(actor, guardian.user.school):
        raise PermissionDenied("You don't have permission to manage this guardian link.")

    if guardian.user.school_id != student.user.school_id:
        raise ValidationError("Guardian and student must belong to the same school.")

    link, created = GuardianStudentLink.objects.get_or_create(
        guardian=guardian,
        student=student,
        defaults={
            "relationship_type": relationship_type,
            "is_primary": is_primary,
            "can_pickup": can_pickup,
        },
    )

    if not created:
        link.relationship_type = relationship_type
        link.is_primary = is_primary
        link.can_pickup = can_pickup
        # if it was soft-deleted, make it active again
        if hasattr(link, "activate"):
            link.activate()
        link.save()

    # Enforce at most one primary guardian per student (service-level rule)
    if is_primary:
        (
            GuardianStudentLink.objects
            .filter(student=student, is_primary=True)
            .exclude(id=link.id)
            .update(is_primary=False)
        )

    return link


@transaction.atomic
def guardian_student_link_update(
    *,
    actor: CustomUser,
    link: GuardianStudentLink,
    data: dict,
) -> GuardianStudentLink:
    """Update link properties (relationship_type, is_primary, can_pickup)."""

    if actor.role not in [Role.ADMIN, Role.MANAGER_WORKSTREAM, Role.MANAGER_SCHOOL, Role.SECRETARY]:
        raise PermissionDenied("You don't have permission to manage guardian links.")

    if not _can_manage_school(actor, link.guardian.user.school):
        raise PermissionDenied("You don't have permission to manage this guardian link.")

    allowed_fields = ["relationship_type", "is_primary", "can_pickup"]

    for f in allowed_fields:
        if f in data:
            setattr(link, f, data[f])

    link.full_clean()
    link.save()

    # Enforce primary uniqueness
    if data.get("is_primary") is True:
        (
            GuardianStudentLink.objects
            .filter(student=link.student, is_primary=True)
            .exclude(id=link.id)
            .update(is_primary=False)
        )

    return link


@transaction.atomic
def guardian_student_link_deactivate(*, link: GuardianStudentLink, actor: CustomUser) -> None:
    """Deactivate a guardian-student link."""

    if actor.role not in [Role.ADMIN, Role.MANAGER_WORKSTREAM, Role.MANAGER_SCHOOL, Role.SECRETARY]:
        raise PermissionDenied("You don't have permission to deactivate guardian links.")

    if not _can_manage_school(actor, link.guardian.user.school):
        raise PermissionDenied("You don't have permission to deactivate this link.")

    link.deactivate(user=actor)
