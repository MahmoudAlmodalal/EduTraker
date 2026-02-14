from __future__ import annotations
from django.core.exceptions import PermissionDenied, ValidationError
from school.models import School
from accounts.policies.school_policies import (
    can_create_school,
    can_update_school,
    can_deactivate_school,
)
from accounts.models import CustomUser, Role
from workstream.models import WorkStream

UNSET = object()


def check_workstream_school_capacity(work_stream_id: int) -> None:
    """
    Check if a workstream has reached its maximum school capacity as per SRS 7.2.2.
    """
    work_stream = WorkStream.objects.get(id=work_stream_id)
    current_active_schools = School.objects.filter(
        work_stream_id=work_stream_id, 
        is_active=True
    ).count()
    
    if current_active_schools >= work_stream.capacity:
        raise ValidationError(
            {"work_stream": f"Workstream '{work_stream.workstream_name}' has reached its maximum capacity of {work_stream.capacity} active schools."}
        )


def create_school(
    *,
    actor: CustomUser,
    school_name: str,
    work_stream: WorkStream,
    manager=None,
    location: str | None = None,
    capacity: int | None = None,
) -> School:
    if not can_create_school(actor=actor, work_stream_id=work_stream.id):
        raise PermissionDenied("Not allowed to create school in this workstream.")

    if not school_name:
        raise ValidationError("school_name is required.")

    # Check capacity
    check_workstream_school_capacity(work_stream.id)

    return School.objects.create(
        school_name=school_name,
        work_stream=work_stream,
        manager=manager,
        location=location,
        capacity=capacity,
        is_active=True,
    )


def update_school(
    *,
    actor: CustomUser,
    school: School,
    school_name: str | None | object = UNSET,
    manager=None,
    location: str | None | object = UNSET,
    capacity: int | None | object = UNSET,
) -> School:
    if not can_update_school(actor=actor, school=school):
        raise PermissionDenied("Not allowed to update this school.")

    if school_name is not UNSET:
        school.school_name = school_name

    if location is not UNSET:
        school.location = location

    if capacity is not UNSET:
        school.capacity = capacity

    if manager is not None:
        school.manager = manager

    school.save()
    return school


def deactivate_school(*, actor: CustomUser, school: School) -> School:
    if not can_deactivate_school(actor=actor, school=school):
        raise PermissionDenied("Not allowed to deactivate this school.")

    if not school.is_active:
        raise ValidationError("School already deactivated.")

    school.deactivate(user=actor)
    return school


def activate_school(*, actor: CustomUser, school: School) -> School:
    # Admin/WorkstreamManager can activate
    if actor.role not in [Role.ADMIN, Role.MANAGER_WORKSTREAM]:
         raise PermissionDenied("Only Admins or Workstream Managers can activate schools.")

    if school.is_active:
        raise ValidationError("School is already active.")

    # Check capacity
    check_workstream_school_capacity(school.work_stream_id)

    school.activate()
    return school
