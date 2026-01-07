from django.db import transaction
from django.core.exceptions import PermissionDenied
from rest_framework.exceptions import ValidationError

from accounts.models import CustomUser
from manager.models import School, Grade, Course
from accounts.policies.user_policies import _has_school_access


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
    Create a new Course for a school and grade.

    Authorization:
        - User must have permission to manage the school

    Raises:
        PermissionDenied: If creator lacks permission
        ValidationError: If validation fails (grade, unique code)
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
def course_update(
    *,
    course: Course,
    actor: CustomUser,
    data: dict
) -> Course:
    """
    Update an existing Course.
    """
    if not _has_school_access(actor, course.school):
        raise PermissionDenied("You don't have permission to update courses for this school.")

    if "course_code" in data:
        new_code = data["course_code"]
        if Course.objects.filter(
            school=course.school, course_code=new_code
        ).exclude(id=course.id).exists():
            raise ValidationError({"course_code": "This course code already exists for this school."})
        course.course_code = new_code

    if "name" in data:
        course.name = data["name"]

    if "grade_id" in data:
        try:
            grade = Grade.objects.get(id=data["grade_id"])
            course.grade = grade
        except Grade.DoesNotExist:
            raise ValidationError({"grade_id": "Grade not found."})

    course.full_clean()
    course.save()

    return course


@transaction.atomic
def course_delete(*, course: Course, actor: CustomUser) -> None:
    """
    Delete a Course.
    """
    if not _has_school_access(actor, course.school):
        raise PermissionDenied("You don't have permission to delete courses for this school.")

    course.delete()