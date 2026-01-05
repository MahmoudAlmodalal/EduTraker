from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied as DRFPermissionDenied
from typing import Optional, Dict

from accounts.models import CustomUser, Role
from student.models import Student
from manager.models import School


def student_list_by_school(
    *,
    school_id: int,
    actor: CustomUser,
    filters: Optional[Dict] = None
) -> QuerySet[Student]:
    """
    Get a list of students filtered by school.
    
    Args:
        school_id: The school ID to filter by
        actor: The user requesting the data
        filters: Optional additional filters (status, search, grade_id)
    
    Returns:
        QuerySet[Student]: Filtered students
    
    Raises:
        PermissionDenied: If actor lacks permission to view this school's students
    """
    filters = filters or {}
    
    # Permission check
    if actor.role == Role.ADMIN:
        pass  # Admin can view any school
    elif actor.role == Role.MANAGER_WORKSTREAM:
        # Must be same workstream
        school = School.objects.filter(id=school_id).first()
        if not school or school.work_stream_id != actor.work_stream_id:
            raise DRFPermissionDenied("Access denied. School not in your workstream.")
    elif actor.role in [Role.MANAGER_SCHOOL, Role.TEACHER, Role.SECRETARY]:
        if actor.school_id != school_id:
            raise DRFPermissionDenied("Access denied. You can only view your own school's students.")
    else:
        raise DRFPermissionDenied("Access denied.")
    
    qs = Student.objects.filter(school_id=school_id).select_related('user', 'grade')
    
    # Apply filters
    if status := filters.get("status"):
        qs = qs.filter(current_status=status)
    
    if search := filters.get("search"):
        qs = qs.filter(user__full_name__icontains=search)
    
    if grade_id := filters.get("grade_id"):
        qs = qs.filter(grade_id=grade_id)
    
    return qs


def student_get(*, student_id: int, actor: CustomUser) -> Student:
    """
    Get a single student by user ID with permission check.
    
    Args:
        student_id: The student's user ID (primary key)
        actor: The user requesting the data
    
    Returns:
        Student: The student profile
    
    Raises:
        Http404: If student not found
        PermissionDenied: If actor lacks permission
    """
    student = get_object_or_404(Student.objects.select_related('user', 'grade', 'school'), user_id=student_id)
    
    # Permission check
    if actor.role == Role.ADMIN:
        return student
    
    if actor.role == Role.MANAGER_WORKSTREAM:
        if student.school.work_stream_id != actor.work_stream_id:
            raise DRFPermissionDenied("Access denied. Student not in your workstream.")
        return student
    
    if actor.role in [Role.MANAGER_SCHOOL, Role.TEACHER, Role.SECRETARY]:
        if student.school_id != actor.school_id:
            raise DRFPermissionDenied("Access denied. Student not in your school.")
        return student
    
    if actor.role == Role.STUDENT:
        if actor.id == student_id:
            return student
        raise DRFPermissionDenied("Access denied.")
    
    raise DRFPermissionDenied("Access denied.")


def student_list(*, actor: CustomUser, filters: Optional[Dict] = None) -> QuerySet[Student]:
    """
    Get a list of all students the actor has access to.
    """
    filters = filters or {}
    
    qs = Student.objects.select_related('user', 'grade', 'school')
    
    # Role-based filtering
    if actor.role == Role.ADMIN:
        pass  # Can see all
    elif actor.role == Role.MANAGER_WORKSTREAM:
        qs = qs.filter(school__work_stream_id=actor.work_stream_id)
    elif actor.role in [Role.MANAGER_SCHOOL, Role.TEACHER, Role.SECRETARY]:
        qs = qs.filter(school_id=actor.school_id)
    else:
        qs = qs.none()
    
    # Apply filters
    if status := filters.get("status"):
        qs = qs.filter(current_status=status)
    
    if search := filters.get("search"):
        qs = qs.filter(user__full_name__icontains=search)
    
    return qs
