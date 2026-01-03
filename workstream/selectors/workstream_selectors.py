from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from workstream.models import WorkStream
from accounts.models import CustomUser, Role
from django.core.exceptions import PermissionDenied


def workstream_list(*, filters: dict, user: CustomUser) -> QuerySet:
    """
    Get list of workstreams based on user role and filters.
    """
    qs = WorkStream.objects.all()
    
    # Role-based filtering
    if user.role == Role.MANAGER_WORKSTREAM:
        # Workstream managers can only see their own workstream
        qs = qs.filter(id=user.work_stream_id)
    
    elif user.role == Role.MANAGER_SCHOOL:
        # School managers can only see their school's workstream
        if user.work_stream_id:
            qs = qs.filter(id=user.work_stream_id)
        else:
            qs = qs.none()
    
    # Apply filters
    if search := filters.get("search"):
        qs = qs.filter(name__icontains=search)
    
    if is_active := filters.get("is_active"):
        qs = qs.filter(is_active=is_active)
    
    return qs


def workstream_get(*, workstream_id: int, actor: CustomUser) -> WorkStream:
    """
    Get a specific workstream by ID with permission check.
    """
    workstream = get_object_or_404(WorkStream, id=workstream_id)
    
    # Permission check
    if actor.role == Role.ADMIN:
        return workstream
    
    if actor.role == Role.MANAGER_WORKSTREAM:
        if workstream.id != actor.work_stream_id:
            raise PermissionDenied("You can only access your own workstream.")
    
    elif actor.role == Role.MANAGER_SCHOOL:
        if workstream.id != actor.work_stream_id:
            raise PermissionDenied("You can only access your school's workstream.")
    
    else:
        raise PermissionDenied("You don't have permission to access workstreams.")
    
    return workstream