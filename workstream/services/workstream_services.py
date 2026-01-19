from __future__ import annotations
from django.db import transaction
from django.core.exceptions import ValidationError, PermissionDenied
from accounts.models import CustomUser, Role
from workstream.models import WorkStream
from accounts.policies.workstream_policies import (
    can_create_workstream,
    allowed_update_fields_for_workstream,
    can_deactivate_workstream,
)


@transaction.atomic
def workstream_create(
    *,
    creator: CustomUser,
    name: str,
    description: str | None,
    manager: CustomUser | None = None,
    max_user: int = 100,
) -> WorkStream:

    if not can_create_workstream(actor=creator):
        raise PermissionDenied("Only admins can create workstreams.")

    # Only validate manager if provided
    if manager is not None:
        if manager.role != Role.MANAGER_WORKSTREAM:
            raise ValidationError("Assigned manager must have MANAGER_WORKSTREAM role.")

        # Check if manager is already assigned to another workstream
        if manager.work_stream is not None:
            raise ValidationError("Manager is already assigned to workstream")

    if WorkStream.objects.filter(name__iexact=name).exists():
        raise ValidationError("Workstream with this name already exists.")

    workstream = WorkStream(
        name=name,
        description=description,
        manager=manager,
        max_user=max_user,
    )

    workstream.full_clean()
    workstream.save()

    # Assign the workstream to the manager's work_stream field if manager exists
    if manager is not None:
        manager.work_stream = workstream
        manager.save(update_fields=['work_stream'])

    return workstream


@transaction.atomic
def workstream_update(
    *,
    actor: CustomUser,
    workstream: WorkStream,
    data: dict,
) -> WorkStream:

    allowed_fields = allowed_update_fields_for_workstream(
        actor=actor,
        workstream=workstream,
    )

    if not allowed_fields:
        raise PermissionDenied("You do not have permission to update this workstream.")

    # Validate manager role if manager is being updated
    if "manager" in data:
        manager = data["manager"]
        if manager.role != Role.MANAGER_WORKSTREAM:
            raise ValidationError("Assigned manager must have MANAGER_WORKSTREAM role.")
        # Check if manager is already assigned to another workstream (not this one)
        if manager.work_stream is not None and manager.work_stream.id != workstream.id:
            raise ValidationError("Manager is already assigned to workstream.")

    # Validate name uniqueness if name is being updated
    if "name" in data:
        new_name = data["name"]
        if not new_name or not new_name.strip():
            raise ValidationError("Workstream name cannot be empty.")
        if WorkStream.objects.filter(name__iexact=new_name).exclude(id=workstream.id).exists():
            raise ValidationError("Workstream with this name already exists.")

    # Track if manager is being changed
    old_manager = workstream.manager if "manager" in data else None
    new_manager = data.get("manager")

    for field in allowed_fields:
        if field in data:
            setattr(workstream, field, data[field])

    workstream.full_clean()
    workstream.save()

    # Update manager's work_stream field if manager was changed
    if new_manager and new_manager != old_manager:
        # Remove workstream from old manager if exists
        if old_manager:
            old_manager.work_stream = None
            old_manager.save(update_fields=['work_stream'])
        # Assign workstream to new manager
        new_manager.work_stream = workstream
        new_manager.save(update_fields=['work_stream'])

    return workstream


@transaction.atomic
def workstream_deactivate(
    *,
    actor: CustomUser,
    workstream: WorkStream,
) -> None:

    if not can_deactivate_workstream(actor=actor, workstream=workstream):
        raise PermissionDenied("Only admins can deactivate workstreams.")

    workstream.is_active = False
    workstream.save()
