from django.db import transaction
from rest_framework.exceptions import ValidationError, PermissionDenied
from datetime import date
from typing import Optional

from teacher.models import Attendance, Teacher, CourseAllocation
from student.models import Student
from accounts.models import CustomUser, Role
from accounts.policies.user_policies import _has_school_access


@transaction.atomic
def attendance_record(
    *,
    teacher: Teacher,
    student: Student,
    course_allocation: CourseAllocation,
    date: date,
    status: str,
    note: Optional[str] = None
) -> Attendance:
    """
    Record attendance for a student.
    """
    # Permission check: Teacher must be assigned to this allocation
    if course_allocation.teacher != teacher:
        raise PermissionDenied("You are not assigned to this course allocation.")

    # Check for existing record
    attendance, created = Attendance.objects.get_or_create(
        student=student,
        course_allocation=course_allocation,
        date=date,
        defaults={'status': status, 'note': note, 'recorded_by': teacher}
    )

    if not created:
        attendance.status = status
        attendance.note = note
        attendance.recorded_by = teacher
        attendance.is_active = True
        attendance.save()

    return attendance


@transaction.atomic
def attendance_deactivate(*, attendance: Attendance, actor: CustomUser) -> None:
    """
    Deactivate an attendance record.
    """
    # Ownership or management
    is_owner = hasattr(actor, 'teacher_profile') and attendance.recorded_by == actor.teacher_profile
    if not (is_owner or actor.role == Role.ADMIN):
        raise PermissionDenied("You don't have permission to deactivate this attendance record.")

    if not attendance.is_active:
        raise ValidationError("Attendance record already deactivated.")

    attendance.deactivate(user=actor)


@transaction.atomic
def attendance_activate(*, attendance: Attendance, actor: CustomUser) -> None:
    """
    Activate an attendance record.
    """
    if actor.role not in [Role.ADMIN, Role.MANAGER_WORKSTREAM, Role.MANAGER_SCHOOL]:
        raise PermissionDenied("You don't have permission to activate attendance records.")

    if attendance.is_active:
        raise ValidationError("Attendance record is already active.")

    attendance.activate()
