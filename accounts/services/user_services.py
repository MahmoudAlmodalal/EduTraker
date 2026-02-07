from django.db import transaction
from accounts.models import CustomUser, Role
from accounts.policies.user_policies import ROLE_CREATION_MATRIX
from accounts.selectors.user_selectors import user_get_by_email
from rest_framework.exceptions import ValidationError, PermissionDenied as DRFPermissionDenied
from typing import Optional
from workstream.models import WorkStream
from reports.utils import log_activity


@transaction.atomic
def user_create(
    *,
    creator: CustomUser,
    email: str,
    full_name: str,
    password: str,
    role: str,
    work_stream_id: Optional[int] = None,
    school_id: Optional[int] = None,
) -> CustomUser:
    """
    Create a new CustomUser with hashed password.
    
    Validates:
    - Email uniqueness
    - Role creation permissions based on creator's role
    - Scope enforcement (workstream/school assignment)
    
    If profile_data is provided, creates the corresponding role profile
    (Secretary, Teacher, Student, Guardian).
    """
    # Check email uniqueness
    if user_get_by_email(email=email):
        raise ValidationError({"email": "A user with this email already exists."})
    
    # Check role creation permission
    allowed_roles = ROLE_CREATION_MATRIX.get(creator.role, [])
    if role not in allowed_roles:
        raise DRFPermissionDenied(
            f"You are not allowed to create users with role '{role}'."
        )

    # Scope enforcement
    if creator.role == Role.MANAGER_WORKSTREAM:
        if work_stream_id != creator.work_stream_id:
            raise DRFPermissionDenied("Invalid work stream assignment.")

    if creator.role == Role.MANAGER_SCHOOL:
        if school_id != creator.school_id:
            raise DRFPermissionDenied("Invalid school assignment.")

    if creator.role in [Role.TEACHER, Role.SECRETARY]:
        if school_id != creator.school_id:
            raise DRFPermissionDenied(
                "Secretary/Teacher can only create users in their own school."
            )
    
    # Validate Workstream Manager Singularity
    if role == Role.MANAGER_WORKSTREAM and work_stream_id:
        try:
            workstream = WorkStream.objects.get(id=work_stream_id)
            if workstream.manager is not None:
                raise ValidationError(
                    f"Workstream '{workstream.workstream_name}' already has a manager assigned ({workstream.manager.full_name})."
                )
        except WorkStream.DoesNotExist:
             raise ValidationError({"work_stream_id": "Workstream not found."})

    user = CustomUser(
        email=email,
        full_name=full_name,
        role=role,
        work_stream_id=work_stream_id,
        school_id=school_id,
    )

    user.set_password(password)
    user.full_clean()
    user.save()

    # Sync WorkStream.manager field
    if role == Role.MANAGER_WORKSTREAM and work_stream_id:
        workstream = WorkStream.objects.get(id=work_stream_id)
        workstream.manager = user
        workstream.save(update_fields=['manager'])

    # Log activity
    role_display = dict(CustomUser.ROLE_CHOICES).get(role, role)
    log_activity(
        actor=creator,
        action_type='CREATE',
        entity_type='User',
        description=f"Created {role_display}: {full_name}",
        entity_id=user.id
    )

    return user



@transaction.atomic
def user_update(*, user: CustomUser, data: dict) -> CustomUser:
    """
    Update user fields.
    """
    email = data.get('email')
    if email and email != user.email:
        if user_get_by_email(email=email):
            raise ValidationError({"email": "A user with this email already exists."})

    password = data.pop('password', None)
    
    # Check for role change OR workstream change if user is/becoming a manager
    new_role = data.get('role', user.role)
    new_work_stream_id = data.get('work_stream_id', user.work_stream_id) if 'work_stream_id' in data else user.work_stream_id
    
    # If user is becoming a manager or is a manager changing workstreams
    if new_role == Role.MANAGER_WORKSTREAM:
        # If role changed to manager OR workstream changed
        is_new_manager_role = (user.role != Role.MANAGER_WORKSTREAM)
        is_workstream_change = (user.work_stream_id != new_work_stream_id)
        
        if (is_new_manager_role or is_workstream_change) and new_work_stream_id:
             try:
                workstream = WorkStream.objects.get(id=new_work_stream_id)
                # Ensure we aren't counting the current user if they are already the manager (though condition above handles checking for change)
                if workstream.manager is not None and workstream.manager.id != user.id:
                    raise ValidationError(
                        f"Workstream '{workstream.workstream_name}' already has a manager assigned ({workstream.manager.full_name})."
                    )
             except WorkStream.DoesNotExist:
                pass # Will be handled by foreign key or subsequent save if invalid

    # Handle clearing old workstream manager if needed
    old_work_stream_id = user.work_stream_id
    old_role = user.role

    for field, value in data.items():
        setattr(user, field, value)
    
    if password:
        user.set_password(password)
        
    user.full_clean()
    user.save()

    # Sync WorkStream.manager logic
    # Case 1: User became a manager or moved to new workstream -> Set new workstream manager
    if new_role == Role.MANAGER_WORKSTREAM and new_work_stream_id:
         if (old_role != Role.MANAGER_WORKSTREAM) or (old_work_stream_id != new_work_stream_id):
              ws = WorkStream.objects.get(id=new_work_stream_id)
              ws.manager = user
              ws.save(update_fields=['manager'])
    
    # Case 2: User was manager and moved AWAY from workstream or changed role -> Clear old workstream manager
    if old_role == Role.MANAGER_WORKSTREAM and old_work_stream_id:
         # If moved to different workstream OR different role OR removed workstream
         if (new_role != Role.MANAGER_WORKSTREAM) or (new_work_stream_id != old_work_stream_id):
              try:
                   old_ws = WorkStream.objects.get(id=old_work_stream_id)
                   if old_ws.manager_id == user.id:
                        old_ws.manager = None
                        old_ws.save(update_fields=['manager'])
              except WorkStream.DoesNotExist:
                   pass

    return user


@transaction.atomic
def user_delete(*, user: CustomUser) -> None:
    """
    Delete a user record.
    """
    # If user was a workstream manager, clear the reference on the workstream
    if user.role == Role.MANAGER_WORKSTREAM and user.work_stream_id:
         try:
              ws = WorkStream.objects.get(id=user.work_stream_id)
              if ws.manager_id == user.id:
                   ws.manager = None
                   ws.save(update_fields=['manager'])
         except WorkStream.DoesNotExist:
              pass
              
    user.delete()


@transaction.atomic
def user_deactivate(*, user: CustomUser) -> CustomUser:
    """
    Deactivate a user (set is_active=False).
    """
    user.is_active = False
    user.save()
    return user

@transaction.atomic
def user_activate(*, user: CustomUser) -> CustomUser:
    """
    Activate a user (set is_active=True).
    Check workstream capacity if user belongs to one.
    """
    if user.is_active:
        return user
        
    user.is_active = True   
    user.save()
    return user
