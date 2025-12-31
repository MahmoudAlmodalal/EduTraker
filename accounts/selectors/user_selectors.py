from django.db.models import QuerySet, Q
from accounts.models import CustomUser, Role

def user_list(*, filters: dict = None, user: CustomUser) -> QuerySet[CustomUser]:
    """
    List users with optional filtering and Row Level Security (RLS).
    """
    filters = filters or {}
    queryset = CustomUser.objects.all()

    # RLS: Enforce visibility based on the requesting user's role
    if user.role == Role.ADMIN:
        pass  # Admins see everything
    elif user.role == Role.MANAGER_WORKSTREAM:
        if user.work_stream_id:
            queryset = queryset.filter(work_stream=user.work_stream)
        else:
            queryset = queryset.none()
    elif user.role == Role.MANAGER_SCHOOL:
        if user.school_id:
            queryset = queryset.filter(school=user.school)
        else:
            queryset = queryset.none()
    else:
        # Others can only see themselves
        queryset = queryset.filter(id=user.id)

    # Search Filter
    search = filters.get('search')
    if search:
        queryset = queryset.filter(
            Q(full_name__icontains=search) |
            Q(email__icontains=search)
        )

    # Role Filter
    role = filters.get('role')
    if role:
        queryset = queryset.filter(role=role)

    return queryset


def user_get(*, user_id: int) -> CustomUser:
    """
    Fetches a single user by ID.
    """
    return CustomUser.objects.get(id=user_id)
