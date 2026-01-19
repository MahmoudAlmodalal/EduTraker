"""
Student services for creating, updating, and deleting Student-related entities.

All business logic, permission checks, validations, and workflows are centralized here.
Services use @transaction.atomic for data-modifying operations.
"""
from django.db import transaction
from django.core.exceptions import PermissionDenied
from rest_framework.exceptions import ValidationError
from typing import Optional
from datetime import date

from accounts.models import CustomUser, Role
from accounts.services.user_services import user_create
from student.models import Student, StudentEnrollment
from student.selectors.student_selectors import can_access_student
from school.models import School, Grade, ClassRoom, AcademicYear
from accounts.policies.user_policies import _has_school_access, _can_manage_school


@transaction.atomic
def student_create(
    *,
    creator: CustomUser,
    email: str,
    full_name: str,
    password: str,
    school_id: int,
    grade_id: int,
    date_of_birth: date,
    admission_date: date,
    address: Optional[str] = None,
    medical_notes: Optional[str] = None,
    current_status: str = "active"
) -> Student:
    """
    Create a new Student with their CustomUser account.

    Authorization:
        ADMIN, MANAGER_WORKSTREAM, MANAGER_SCHOOL, TEACHER, SECRETARY can create students
        within their scope.

    Raises:
        PermissionDenied: If creator lacks permission
        ValidationError: If validation fails
    """
    # Validate school exists
    try:
        school = School.objects.get(id=school_id)
    except School.DoesNotExist:
        raise ValidationError({"school_id": "School not found."})

    # Authorization check
    if not _can_manage_school(creator, school):
        raise PermissionDenied("You don't have permission to create students in this school.")

    # Validate grade exists
    try:
        grade = Grade.objects.get(id=grade_id)
    except Grade.DoesNotExist:
        raise ValidationError({"grade_id": "Grade not found."})

    # Validate dates
    if admission_date < date_of_birth:
        raise ValidationError({"admission_date": "Admission date must be after date of birth."})

    # Determine work_stream from school
    work_stream_id = school.work_stream_id

    # Create the user account (with school linked to user)
    user = user_create(
        creator=creator,
        email=email,
        full_name=full_name,
        password=password,
        role=Role.STUDENT,
        work_stream_id=work_stream_id,
        school_id=school_id,
    )

    # Create the student profile (school is on user, not student)
    student = Student(
        user=user,
        date_of_birth=date_of_birth,
        admission_date=admission_date,
        current_status=current_status,
        address=address,
        medical_notes=medical_notes,
    )

    student.full_clean()
    student.save()

    # Optionally: auto-enroll in a default classroom for the grade
    # This can be added if needed

    return student


@transaction.atomic
def student_update(*, student: Student, actor: CustomUser, data: dict) -> Student:
    """
    Update a student's profile.

    Authorization:
        ADMIN: can update all fields
        MANAGER_SCHOOL: can update all fields for students in their school
        SECRETARY: can update limited fields (address, admission_date, current_status, medical_notes)

    Raises:
        PermissionDenied: If actor lacks permission
        ValidationError: If validation fails
    """
    # Check basic access
    if not can_access_student(actor=actor, student=student):
        raise PermissionDenied("You don't have permission to update this student.")

    # Define allowed fields based on role
    if actor.role in [Role.ADMIN, Role.MANAGER_WORKSTREAM, Role.MANAGER_SCHOOL]:
        allowed_fields = [
            'address', 'admission_date', 'current_status', 'medical_notes',
        ]
        allowed_user_fields = ['email', 'full_name', 'school_id']
    elif actor.role in [Role.TEACHER, Role.SECRETARY]:
        allowed_fields = ['address', 'admission_date', 'current_status', 'medical_notes']
        allowed_user_fields = []
    else:
        raise PermissionDenied("You don't have permission to update students.")

    # Handle user fields
    for field in allowed_user_fields:
        if field in data:
            if field == 'school_id':
                # Only admins can change school
                if actor.role != Role.ADMIN:
                    raise PermissionDenied("Only admins can change the school of a student.")
                try:
                    school = School.objects.get(id=data[field])
                    student.user.school = school
                except School.DoesNotExist:
                    raise ValidationError({"school_id": "School not found."})
            else:
                setattr(student.user, field, data[field])

    if any(f in data for f in allowed_user_fields):
        student.user.full_clean()
        student.user.save()

    # Handle student profile fields
    for field in allowed_fields:
        if field in data:
            setattr(student, field, data[field])

    student.full_clean()
    student.save()

    return student


@transaction.atomic
def student_delete(*, student: Student, actor: CustomUser) -> None:
    """
    Delete a student.

    Note: Always raises PermissionDenied instructing to use deactivate instead.
    """
    raise PermissionDenied("Use deactivate endpoint instead of delete.")


@transaction.atomic
def student_deactivate(*, student: Student, actor: CustomUser) -> Student:
    """
    Deactivate a student account.

    Authorization:
        ADMIN, MANAGER_SCHOOL, SECRETARY can deactivate students in their scope.

    Sets user.is_active = False and student.current_status = 'inactive'.
    """
    if not can_access_student(actor=actor, student=student):
        raise PermissionDenied("You don't have permission to deactivate this student.")

    if actor.role not in [Role.ADMIN, Role.MANAGER_WORKSTREAM, Role.MANAGER_SCHOOL, Role.SECRETARY]:
        raise PermissionDenied("You don't have permission to deactivate students.")

    student.user.is_active = False
    student.user.save()

    student.current_status = "inactive"
    student.save()

    return student
