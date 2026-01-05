"""
Enrollment services for creating, updating, and deleting StudentEnrollment entities.

All business logic, permission checks, validations, and workflows are centralized here.
Services use @transaction.atomic for data-modifying operations.
"""
from django.db import transaction
from django.core.exceptions import PermissionDenied
from rest_framework.exceptions import ValidationError

from accounts.models import CustomUser, Role
from student.models import Student, StudentEnrollment
from manager.models import School, ClassRoom, AcademicYear
from accounts.policies.user_policies import _can_manage_school


@transaction.atomic
def enrollment_create(
    *,
    creator: CustomUser,
    student_id: int,
    class_room_id: int,
    academic_year_id: int,
    status: str = "enrolled"
) -> StudentEnrollment:
    """
    Create a new StudentEnrollment.

    Authorization:
        ADMIN, MANAGER_SCHOOL, SECRETARY can create enrollments.

    Validates:
        - Student, ClassRoom, AcademicYear exist
        - All belong to the same school
        - No duplicate enrollment (unique constraint)
    """
    # Authorization check
    if creator.role not in [Role.ADMIN, Role.MANAGER_WORKSTREAM, Role.MANAGER_SCHOOL, Role.SECRETARY]:
        raise PermissionDenied("You don't have permission to create enrollments.")

    # Validate student exists
    try:
        student = Student.objects.select_related('school').get(user_id=student_id)
    except Student.DoesNotExist:
        raise ValidationError({"student_id": "Student not found."})

    # Check creator can manage this student's school
    if not _can_manage_school(creator, student.school):
        raise PermissionDenied("You don't have permission to enroll students in this school.")

    # Validate classroom exists
    try:
        class_room = ClassRoom.objects.select_related('school', 'academic_year').get(id=class_room_id)
    except ClassRoom.DoesNotExist:
        raise ValidationError({"class_room_id": "Classroom not found."})

    # Validate academic year exists
    try:
        academic_year = AcademicYear.objects.select_related('school').get(id=academic_year_id)
    except AcademicYear.DoesNotExist:
        raise ValidationError({"academic_year_id": "Academic year not found."})

    # Validate all belong to the same school
    if class_room.school_id != student.school_id:
        raise ValidationError({"class_room_id": "Classroom does not belong to the student's school."})

    if academic_year.school_id != student.school_id:
        raise ValidationError({"academic_year_id": "Academic year does not belong to the student's school."})

    # Check for duplicate enrollment
    if StudentEnrollment.objects.filter(student=student, class_room=class_room).exists():
        raise ValidationError({"student_id": "Student is already enrolled in this classroom."})

    enrollment = StudentEnrollment(
        student=student,
        class_room=class_room,
        academic_year=academic_year,
        status=status,
    )

    enrollment.full_clean()
    enrollment.save()

    return enrollment


@transaction.atomic
def enrollment_update(
    *,
    enrollment: StudentEnrollment,
    actor: CustomUser,
    data: dict
) -> StudentEnrollment:
    """
    Update a StudentEnrollment.

    Authorization:
        ADMIN, MANAGER_SCHOOL, SECRETARY can update enrollments.

    Allowed fields: status
    Valid statuses: enrolled, completed, withdrawn, transferred
    """
    if actor.role not in [Role.ADMIN, Role.MANAGER_WORKSTREAM, Role.MANAGER_SCHOOL, Role.SECRETARY]:
        raise PermissionDenied("You don't have permission to update enrollments.")

    # Check actor can manage this school
    if not _can_manage_school(actor, enrollment.student.school):
        raise PermissionDenied("You don't have permission to update enrollments in this school.")

    # Update status if provided
    if 'status' in data:
        valid_statuses = ['enrolled', 'completed', 'withdrawn', 'transferred']
        if data['status'] not in valid_statuses:
            raise ValidationError({
                "status": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            })
        enrollment.status = data['status']

    enrollment.full_clean()
    enrollment.save()

    return enrollment


@transaction.atomic
def enrollment_delete(*, enrollment: StudentEnrollment, actor: CustomUser) -> None:
    """
    Delete a StudentEnrollment.

    Authorization:
        ADMIN, MANAGER_SCHOOL, SECRETARY can delete enrollments.
    """
    if actor.role not in [Role.ADMIN, Role.MANAGER_WORKSTREAM, Role.MANAGER_SCHOOL, Role.SECRETARY]:
        raise PermissionDenied("You don't have permission to delete enrollments.")

    # Check actor can manage this school
    if not _can_manage_school(actor, enrollment.student.school):
        raise PermissionDenied("You don't have permission to delete enrollments in this school.")

    enrollment.delete()