from django.db import transaction
from django.core.exceptions import ValidationError
from rest_framework.exceptions import PermissionDenied, ValidationError as DRFValidationError
from .models import CustomUser, Role
from workstream.models import WorkStream
from school.models import School

from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import PermissionDenied, ValidationError as DRFValidationError
from .models import CustomUser, Role
from workstream.models import WorkStream
from school.models import School
# Import selectors to fetch users safely before update/delete
from . import selectors 

# ==========================================
# 1. STRICT SOURCE OF TRUTH (RBAC MAP)
# ==========================================
# Key: Actor's Role -> Value: List of roles they can Create/Update/Delete
ALLOWED_MANAGEABLE_ROLES = {
    Role.ADMIN: [
        Role.ADMIN, Role.MANAGER_WORKSTREAM, Role.MANAGER_SCHOOL, 
        Role.TEACHER, Role.SECRETARY, Role.STUDENT, Role.GUARDIAN, Role.GUEST
    ],
    Role.MANAGER_WORKSTREAM: [Role.MANAGER_SCHOOL, Role.TEACHER, Role.SECRETARY, Role.STUDENT, Role.GUARDIAN],
    Role.MANAGER_SCHOOL: [Role.TEACHER, Role.SECRETARY, Role.STUDENT, Role.GUARDIAN],
    Role.SECRETARY: [Role.STUDENT, Role.GUARDIAN],
}

def _validate_rbac_permission(actor: CustomUser, target_role: str):
    """
    Centralized validator to check if actor is allowed to manage the target role.
    """
    # 1. Check if actor has any management rights
    if actor.role not in ALLOWED_MANAGEABLE_ROLES:
         raise PermissionDenied(f"Role '{actor.get_role_display()}' is not authorized to manage users.")

    # 2. Check if specific target role is allowed
    allowed_roles = ALLOWED_MANAGEABLE_ROLES[actor.role]
    if target_role not in allowed_roles:
        raise DRFValidationError({
            "role": f"Operation Forbidden: A '{actor.get_role_display()}' cannot manage a '{target_role}' account."
        })

def _validate_ownership(actor: CustomUser, work_stream_id: int = None, school_id: int = None):
    """
    Ensures the actor owns the resources they are assigning.
    Returns: (work_stream_obj, school_obj)
    """
    work_stream = None
    school = None

    # Fetch Objects if IDs are provided
    if work_stream_id:
        try:
            work_stream = WorkStream.objects.get(id=work_stream_id)
        except ObjectDoesNotExist:
            raise DRFValidationError({"work_stream_id": "Invalid Workstream ID."})

    if school_id:
        try:
            school = School.objects.get(id=school_id)
        except ObjectDoesNotExist:
            raise DRFValidationError({"school_id": "Invalid School ID."})

    # Validate Context based on Actor's Role
    if actor.role == Role.MANAGER_WORKSTREAM:
        # Must belong to actor's workstream
        if not actor.work_stream:
            raise DRFValidationError("You are not assigned to a workstream.")
        if school and school.work_stream != actor.work_stream:
            raise DRFValidationError({"school_id": "This school does not belong to your workstream."})
        # Force workstream match
        work_stream = actor.work_stream

    elif actor.role == Role.MANAGER_SCHOOL:
        # Must belong to actor's school
        if not actor.school:
             raise DRFValidationError("You are not assigned to a school.")
        # Cannot assign to other schools
        if school_id and school_id != actor.school.id:
             raise DRFValidationError({"school_id": "You cannot assign users to other schools."})
        
        school = actor.school
        work_stream = actor.school.work_stream

    elif actor.role == Role.SECRETARY:
        school = actor.school
        work_stream = actor.school.work_stream

    return work_stream, school


# ==========================================
# 2. SERVICE FUNCTIONS
# ==========================================

@transaction.atomic
def create_user(*, actor: CustomUser, email: str, full_name: str, role: str, password: str, work_stream_id: int = None, school_id: int = None) -> CustomUser:
    """
    Creates a user after strictly validating the ALLOWED_MANAGEABLE_ROLES map.
    """
    # 1. Strict Map Validation
    _validate_rbac_permission(actor, role)

    # 2. Ownership & Context Validation
    # Special Check: Admin must provide work_stream_id when creating Workstream Manager
    if actor.role == Role.ADMIN and role == Role.MANAGER_WORKSTREAM and not work_stream_id:
        raise DRFValidationError({"work_stream_id": "Admin must assign a workstream to the new Manager."})

    work_stream, school = _validate_ownership(actor, work_stream_id, school_id)

    # 3. Create
    return CustomUser.objects.create_user(
        email=email,
        full_name=full_name,
        role=role,
        password=password,
        work_stream=work_stream,
        school=school
    )


@transaction.atomic
def update_user(*, actor: CustomUser, user_id: int, data: dict) -> CustomUser:
    """
    Updates a user. strictly checks if the actor is allowed to manage 
    the user's *current* role AND the *new* role (if changing).
    """
    # 1. Fetch User (ensure existence)
    user = selectors.get_user_detail(actor=actor, user_id=user_id)

    # 2. Strict Map Validation (Can actor manage this specific user?)
    _validate_rbac_permission(actor, user.role)

    # 3. If Role is changing, validate the NEW role is also allowed
    if 'role' in data and data['role'] != user.role:
        _validate_rbac_permission(actor, data['role'])

    # 4. Handle Foreign Keys & Ownership safely
    # If IDs are passed, validate them. If not passed, keep existing.
    ws_id = data.get('work_stream_id', user.work_stream_id)
    s_id = data.get('school_id', user.school_id)
    
    # We re-run ownership validation to ensure they aren't moving a user 
    # to a school/workstream they don't own.
    work_stream, school = _validate_ownership(actor, ws_id, s_id)

    # 5. Apply Updates
    if 'work_stream_id' in data: user.work_stream = work_stream
    if 'school_id' in data: user.school = school
    
    if 'password' in data:
        user.set_password(data.pop('password'))

    for attr, value in data.items():
        if attr not in ['work_stream_id', 'school_id', 'password']:
            setattr(user, attr, value)

    user.save()
    return user


@transaction.atomic
def delete_user(*, actor: CustomUser, user_id: int) -> CustomUser:
    """
    Deletes a user after strict RBAC check.
    """
    user = selectors.get_user_detail(actor=actor, user_id=user_id)
    
    # Strict Map Validation
    _validate_rbac_permission(actor, user.role)
    
    return user.delete()


@transaction.atomic
def deactivate_user(*, actor: CustomUser, user_id: int) -> None:
    """
    Deactivates a user after strict RBAC check.
    """
    user = selectors.get_user_detail(actor=actor, user_id=user_id)
    
    # Strict Map Validation
    _validate_rbac_permission(actor, user.role)
    
    user.is_active = False
    user.save()
