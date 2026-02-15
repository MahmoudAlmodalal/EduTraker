from django.db import transaction
from accounts.models import CustomUser, Role
from accounts.policies.user_policies import ROLE_CREATION_MATRIX
from rest_framework.exceptions import ValidationError, PermissionDenied as DRFPermissionDenied
from typing import Optional
from workstream.models import WorkStream
from reports.utils import log_activity
from django.core.exceptions import ValidationError as DjangoValidationError


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
    normalized_email = (email or "").strip()

    # Check email uniqueness against all users, including inactive (soft-deleted) ones
    existing_user = CustomUser.all_objects.filter(email=normalized_email).first()
    if existing_user:
        if existing_user.is_active:
            raise ValidationError({"email": "A user with this email already exists."})
        raise ValidationError(
            {"email": "A deactivated user with this email already exists. Reactivate the user instead of creating a new one."}
        )
    
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

    # Handle School Manager Assignment (allow replacement)
    if role == Role.MANAGER_SCHOOL and school_id:
        try:
            from school.models import School
            school = School.objects.get(id=school_id)
            # If school already has a manager, clear it (we'll assign the new one later)
            if school.manager is not None:
                old_manager = school.manager
                # Clear the old manager's school assignment
                old_manager.school_id = None
                old_manager.save(update_fields=['school_id'])
        except School.DoesNotExist:
             raise ValidationError({"school_id": "School not found."})


    user = CustomUser(
        email=normalized_email,
        full_name=full_name,
        role=role,
        work_stream_id=work_stream_id,
        school_id=school_id,
    )

    user.set_password(password)
    try:
        user.full_clean()
    except DjangoValidationError as exc:
        raise ValidationError(getattr(exc, "message_dict", {"detail": exc.messages}))
    user.save()

    # Sync WorkStream.manager field
    if role == Role.MANAGER_WORKSTREAM and work_stream_id:
        workstream = WorkStream.objects.get(id=work_stream_id)
        workstream.manager = user
        workstream.save(update_fields=['manager'])

    # Sync School.manager field
    if role == Role.MANAGER_SCHOOL and school_id:
        try:
            from school.models import School
            school = School.objects.get(id=school_id)
            school.manager = user
            school.save(update_fields=['manager'])
        except School.DoesNotExist:
            pass


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
        normalized_email = email.strip()
        existing_user = CustomUser.all_objects.filter(email=normalized_email).exclude(id=user.id).first()
        if existing_user:
            raise ValidationError({"email": "A user with this email already exists."})
        data['email'] = normalized_email

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

    # If user is becoming a manager or is a manager changing schools
    new_school_id = data.get('school_id', user.school_id) if 'school_id' in data else user.school_id
    if new_role == Role.MANAGER_SCHOOL:
        # If role changed to manager OR school changed
        is_new_manager_role = (user.role != Role.MANAGER_SCHOOL)
        is_school_change = (user.school_id != new_school_id)
        
        if (is_new_manager_role or is_school_change) and new_school_id:
             try:
                from school.models import School
                school = School.objects.get(id=new_school_id)
                # If school already has a different manager, clear it (allow replacement)
                if school.manager is not None and school.manager.id != user.id:
                    old_manager = school.manager
                    # Clear the old manager's school assignment
                    old_manager.school_id = None
                    old_manager.save(update_fields=['school_id'])
             except School.DoesNotExist:
                pass


    # Handle associated manager fields clearing 
    old_work_stream_id = user.work_stream_id
    old_school_id = user.school_id
    old_role = user.role

    for field, value in data.items():
        setattr(user, field, value)

    
    if password:
        user.set_password(password)
        
    try:
        user.full_clean()
    except DjangoValidationError as exc:
        raise ValidationError(getattr(exc, "message_dict", {"detail": exc.messages}))
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

    # Case 1b: User became a school manager or moved to new school -> Set new school manager
    if new_role == Role.MANAGER_SCHOOL and new_school_id:
         if (old_role != Role.MANAGER_SCHOOL) or (old_school_id != new_school_id):
              try:
                  from school.models import School
                  school = School.objects.get(id=new_school_id)
                  school.manager = user
                  school.save(update_fields=['manager'])
              except School.DoesNotExist:
                  pass

    # Case 2: User was manager and moved AWAY or changed role -> Clear old manager
    if old_role == Role.MANAGER_WORKSTREAM and old_work_stream_id:
         if (new_role != Role.MANAGER_WORKSTREAM) or (new_work_stream_id != old_work_stream_id):
              try:
                   old_ws = WorkStream.objects.get(id=old_work_stream_id)
                   if old_ws.manager_id == user.id:
                        old_ws.manager = None
                        old_ws.save(update_fields=['manager'])
              except WorkStream.DoesNotExist:
                   pass

    if old_role == Role.MANAGER_SCHOOL and old_school_id:
         if (new_role != Role.MANAGER_SCHOOL) or (new_school_id != old_school_id):
              try:
                   from school.models import School
                   old_school = School.objects.get(id=old_school_id)
                   if old_school.manager_id == user.id:
                        old_school.manager = None
                        old_school.save(update_fields=['manager'])
              except School.DoesNotExist:
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
    
    # If user was a school manager, clear the reference on the school
    if user.role == Role.MANAGER_SCHOOL and user.school_id:
         try:
              from school.models import School
              school = School.objects.get(id=user.school_id)
              if school.manager_id == user.id:
                   school.manager = None
                   school.save(update_fields=['manager'])
         except School.DoesNotExist:
              pass
              
    user.delete()


@transaction.atomic
def user_deactivate(*, user: CustomUser) -> CustomUser:
    """
    Deactivate a user (set is_active=False).
    """
    user.is_active = False
    user.save()

    # If user was a manager, clear the reference
    if user.role == Role.MANAGER_WORKSTREAM and user.work_stream_id:
         try:
              ws = WorkStream.objects.get(id=user.work_stream_id)
              if ws.manager_id == user.id:
                   ws.manager = None
                   ws.save(update_fields=['manager'])
         except WorkStream.DoesNotExist:
              pass

    if user.role == Role.MANAGER_SCHOOL and user.school_id:
         try:
              from school.models import School
              school = School.objects.get(id=user.school_id)
              if school.manager_id == user.id:
                   school.manager = None
                   school.save(update_fields=['manager'])
         except School.DoesNotExist:
              pass

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

    # If user is a manager, try to restore assignment
    if user.role == Role.MANAGER_WORKSTREAM and user.work_stream_id:
         try:
              ws = WorkStream.objects.get(id=user.work_stream_id)
              if ws.manager is None:
                   ws.manager = user
                   ws.save(update_fields=['manager'])
         except WorkStream.DoesNotExist:
              pass

    if user.role == Role.MANAGER_SCHOOL and user.school_id:
         try:
              from school.models import School
              school = School.objects.get(id=user.school_id)
              if school.manager is None:
                   school.manager = user
                   school.save(update_fields=['manager'])
         except School.DoesNotExist:
              pass

    return user
