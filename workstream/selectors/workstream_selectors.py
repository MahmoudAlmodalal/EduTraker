from django.db.models import QuerySet, Count
from django.shortcuts import get_object_or_404
from workstream.models import WorkStream
from accounts.models import CustomUser, Role
from accounts.policies.workstream_policies import can_view_workstream
from django.core.exceptions import PermissionDenied

def workstream_list(*, filters: dict, user: CustomUser) -> QuerySet:
    # Bypass ActiveManager by using all_objects.filter(is_active=True)
    # This avoids potential issues with the custom manager's get_queryset overriding standard behavior
    qs = WorkStream.all_objects.annotate(
        total_users=Count("users"),
        total_schools=Count("schools")
    )

    if user.role in {Role.MANAGER_WORKSTREAM, Role.MANAGER_SCHOOL}:
        qs = qs.filter(id=user.work_stream_id)

    if search := filters.get("search"):
        qs = qs.filter(workstream_name__icontains=search)
    
    is_active = filters.get("is_active")
    if is_active is None:
        is_active = True
    
    qs = qs.filter(is_active=is_active)

    return qs


def workstream_get(*, workstream_id: int, actor: CustomUser) -> WorkStream:
    workstream = get_object_or_404(WorkStream.all_objects, id=workstream_id)

    if not can_view_workstream(actor=actor, workstream=workstream):
        raise PermissionDenied("You do not have access to this workstream.")

    return workstream
