"""
School services for creating, updating, and deleting School-related entities.

All business logic, validation, and permission enforcement is centralized here.
Services use @transaction.atomic for data-modifying operations.
"""
from django.db import transaction
from django.core.exceptions import PermissionDenied
from rest_framework.exceptions import ValidationError

from accounts.models import CustomUser, Role
from manager.models import School, AcademicYear, Grade, Course, ClassRoom
from workstream.models import WorkStream
from teacher.models import Teacher


def _has_school_access(user: CustomUser, school: School) -> bool:
    """Check if user has access to perform operations on the given school."""
    if user.role == Role.ADMIN:
        return True
    if user.role == Role.MANAGER_WORKSTREAM:
        return school.work_stream_id == user.work_stream_id
    if user.role == Role.MANAGER_SCHOOL:
        return school.id == user.school_id
    return False


def _can_create_in_workstream(user: CustomUser, work_stream_id: int) -> bool:
    """Check if user can create schools in the given workstream."""
    if user.role == Role.ADMIN:
        return True
    if user.role == Role.MANAGER_WORKSTREAM:
        return user.work_stream_id == work_stream_id
    return False


@transaction.atomic
def school_create(
    *,
    creator: CustomUser,
    school_name: str,
    work_stream_id: int,
    manager_id: int
) -> School:
    """
    Create a new School.

    Authorization:
        - ADMIN/SUPERADMIN: can create in any workstream
        - WORKSTREAM manager: can create only in their workstream

    Raises:
        PermissionDenied: If creator lacks permission
        ValidationError: If validation fails (unique constraints, invalid references)
    """
    # Validate workstream exists
    try:
        work_stream = WorkStream.objects.get(id=work_stream_id)
    except WorkStream.DoesNotExist:
        raise ValidationError({"work_stream_id": "WorkStream not found."})

    # Authorization check
    if not _can_create_in_workstream(creator, work_stream_id):
        raise PermissionDenied("You don't have permission to create schools in this workstream.")

    # Validate manager exists and has correct role
    try:
        manager = CustomUser.objects.get(id=manager_id)
    except CustomUser.DoesNotExist:
        raise ValidationError({"manager_id": "Manager user not found."})

    if manager.role != Role.MANAGER_SCHOOL:
        raise ValidationError({"manager_id": "Assigned manager must have MANAGER_SCHOOL role."})

    # Validate unique school name within workstream
    if School.objects.filter(
        school_name__iexact=school_name, work_stream_id=work_stream_id
    ).exists():
        raise ValidationError({"school_name": "A school with this name already exists in the workstream."})

    school = School(
        school_name=school_name,
        work_stream=work_stream,
        manager=manager,
    )

    school.full_clean()
    school.save()

    return school


@transaction.atomic
def school_update(*, school: School, actor: CustomUser, data: dict) -> School:
    """
    Update an existing School.

    Authorization:
        - ADMIN: can update any school
        - WORKSTREAM manager: can update schools in their workstream
        - SCHOOL manager: can update only their own school

    Raises:
        PermissionDenied: If actor lacks permission
        ValidationError: If validation fails
    """
    # Authorization check
    if not _has_school_access(actor, school):
        raise PermissionDenied("You don't have permission to update this school.")

    # Validate and apply updates
    if "school_name" in data:
        new_name = data["school_name"]
        # Check unique constraint
        if School.objects.filter(
            school_name__iexact=new_name,
            work_stream_id=school.work_stream_id
        ).exclude(id=school.id).exists():
            raise ValidationError({"school_name": "A school with this name already exists in the workstream."})
        school.school_name = new_name

    if "work_stream_id" in data:
        # Only admin can change workstream
        if actor.role != Role.ADMIN:
            raise PermissionDenied("Only admins can change the workstream of a school.")
        try:
            work_stream = WorkStream.objects.get(id=data["work_stream_id"])
            school.work_stream = work_stream
        except WorkStream.DoesNotExist:
            raise ValidationError({"work_stream_id": "WorkStream not found."})

    if "manager_id" in data:
        try:
            manager = CustomUser.objects.get(id=data["manager_id"])
            if manager.role != Role.MANAGER_SCHOOL:
                raise ValidationError({"manager_id": "Assigned manager must have MANAGER_SCHOOL role."})
            school.manager = manager
        except CustomUser.DoesNotExist:
            raise ValidationError({"manager_id": "Manager user not found."})

    school.full_clean()
    school.save()

    return school


@transaction.atomic
def school_delete(*, school: School, actor: CustomUser) -> None:
    """
    Delete a School.

    Authorization:
        - ADMIN: can delete any school
        - WORKSTREAM manager: can delete schools in their workstream
        - SCHOOL manager: can delete only their own school

    Raises:
        PermissionDenied: If actor lacks permission
    """
    if not _has_school_access(actor, school):
        raise PermissionDenied("You don't have permission to delete this school.")

    school.delete()


@transaction.atomic
def academic_year_create(
    *,
    creator: CustomUser,
    school_id: int,
    academic_year_code: str,
    start_date,
    end_date
) -> AcademicYear:
    """
    Create a new AcademicYear for a school.

    Authorization:
        - User must have permission to manage the school

    Raises:
        PermissionDenied: If creator lacks permission
        ValidationError: If validation fails (dates, unique code)
    """
    # Validate school exists
    try:
        school = School.objects.get(id=school_id)
    except School.DoesNotExist:
        raise ValidationError({"school_id": "School not found."})

    # Authorization check
    if not _has_school_access(creator, school):
        raise PermissionDenied("You don't have permission to create academic years for this school.")

    # Validate dates
    if start_date >= end_date:
        raise ValidationError({"start_date": "Start date must be before end date."})

    # Validate unique academic_year_code per school
    if AcademicYear.objects.filter(
        school_id=school_id, academic_year_code=academic_year_code
    ).exists():
        raise ValidationError({"academic_year_code": "This academic year code already exists for this school."})

    academic_year = AcademicYear(
        school=school,
        academic_year_code=academic_year_code,
        start_date=start_date,
        end_date=end_date,
    )

    academic_year.full_clean()
    academic_year.save()

    return academic_year


@transaction.atomic
def grade_create(
    *,
    creator: CustomUser,
    name: str,
    numeric_level: int,
    min_age: int,
    max_age: int
) -> Grade:
    """
    Create a new Grade (global).

    Authorization:
        - ADMIN only (grades are global entities)

    Raises:
        PermissionDenied: If creator is not admin
        ValidationError: If validation fails
    """
    # Authorization: admin only
    if creator.role != Role.ADMIN:
        raise PermissionDenied("Only admins can create grades.")

    # Validate age range
    if min_age > max_age:
        raise ValidationError({"min_age": "Minimum age must be less than or equal to maximum age."})

    # Validate unique numeric_level
    if Grade.objects.filter(numeric_level=numeric_level).exists():
        raise ValidationError({"numeric_level": "A grade with this numeric level already exists."})

    grade = Grade(
        name=name,
        numeric_level=numeric_level,
        min_age=min_age,
        max_age=max_age,
    )

    grade.full_clean()
    grade.save()

    return grade


@transaction.atomic
def course_create(
    *,
    creator: CustomUser,
    school_id: int,
    grade_id: int,
    course_code: str,
    name: str
) -> Course:
    """
    Create a new Course for a school.

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
        raise PermissionDenied("You don't have permission to create courses for this school.")

    # Validate grade exists
    try:
        grade = Grade.objects.get(id=grade_id)
    except Grade.DoesNotExist:
        raise ValidationError({"grade_id": "Grade not found."})

    # Validate unique course_code per school
    if Course.objects.filter(school_id=school_id, course_code=course_code).exists():
        raise ValidationError({"course_code": "This course code already exists for this school."})

    course = Course(
        school=school,
        grade=grade,
        course_code=course_code,
        name=name,
    )

    course.full_clean()
    course.save()

    return course


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
