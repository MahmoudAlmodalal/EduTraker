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
    manager: CustomUser,
    max_user: int,
) -> WorkStream:

    if not can_create_workstream(actor=creator):
        raise PermissionDenied("Only admins can create workstreams.")

    if manager.role != Role.MANAGER_WORKSTREAM:
        raise ValidationError("Assigned manager must have MANAGER_WORKSTREAM role.")

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

    for field in allowed_fields:
        if field in data:
            setattr(workstream, field, data[field])

    workstream.full_clean()
    workstream.save()
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
