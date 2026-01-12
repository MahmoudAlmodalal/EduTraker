from django.db import transaction
from accounts.models import CustomUser, Role
from accounts.policies.user_policies import ROLE_CREATION_MATRIX
from accounts.selectors.user_selectors import user_get_by_email
from rest_framework.exceptions import ValidationError, PermissionDenied as DRFPermissionDenied
from typing import Optional
from workstream.models import WorkStream


def check_workstream_capacity(work_stream_id: int) -> None:
    """
    Check if a workstream has reached its maximum capacity.
    """
    work_stream = WorkStream.objects.get(id=work_stream_id)
    current_active_users = CustomUser.objects.filter(
        work_stream_id=work_stream_id, 
        is_active=True
    ).count()
    
    if current_active_users >= work_stream.max_user:
        raise ValidationError(
            {"work_stream": f"Workstream '{work_stream.name}' has reached its maximum capacity of {work_stream.max_user} active users."}
        )


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
    profile_data: Optional[dict] = None,
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
    
    # Check workstream capacity
    if work_stream_id:
        check_workstream_capacity(work_stream_id)

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

    # Create role-specific profile if profile_data is provided
    if profile_data:
        _create_role_profile(user=user, role=role, profile_data=profile_data, school_id=school_id)

    return user


def _create_role_profile(*, user: CustomUser, role: str, profile_data: dict, school_id: Optional[int] = None) -> None:
    """
    Create role-specific profile record based on user role.
    """
    from secretary.models import Secretary
    from teacher.models import Teacher
    from student.models import Student
    from guardian.models import Guardian

    if role == Role.SECRETARY:
        # Required: department, hire_date
        Secretary.objects.create(
            user=user,
            department=profile_data.get("department", ""),
            office_number=profile_data.get("office_number"),
            hire_date=profile_data.get("hire_date"),
        )

    elif role == Role.TEACHER:
        # Required: hire_date, employment_status
        Teacher.objects.create(
            user=user,
            specialization=profile_data.get("specialization"),
            hire_date=profile_data.get("hire_date"),
            employment_status=profile_data.get("employment_status", "full_time"),
            highest_degree=profile_data.get("highest_degree"),
            years_of_experience=profile_data.get("years_of_experience"),
            office_location=profile_data.get("office_location"),
        )

    elif role == Role.STUDENT:
        # Required: school, date_of_birth, admission_date
        from school.models import School, Grade
        school = School.objects.get(id=school_id) if school_id else None
        grade = None
        if profile_data.get("grade_id"):
            grade = Grade.objects.get(id=profile_data["grade_id"])
        
        Student.objects.create(
            user=user,
            school=school,
            grade=grade,
            date_of_birth=profile_data.get("date_of_birth"),
            admission_date=profile_data.get("admission_date"),
            current_status=profile_data.get("current_status", "active"),
            address=profile_data.get("address"),
            medical_notes=profile_data.get("medical_notes"),
        )

    elif role == Role.GUARDIAN:
        # Optional: phone_number
        Guardian.objects.create(
            user=user,
            phone_number=profile_data.get("phone_number"),
        )


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
    
    # Check capacity if changing workstream OR if activating an inactive user
    new_workstream_id = data.get('work_stream_id')
    is_activating = data.get('is_active') is True and not user.is_active

    if new_workstream_id and new_workstream_id != user.work_stream_id:
        check_workstream_capacity(new_workstream_id)
    elif is_activating and user.work_stream_id:
        check_workstream_capacity(user.work_stream_id)

    for field, value in data.items():
        setattr(user, field, value)
    
    if password:
        user.set_password(password)
        
    user.full_clean()
    user.save()
    return user


@transaction.atomic
def user_delete(*, user: CustomUser) -> None:
    """
    Delete a user record.
    """
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
        
    if user.work_stream_id:
        check_workstream_capacity(user.work_stream_id)
        
    user.is_active = True   
    user.save()
    return user
