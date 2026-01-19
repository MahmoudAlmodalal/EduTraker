from django.db import transaction
from django.core.exceptions import PermissionDenied
from rest_framework.exceptions import ValidationError
from datetime import date

from accounts.models import CustomUser, Role
from student.models import Student, StudentEnrollment
from school.models import School, ClassRoom, AcademicYear
from accounts.policies.user_policies import _can_manage_school


@transaction.atomic
def enrollment_create(
    *,
    creator: CustomUser,
    student_id: int,
    class_room_id: int,
    academic_year_id: int,
    status: str = "active",
    enrollment_date: date = None
) -> StudentEnrollment:
    """
    Create a new StudentEnrollment.
    """
    # Authorization check
    if creator.role not in [Role.ADMIN, Role.MANAGER_WORKSTREAM, Role.MANAGER_SCHOOL, Role.SECRETARY]:
        raise PermissionDenied("You don't have permission to create enrollments.")

    # Validate student exists
    try:
        student = Student.objects.select_related('user', 'user__school').get(user_id=student_id)
    except Student.DoesNotExist:
        raise ValidationError({"student_id": "Student not found."})

    # Check creator can manage this student's school
    if not _can_manage_school(creator, student.user.school):
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
    if class_room.school_id != student.user.school_id:
        raise ValidationError({"class_room_id": "Classroom does not belong to the student's school."})

    if academic_year.school_id != student.user.school_id:
        raise ValidationError({"academic_year_id": "Academic year does not belong to the student's school."})

    # Check for duplicate enrollment
    if StudentEnrollment.objects.filter(
        student=student, class_room=class_room, academic_year=academic_year
    ).exists():
        raise ValidationError({"student_id": "Student is already enrolled in this classroom for this academic year."})

    # Set enrollment_date to today if not provided
    if enrollment_date is None:
        enrollment_date = date.today()

    enrollment = StudentEnrollment(
        student=student,
        class_room=class_room,
        academic_year=academic_year,
        status=status,
        enrollment_date=enrollment_date,
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
    """
    if actor.role not in [Role.ADMIN, Role.MANAGER_WORKSTREAM, Role.MANAGER_SCHOOL, Role.SECRETARY]:
        raise PermissionDenied("You don't have permission to update enrollments.")

    # Check actor can manage this school
    if not _can_manage_school(actor, enrollment.student.user.school):
        raise PermissionDenied("You don't have permission to update enrollments in this school.")

    # Update status if provided
    if 'status' in data:
        valid_statuses = ['active', 'enrolled', 'completed', 'withdrawn', 'transferred']
        if data['status'] not in valid_statuses:
            raise ValidationError({
                "status": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            })
        enrollment.status = data['status']

    # Update completion_date if provided
    if 'completion_date' in data:
        enrollment.completion_date = data['completion_date']

    enrollment.full_clean()
    enrollment.save()

    return enrollment


@transaction.atomic
def enrollment_deactivate(*, enrollment: StudentEnrollment, actor: CustomUser) -> None:
    """
    Deactivate a StudentEnrollment (soft delete).
    """
    if actor.role not in [Role.ADMIN, Role.MANAGER_WORKSTREAM, Role.MANAGER_SCHOOL, Role.SECRETARY]:
        raise PermissionDenied("You don't have permission to deactivate enrollments.")

    # Check actor can manage this school
    if not _can_manage_school(actor, enrollment.student.user.school):
        raise PermissionDenied("You don't have permission to deactivate enrollments in this school.")

    if not enrollment.is_active:
        raise ValidationError("Enrollment already deactivated.")

    enrollment.deactivate(user=actor)


@transaction.atomic
def enrollment_activate(*, enrollment: StudentEnrollment, actor: CustomUser) -> None:
    """
    Activate a StudentEnrollment.
    """
    if actor.role not in [Role.ADMIN, Role.MANAGER_WORKSTREAM, Role.MANAGER_SCHOOL]:
        raise PermissionDenied("You don't have permission to activate enrollments.")

    # Check actor can manage this school
    if not _can_manage_school(actor, enrollment.student.user.school):
        raise PermissionDenied("You don't have permission to activate enrollments in this school.")

    if enrollment.is_active:
        raise ValidationError("Enrollment is already active.")

    enrollment.activate()