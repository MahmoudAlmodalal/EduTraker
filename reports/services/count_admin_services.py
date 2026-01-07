from django.db.models import Count, Q
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from datetime import timedelta
from accounts.models import CustomUser, Role
from workstream.models import WorkStream
from school.models import School, ClassRoom, Course
from teacher.models import Teacher
from student.models import Student
from typing import Dict


def _check_admin_permission(actor: CustomUser) -> None:
    """Check if actor has admin permission."""
    if actor.role != Role.ADMIN:
        raise PermissionDenied("Access denied. Admin role required.")


def get_global_statistics(*, actor: CustomUser) -> Dict:
    """
    Get global platform statistics for admin dashboard.
    
    Returns:
        {
            'total_students': int,
            'total_active_students': int,
            'total_teachers': int,
            'total_workstreams': int,
            'total_active_workstreams': int,
            'total_schools': int,
            'total_classrooms': int,
            'total_courses': int,
            'total_users': int
        }
    """
    _check_admin_permission(actor)
    
    return {
        'total_students': Student.objects.count(),
        'total_active_students': Student.objects.filter(current_status='active').count(),
        'total_teachers': Teacher.objects.count(),
        'total_workstreams': WorkStream.objects.count(),
        'total_active_workstreams': WorkStream.objects.filter(is_active=True).count(),
        'total_schools': School.objects.count(),
        'total_classrooms': ClassRoom.objects.count(),
        'total_courses': Course.objects.count(),
        'total_users': CustomUser.objects.filter(is_active=True).count()
    }


def get_students_by_workstream(*, actor: CustomUser) -> Dict:
    """
    Get student distribution across all workstreams.
    
    Returns:
        {
            'total_students': int,
            'by_workstream': [
                {
                    'workstream_id': int,
                    'workstream_name': str,
                    'is_active': bool,
                    'student_count': int,
                    'school_count': int
                }
            ]
        }
    """
    _check_admin_permission(actor)
    
    workstreams = WorkStream.objects.annotate(
        student_count=Count(
            'schools__students',
            filter=Q(schools__students__current_status='active')
        ),
        school_count=Count('schools', distinct=True)
    )
    
    by_workstream = [
        {
            'workstream_id': ws.id,
            'workstream_name': ws.name,
            'is_active': ws.is_active,
            'student_count': ws.student_count,
            'school_count': ws.school_count
        }
        for ws in workstreams
    ]
    
    total_students = sum(ws['student_count'] for ws in by_workstream)
    
    return {
        'total_students': total_students,
        'by_workstream': by_workstream
    }


def get_teachers_by_workstream(*, actor: CustomUser) -> Dict:
    """
    Get teacher count per workstream.
    
    Returns:
        {
            'total_teachers': int,
            'by_workstream': [
                {
                    'workstream_id': int,
                    'workstream_name': str,
                    'teacher_count': int
                }
            ]
        }
    """
    _check_admin_permission(actor)
    
    # Teachers are linked to schools via their user's school field
    workstreams = WorkStream.objects.annotate(
        teacher_count=Count(
            'users__teacher_profile',
            filter=Q(users__role=Role.TEACHER),
            distinct=True
        )
    )
    
    by_workstream = [
        {
            'workstream_id': ws.id,
            'workstream_name': ws.name,
            'teacher_count': ws.teacher_count
        }
        for ws in workstreams
    ]
    
    total_teachers = Teacher.objects.count()
    
    return {
        'total_teachers': total_teachers,
        'by_workstream': by_workstream
    }


def get_schools_overview(*, actor: CustomUser) -> Dict:
    """
    Get all schools with student and teacher counts.
    
    Returns:
        {
            'total_schools': int,
            'schools': [
                {
                    'school_id': int,
                    'school_name': str,
                    'workstream_id': int,
                    'workstream_name': str,
                    'manager_name': str | None,
                    'student_count': int,
                    'teacher_count': int,
                    'classroom_count': int,
                    'course_count': int
                }
            ]
        }
    """
    _check_admin_permission(actor)
    
    schools = School.objects.select_related(
        'work_stream', 'manager'
    ).annotate(
        student_count=Count(
            'students',
            filter=Q(students__current_status='active')
        ),
        teacher_count=Count(
            'users__teacher_profile',
            filter=Q(users__role=Role.TEACHER),
            distinct=True
        ),
        classroom_count=Count('classrooms', distinct=True),
        course_count=Count('courses', distinct=True)
    )
    
    schools_data = [
        {
            'school_id': school.id,
            'school_name': school.school_name,
            'workstream_id': school.work_stream_id,
            'workstream_name': school.work_stream.name,
            'manager_name': school.manager.full_name if school.manager else None,
            'student_count': school.student_count,
            'teacher_count': school.teacher_count,
            'classroom_count': school.classroom_count,
            'course_count': school.course_count
        }
        for school in schools
    ]
    
    return {
        'total_schools': len(schools_data),
        'schools': schools_data
    }


def get_platform_growth_summary(*, actor: CustomUser, days: int = 30) -> Dict:
    """
    Get count of recently added users and schools.
    
    Args:
        actor: The user requesting the statistics
        days: Number of days to look back (default 30)
    
    Returns:
        {
            'period_days': int,
            'new_users': int,
            'new_students': int,
            'new_teachers': int,
            'new_schools': int,
            'users_by_role': {
                'student': int,
                'teacher': int,
                ...
            }
        }
    """
    _check_admin_permission(actor)
    
    cutoff_date = timezone.now() - timedelta(days=days)
    
    # Count new users by role
    new_users_by_role = CustomUser.objects.filter(
        date_joined__gte=cutoff_date
    ).values('role').annotate(
        count=Count('id')
    )
    
    users_by_role = {item['role']: item['count'] for item in new_users_by_role}
    
    new_users = CustomUser.objects.filter(date_joined__gte=cutoff_date).count()
    new_students = users_by_role.get(Role.STUDENT, 0)
    new_teachers = users_by_role.get(Role.TEACHER, 0)
    
    # Note: School model doesn't have created_at, so we count all schools
    # In a real scenario, you'd add a created_at field to School model
    total_schools = School.objects.count()
    
    return {
        'period_days': days,
        'new_users': new_users,
        'new_students': new_students,
        'new_teachers': new_teachers,
        'total_schools': total_schools,
        'users_by_role': users_by_role
    }


def get_admin_dashboard_statistics(*, actor: CustomUser) -> Dict:
    """
    Get comprehensive admin dashboard statistics.
    Combines global stats with distribution summaries.
    
    Returns combined statistics for admin dashboard.
    """
    _check_admin_permission(actor)
    
    return {
        'global': get_global_statistics(actor=actor),
        'students_by_workstream': get_students_by_workstream(actor=actor),
        'teachers_by_workstream': get_teachers_by_workstream(actor=actor),
        'growth_summary': get_platform_growth_summary(actor=actor)
    }

