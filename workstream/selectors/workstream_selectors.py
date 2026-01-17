from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from workstream.models import WorkStream
from accounts.models import CustomUser, Role
from accounts.policies.workstream_policies import can_view_workstream
from django.core.exceptions import PermissionDenied

def workstream_list(*, filters: dict, user: CustomUser) -> QuerySet:
    qs = WorkStream.objects.all()

    if user.role in {Role.MANAGER_WORKSTREAM, Role.MANAGER_SCHOOL}:
        qs = qs.filter(id=user.work_stream_id)

    if search := filters.get("search"):
        qs = qs.filter(name__icontains=search)

    if (is_active := filters.get("is_active")) is not None:
        qs = qs.filter(is_active=is_active)

    return qs


def workstream_get(*, workstream_id: int, actor: CustomUser) -> WorkStream:
    workstream = get_object_or_404(WorkStream, id=workstream_id)

    if not can_view_workstream(actor=actor, workstream=workstream):
        raise PermissionDenied("You do not have access to this workstream.")

    return workstream
