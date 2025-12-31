from django.db.models import QuerySet, Q
from accounts.models import CustomUser, Role
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from accounts.services.user_services import can_access_user
def user_list(*, filters: dict, user: CustomUser):
    qs = CustomUser.objects.all()

    if user.role == Role.MANAGER_WORKSTREAM:
        qs = qs.filter(work_stream=user.work_stream)

    elif user.role == Role.MANAGER_SCHOOL:
        qs = qs.filter(school=user.school)

    elif user.role in [Role.TEACHER, Role.SECRETARY]:
        qs = qs.filter(role__in=[Role.GUARDIAN, Role.STUDENT])

    if role := filters.get("role"):
        qs = qs.filter(role=role)

    if search := filters.get("search"):
        qs = qs.filter(full_name__icontains=search)

    return qs



def user_get(*, user_id: int, actor: CustomUser) -> CustomUser:
    user = get_object_or_404(CustomUser, id=user_id)

    if not can_access_user(actor=actor, target=user):
        raise PermissionDenied("Access denied.")

    return user
