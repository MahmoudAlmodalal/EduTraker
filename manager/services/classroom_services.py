from django.db import transaction
from django.core.exceptions import PermissionDenied
from rest_framework.exceptions import ValidationError

from accounts.models import CustomUser
from school.models import School, AcademicYear, Grade, ClassRoom
from teacher.models import Teacher
from accounts.policies.user_policies import _has_school_access


@transaction.atomic
def classroom_create(
    *,
    creator: CustomUser,
    school_id: int,
    academic_year_id: int,
    grade_id: int,
    classroom_name: str,
    homeroom_teacher_id: int = None
) -> ClassRoom:
    """
    Create a new ClassRoom.

    Authorization:
        - ADMIN or managers with access to the school

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
    if not _has_school_access(creator, school):
        raise PermissionDenied("You don't have permission to create classrooms for this school.")

    # Validate academic year exists and belongs to school
    try:
        academic_year = AcademicYear.objects.get(id=academic_year_id)
    except AcademicYear.DoesNotExist:
        raise ValidationError({"academic_year_id": "Academic year not found."})

    if academic_year.school_id != school_id:
        raise ValidationError({"academic_year_id": "Academic year does not belong to this school."})

    # Validate grade exists
    try:
        grade = Grade.objects.get(id=grade_id)
    except Grade.DoesNotExist:
        raise ValidationError({"grade_id": "Grade not found."})

    # Validate homeroom teacher if provided
    homeroom_teacher = None
    if homeroom_teacher_id:
        try:
            homeroom_teacher = Teacher.objects.select_related('user').get(user_id=homeroom_teacher_id)
        except Teacher.DoesNotExist:
            raise ValidationError({"homeroom_teacher_id": "Teacher not found."})

        # Validate teacher belongs to the same school
        if homeroom_teacher.user.school_id != school_id:
            raise ValidationError({"homeroom_teacher_id": "Teacher does not belong to this school."})

    # Check unique constraint
    if ClassRoom.objects.filter(
        school=school, academic_year=academic_year, classroom_name=classroom_name
    ).exists():
        raise ValidationError({"classroom_name": "A classroom with this name already exists for this school and year."})

    classroom = ClassRoom(
        school=school,
        academic_year=academic_year,
        grade=grade,
        classroom_name=classroom_name,
        homeroom_teacher=homeroom_teacher,
    )

    classroom.full_clean()
    classroom.save()

    return classroom


@transaction.atomic
def classroom_update(
    *,
    classroom: ClassRoom,
    actor: CustomUser,
    data: dict
) -> ClassRoom:
    """
    Update an existing ClassRoom.
    """
    if not _has_school_access(actor, classroom.school):
        raise PermissionDenied("You don't have permission to update classrooms for this school.")

    if "classroom_name" in data:
        new_name = data["classroom_name"]
        if ClassRoom.objects.filter(
            school=classroom.school, 
            academic_year=classroom.academic_year, 
            classroom_name=new_name
        ).exclude(id=classroom.id).exists():
            raise ValidationError({"classroom_name": "A classroom with this name already exists for this school and year."})
        classroom.classroom_name = new_name

    if "grade_id" in data:
        try:
            grade = Grade.objects.get(id=data["grade_id"])
            classroom.grade = grade
        except Grade.DoesNotExist:
            raise ValidationError({"grade_id": "Grade not found."})

    if "homeroom_teacher_id" in data:
        teacher_id = data["homeroom_teacher_id"]
        if teacher_id is None:
            classroom.homeroom_teacher = None
        else:
            try:
                teacher = Teacher.objects.select_related('user').get(user_id=teacher_id)
                if teacher.user.school_id != classroom.school_id:
                    raise ValidationError({"homeroom_teacher_id": "Teacher does not belong to this school."})
                classroom.homeroom_teacher = teacher
            except Teacher.DoesNotExist:
                raise ValidationError({"homeroom_teacher_id": "Teacher not found."})

    classroom.full_clean()
    classroom.save()

    return classroom


@transaction.atomic
def classroom_delete(*, classroom: ClassRoom, actor: CustomUser) -> None:
    """
    Delete a ClassRoom.
    """
    if not _has_school_access(actor, classroom.school):
        raise PermissionDenied("You don't have permission to delete classrooms for this school.")

    classroom.delete()
