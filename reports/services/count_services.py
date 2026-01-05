"""
Base statistics services module.

This module provides the main entry point for role-based statistics through
`get_comprehensive_statistics()` which delegates to role-specific service modules:

- count_admin_services.py - Admin platform-wide statistics
- count_managerWorkstream_services.py - Workstream manager statistics
- count_managerSchool_services.py - School manager statistics
- count_teacher_services.py - Teacher teaching statistics
- count__student_services.py - Student academic statistics
"""
from django.core.exceptions import PermissionDenied
from accounts.models import CustomUser, Role
from typing import Dict

# Import role-specific services
from reports.services.count_admin_services import (
    get_global_statistics,
    get_students_by_workstream,
    get_teachers_by_workstream,
    get_schools_overview,
    get_platform_growth_summary,
    get_admin_dashboard_statistics,
)
from reports.services.count_managerWorkstream_services import (
    get_workstream_summary,
    get_schools_in_workstream,
    get_teachers_in_workstream,
    get_classrooms_in_workstream,
    get_workstream_dashboard_statistics,
)
from reports.services.count_managerSchool_services import (
    get_school_summary,
    get_students_by_grade,
    get_students_by_classroom,
    get_teachers_in_school,
    get_courses_in_school,
    get_classroom_details,
    get_school_dashboard_statistics,
)
from reports.services.count_teacher_services import (
    get_teacher_summary,
    get_students_by_course,
    get_students_by_classroom as get_teacher_students_by_classroom,
    get_course_details,
    get_attendance_summary,
    get_assignment_stats,
    get_teacher_dashboard_statistics,
)
from reports.services.count__student_services import (
    get_student_profile_summary,
    get_student_courses,
    get_student_grades_summary,
    get_student_attendance_summary,
    get_classmates_count,
    get_student_dashboard_statistics,
)


def get_comprehensive_statistics(*, actor: CustomUser) -> Dict:
    """
    Get comprehensive statistics based on user role.
    Delegates to role-specific dashboard functions.
    
    Args:
        actor: The user requesting statistics
    
    Returns:
        {
            'user_role': str,
            'statistics': {...}  # Role-specific statistics
        }
    """
    stats = {
        'user_role': actor.role,
        'statistics': {}
    }
    
    if actor.role == Role.ADMIN:
        stats['statistics'] = get_admin_dashboard_statistics(actor=actor)
    
    elif actor.role == Role.MANAGER_WORKSTREAM:
        if not actor.work_stream_id:
            raise PermissionDenied("No workstream assigned to this user.")
        stats['statistics'] = get_workstream_dashboard_statistics(
            workstream_id=actor.work_stream_id,
            actor=actor
        )
    
    elif actor.role == Role.MANAGER_SCHOOL:
        if not actor.school_id:
            raise PermissionDenied("No school assigned to this user.")
        stats['statistics'] = get_school_dashboard_statistics(
            school_id=actor.school_id,
            actor=actor
        )
    
    elif actor.role == Role.TEACHER:
        stats['statistics'] = get_teacher_dashboard_statistics(
            teacher_id=actor.id,
            actor=actor
        )
    
    elif actor.role == Role.STUDENT:
        stats['statistics'] = get_student_dashboard_statistics(
            student_id=actor.id,
            actor=actor
        )
    
    else:
        # Guest, Secretary, Guardian - limited access
        stats['statistics'] = {
            'message': 'Limited statistics access for this role.'
        }
    
    return stats


# Aliases for backward compatibility with stats_views.py
get_student_count_by_teacher = get_teacher_summary
get_student_count_by_workstream = get_workstream_summary
get_student_count_by_school = get_school_summary
get_student_count_by_school_manager = get_school_summary  # Note: School managers are usually assigned to one school
get_student_count_by_course = get_students_by_course
get_student_count_by_classroom = get_teacher_students_by_classroom


# Re-export all functions for backward compatibility
__all__ = [
    # Base
    'get_comprehensive_statistics',
    
    # Admin services
    'get_global_statistics',
    'get_students_by_workstream',
    'get_teachers_by_workstream',
    'get_schools_overview',
    'get_platform_growth_summary',
    'get_admin_dashboard_statistics',
    
    # Workstream manager services
    'get_workstream_summary',
    'get_schools_in_workstream',
    'get_teachers_in_workstream',
    'get_classrooms_in_workstream',
    'get_workstream_dashboard_statistics',
    
    # School manager services
    'get_school_summary',
    'get_students_by_grade',
    'get_students_by_classroom',
    'get_teachers_in_school',
    'get_courses_in_school',
    'get_classroom_details',
    'get_school_dashboard_statistics',
    
    # Teacher services
    'get_teacher_summary',
    'get_students_by_course',
    'get_teacher_students_by_classroom',
    'get_course_details',
    'get_attendance_summary',
    'get_assignment_stats',
    'get_teacher_dashboard_statistics',
    
    # Student services
    'get_student_profile_summary',
    'get_student_courses',
    'get_student_grades_summary',
    'get_student_attendance_summary',
    'get_classmates_count',
    'get_student_dashboard_statistics',
]
