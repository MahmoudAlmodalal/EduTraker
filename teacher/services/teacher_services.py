from django.db import transaction
from datetime import date
from rest_framework.exceptions import ValidationError, PermissionDenied as DRFPermissionDenied
from typing import Optional

from accounts.models import CustomUser, Role
from accounts.services.user_services import user_create
from teacher.models import Teacher
from school.models import School


@transaction.atomic
def teacher_create(
    *,
    creator: CustomUser,
    email: str,
    full_name: str,
    password: str,
    school_id: int,
    hire_date: date,
    employment_status: str,
    specialization: Optional[str] = None,
    highest_degree: Optional[str] = None,
    years_of_experience: Optional[int] = None,
    office_location: Optional[str] = None,
) -> Teacher:
    """
    Create a new Teacher with their CustomUser account.
    
    This is an atomic operation that:
    1. Creates the CustomUser with TEACHER role
    2. Creates the Teacher profile linked to the user
    
    Args:
        creator: The user creating this teacher
        email: Teacher's email address
        full_name: Teacher's full name
        password: Account password
        school_id: ID of the school
        hire_date: Date of hire
        employment_status: Employment status (full_time, part_time, contract, substitute)
        specialization: Optional teaching specialization
        highest_degree: Optional highest educational degree
        years_of_experience: Optional years of teaching experience
        office_location: Optional office location
    
    Returns:
        Teacher: The created teacher profile
    
    Raises:
        ValidationError: If validation fails
        PermissionDenied: If creator lacks permission
    """
    # Validate school exists
    try:
        school = School.objects.get(id=school_id)
    except School.DoesNotExist:
        raise ValidationError({"school_id": "School not found."})
    
    # Validate employment_status
    valid_statuses = ["full_time", "part_time", "contract", "substitute"]
    if employment_status not in valid_statuses:
        raise ValidationError({
            "employment_status": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        })
    
    # Determine work_stream from school
    work_stream_id = school.work_stream_id
    
    # Create the user account
    user = user_create(
        creator=creator,
        email=email,
        full_name=full_name,
        password=password,
        role=Role.TEACHER,
        work_stream_id=work_stream_id,
        school_id=school_id,
    )
    
    # Create the teacher profile
    teacher = Teacher(
        user=user,
        specialization=specialization,
        hire_date=hire_date,
        employment_status=employment_status,
        highest_degree=highest_degree,
        years_of_experience=years_of_experience,
        office_location=office_location,
    )
    
    teacher.full_clean()
    teacher.save()
    
    return teacher


@transaction.atomic
def teacher_update(*, teacher: Teacher, data: dict) -> Teacher:
    """
    Update teacher profile fields.
    """
    for field, value in data.items():
        if hasattr(teacher, field):
            setattr(teacher, field, value)
    
    teacher.full_clean()
    teacher.save()
    return teacher
