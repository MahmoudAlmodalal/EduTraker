from django.core.exceptions import PermissionDenied, ValidationError
from school.models import School
from accounts.policies.school_policies import (
    can_create_school,
    can_update_school,
    can_deactivate_school,
)
from accounts.models import CustomUser
from workstream.models import WorkStream


def create_school(*, actor: CustomUser, school_name: str, work_stream: WorkStream, manager=None) -> School: 
    if not can_create_school(actor=actor, work_stream_id=work_stream.id):
        raise PermissionDenied("Not allowed to create school in this workstream.")

    if not school_name:
        raise ValidationError("school_name is required.")

    return School.objects.create(
        school_name=school_name,
        work_stream=work_stream,
        manager=manager,
        is_active=True,
    )


def update_school(*, actor: CustomUser, school: School, school_name: str | None = None, manager=None) -> School:
    if not can_update_school(actor=actor, school=school):
        raise PermissionDenied("Not allowed to update this school.")

    if school_name is not None:
        school.school_name = school_name

    if manager is not None:
        school.manager = manager

    school.save()
    return school


def deactivate_school(*, actor: CustomUser, school: School) -> School:
    if not can_deactivate_school(actor=actor, school=school):
        raise PermissionDenied("Not allowed to deactivate this school.")

    if not school.is_active:
        raise ValidationError("School already deactivated.")

    school.is_active = False
    school.save(update_fields=["is_active"])
    return school
