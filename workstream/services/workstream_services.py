from django.db import transaction
from django.core.exceptions import PermissionDenied, ValidationError
from workstream.models import WorkStream
from accounts.models import CustomUser, Role


@transaction.atomic
def workstream_create(
    *,
    creator: CustomUser,
    name: str,
    description: str = None,
    capacity: int = 0,
) -> WorkStream:
    """
    Create a new workstream.
    Only Admins can create workstreams.
    """
    # Permission check
    if creator.role != Role.ADMIN:
        raise PermissionDenied("Only Admins can create workstreams.")
    
    # Check if workstream name already exists
    if WorkStream.objects.filter(name=name).exists():
        raise ValidationError(f"A workstream with the name '{name}' already exists.")
    
    # Create workstream
    workstream = WorkStream(
        name=name,
        description=description,
        capacity=capacity,
        is_active=True,
    )
    
    workstream.full_clean()
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


@transaction.atomic
def workstream_delete(*, workstream: WorkStream, actor: CustomUser):
    """
    Delete a workstream.
    Only Admins can delete workstreams.
    """
    if actor.role != Role.ADMIN:
        raise PermissionDenied("Only Admins can delete workstreams.")
    
    # Check if workstream has associated users
    if workstream.users.exists():
        raise ValidationError(
            "Cannot delete workstream with associated users. "
            "Please reassign or remove users first."
        )
    
    workstream.delete()


@transaction.atomic
def workstream_deactivate(
    *,
    workstream: WorkStream,
    actor: CustomUser
) -> WorkStream:
    """
    Deactivate a workstream (soft delete).
    Only Admins can deactivate workstreams.
    """
    if actor.role != Role.ADMIN:
        raise PermissionDenied("Only Admins can deactivate workstreams.")
    
    workstream.is_active = False
    workstream.save()
    
    return workstream