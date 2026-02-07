from django.db.models import QuerySet, Q
from accounts.models import CustomUser, Role
from django.shortcuts import get_object_or_404
from accounts.policies.user_policies import can_access_user
from rest_framework.exceptions import ValidationError, PermissionDenied as DRFPermissionDenied
from typing import Optional, Dict, Any
from django.db.models.functions import Lower


def user_list(*, filters: dict, user: CustomUser) -> QuerySet[CustomUser]:
    """
    Get a filtered list of users based on the actor's role and permissions.
    """
    qs = CustomUser.all_objects.all()

    if user.role == Role.MANAGER_WORKSTREAM:
        qs = qs.filter(work_stream=user.work_stream)

    elif user.role in [Role.TEACHER, Role.SECRETARY, Role.MANAGER_SCHOOL]:
        # Staff can see Students, Guardians, and other Staff in their school
        qs = qs.filter(school=user.school)

    elif user.role in [Role.STUDENT, Role.GUARDIAN]:
        # Students/Guardians can see Staff in their school
        qs = qs.filter(
            school=user.school,
            role__in=[Role.TEACHER, Role.SECRETARY, Role.MANAGER_SCHOOL]
        )

    if role := filters.get("role"):
        qs = qs.filter(role=role)

    if (is_active_val := filters.get("is_active")) is not None:
         qs = qs.filter(is_active=is_active_val)

    if search := filters.get("search"):
        qs = qs.annotate(
            low_full_name=Lower('full_name'),
            low_email=Lower('email')
        ).filter(
            Q(low_full_name__icontains=search.lower()) | 
            Q(low_email__icontains=search.lower())
        )

    return qs


def user_get(*, user_id: int, actor: CustomUser) -> CustomUser:
    """
    Get a single user by ID with permission check.
    """
    user = get_object_or_404(CustomUser.all_objects, id=user_id)

    if not can_access_user(actor=actor, target=user):
        raise DRFPermissionDenied("Access denied.")

    return user


def user_get_by_email(*, email: str) -> Optional[CustomUser]:
    """
    Get user by email address.
    Returns None if user does not exist.
    """
    try:
        return CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        return None


def user_get_profile(*, user_id: int, actor: CustomUser) -> Dict[str, Any]:
    """
    Get user with their role-specific profile.
    
    Returns:
        {
            'user': CustomUser,
            'profile': Student | Teacher | None,
            'profile_type': str | None
        }
    """
    user = user_get(user_id=user_id, actor=actor)
    
    profile = None
    profile_type = None
    
    if user.role == Role.STUDENT:
        try:
            profile = user.student_profile
            profile_type = 'student'
        except Exception:
            pass
    
    elif user.role == Role.TEACHER:
        try:
            profile = user.teacher_profile
            profile_type = 'teacher'
        except Exception:
            pass
    
    return {
        'user': user,
        'profile': profile,
        'profile_type': profile_type
    }