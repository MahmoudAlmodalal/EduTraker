from django.db import transaction
from django.db.models import QuerySet
from datetime import date
from rest_framework.exceptions import ValidationError, PermissionDenied as DRFPermissionDenied
from typing import Optional

from accounts.models import CustomUser, Role
from accounts.services.user_services import user_create
from student.models import Student
from manager.models import School, Grade


@transaction.atomic
def student_create(
    *,
    creator: CustomUser,
    email: str,
    full_name: str,
    password: str,
    school_id: int,
    date_of_birth: date,
    admission_date: date,
    grade_id: Optional[int] = None,
    address: Optional[str] = None,
    medical_notes: Optional[str] = None,
) -> Student:
    """
    Create a new Student with their CustomUser account.
    
    This is an atomic operation that:
    1. Creates the CustomUser with STUDENT role
    2. Creates the Student profile linked to the user
    
    Args:
        creator: The user creating this student
        email: Student's email address
        full_name: Student's full name
        password: Account password
        school_id: ID of the school
        date_of_birth: Student's date of birth
        admission_date: Date of admission
        grade_id: Optional grade ID
        address: Optional address
        medical_notes: Optional medical notes
    
    Returns:
        Student: The created student profile
    
    Raises:
        ValidationError: If validation fails
        PermissionDenied: If creator lacks permission
    """
    # Validate school exists
    try:
        school = School.objects.get(id=school_id)
    except School.DoesNotExist:
        raise ValidationError({"school_id": "School not found."})
    
    # Get grade if provided
    grade = None
    if grade_id:
        try:
            grade = Grade.objects.get(id=grade_id)
        except Grade.DoesNotExist:
            raise ValidationError({"grade_id": "Grade not found."})
    
    # Determine work_stream from school
    work_stream_id = school.work_stream_id
    
    # Create the user account
    user = user_create(
        creator=creator,
        email=email,
        full_name=full_name,
        password=password,
        role=Role.STUDENT,
        work_stream_id=work_stream_id,
        school_id=school_id,
    )
    
    # Create the student profile
    student = Student(
        user=user,
        school=school,
        grade=grade,
        date_of_birth=date_of_birth,
        admission_date=admission_date,
        current_status="active",
        address=address,
        medical_notes=medical_notes,
    )
    
    student.full_clean()
    student.save()
    
    return student


@transaction.atomic
def student_update(*, student: Student, data: dict) -> Student:
    """
    Update student profile fields.
    """
    for field, value in data.items():
        if hasattr(student, field):
            setattr(student, field, value)
    
    student.full_clean()
    student.save()
    return student


@transaction.atomic
def student_deactivate(*, student: Student) -> Student:
    """
    Deactivate a student (set status to inactive).
    """
    student.current_status = "inactive"
    student.save()
    return student
