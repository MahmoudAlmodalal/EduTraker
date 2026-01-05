from __future__ import annotations

from django.db import transaction
from django.core.exceptions import ValidationError, PermissionDenied
from accounts.models import CustomUser, Role
from workstream.models import WorkStream

@transaction.atomic
def workstream_create(
    *,
    creator: CustomUser,
    name: str,

    description: str | None,
    manager: CustomUser,
    max_user: int,
) -> WorkStream:
    """
    Create a new workstream.
    """
    # Only admins can create workstreams
    if creator.role != Role.ADMIN:
        raise PermissionDenied("Only admins can create workstreams.")

    # Manager role validation
    if manager.role != Role.MANAGER_WORKSTREAM:
        raise ValidationError("Assigned manager must have MANAGER_WORKSTREAM role.")

    # Prevent duplicate names (business-level uniqueness)
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
def workstream_deactivate(
    *,
    actor: CustomUser,
    workstream: WorkStream,
) -> WorkStream:
    """
    Deactivate a workstream.
    """
    if actor.role != Role.ADMIN:
        raise PermissionDenied("Only admins can deactivate workstreams.")

    workstream.is_active = False
    workstream.save()

    return workstream


@transaction.atomic
def workstream_update(
    *,
    workstream: WorkStream,
    actor: CustomUser,
    data: dict
) -> WorkStream:
    """
    Update workstream details.
    Admins can update any workstream.
    Workstream managers can update their own workstream (limited fields).
    """
    # Permission check
    if actor.role == Role.ADMIN:
        # Admins can update all fields
        allowed_fields = ['name', 'description', 'capacity', 'is_active']
    elif actor.role == Role.MANAGER_WORKSTREAM:
        # Workstream managers can only update limited fields of their own workstream
        if workstream.id != actor.work_stream_id:
            raise PermissionDenied("You can only update your own workstream.")
        allowed_fields = ['description']
    else:
        raise PermissionDenied("You don't have permission to update workstreams.")
    
    # Update allowed fields
    for field, value in data.items():
        if field in allowed_fields:
            setattr(workstream, field, value)
    
    workstream.full_clean()
    workstream.save()
    
    return workstream
 
