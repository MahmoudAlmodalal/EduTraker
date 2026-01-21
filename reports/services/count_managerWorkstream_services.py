from django.db.models import Count, Q
from django.core.exceptions import PermissionDenied
from accounts.models import CustomUser, Role
from workstream.models import WorkStream
from school.models import School, ClassRoom, Course
from teacher.models import Teacher
from student.models import Student
from typing import Dict


def _check_workstream_permission(actor: CustomUser, workstream_id: int) -> None:
    """Check if actor has permission to access workstream data."""
    if actor.role == Role.ADMIN:
        return
    if actor.role == Role.MANAGER_WORKSTREAM:
        if actor.work_stream_id != workstream_id:
            raise PermissionDenied("Access denied. You can only view your own workstream.")
        return
    raise PermissionDenied("Access denied. Workstream manager or admin role required.")


def get_workstream_summary(*, workstream_id: int, actor: CustomUser) -> Dict:
    """
    Get overview statistics for a specific workstream.
    
    Returns:
        {
            'workstream_id': int,
            'workstream_name': str,
            'is_active': bool,
            'total_students': int,
            'total_teachers': int,
            'school_count': int,
            'classroom_count': int,
            'course_count': int,
            'by_school': [...]
        }
    """
    try:
        workstream = WorkStream.objects.get(id=workstream_id)
    except WorkStream.DoesNotExist:
        raise ValueError("Workstream not found.")
    
    _check_workstream_permission(actor, workstream_id)
    
    # Get schools with annotated counts
    schools = School.objects.filter(
        work_stream_id=workstream_id
    ).select_related('manager').annotate(
        student_count=Count(
            'users__student_profile',
            filter=Q(users__student_profile__enrollment_status='active')
        ),
        teacher_count=Count(
            'users__teacher_profile',
            filter=Q(users__role=Role.TEACHER),
            distinct=True
        ),
        classroom_count=Count('classrooms', distinct=True)
    )
    
    by_school = []
    total_students = 0
    total_teachers = 0
    total_classrooms = 0
    
    for school in schools:
        by_school.append({
            'school_id': school.id,
            'school_name': school.school_name,
            'manager_name': school.manager.full_name if school.manager else None,
            'student_count': school.student_count,
            'teacher_count': school.teacher_count,
            'classroom_count': school.classroom_count
        })
        total_students += school.student_count
        total_teachers += school.teacher_count
        total_classrooms += school.classroom_count
    
    # Get total courses in workstream
    total_courses = Course.objects.filter(
        school__work_stream_id=workstream_id
    ).count()
    
    return {
        'workstream_id': workstream_id,
        'workstream_name': workstream.name,
        'is_active': workstream.is_active,
        'total_students': total_students,
        'total_teachers': total_teachers,
        'school_count': len(by_school),
        'classroom_count': total_classrooms,
        'course_count': total_courses,
        'by_school': by_school
    }


def get_schools_in_workstream(*, workstream_id: int, actor: CustomUser) -> Dict:
    """
    Get all schools in workstream with student counts.
    
    Returns:
        {
            'workstream_id': int,
            'workstream_name': str,
            'total_schools': int,
            'schools': [
                {
                    'school_id': int,
                    'school_name': str,
                    'manager_name': str | None,
                    'student_count': int,
                    'active_student_count': int
                }
            ]
        }
    """
    try:
        workstream = WorkStream.objects.get(id=workstream_id)
    except WorkStream.DoesNotExist:
        raise ValueError("Workstream not found.")
    
    _check_workstream_permission(actor, workstream_id)
    
    schools = School.objects.filter(
        work_stream_id=workstream_id
    ).select_related('manager').annotate(
        student_count=Count('users__student_profile'),
        active_student_count=Count(
            'users__student_profile',
            filter=Q(users__student_profile__enrollment_status='active')
        )
    )
    
    schools_data = [
        {
            'school_id': school.id,
            'school_name': school.school_name,
            'manager_name': school.manager.full_name if school.manager else None,
            'student_count': school.student_count,
            'active_student_count': school.active_student_count
        }
        for school in schools
    ]
    
    return {
        'workstream_id': workstream_id,
        'workstream_name': workstream.name,
        'total_schools': len(schools_data),
        'schools': schools_data
    }


def get_teachers_in_workstream(*, workstream_id: int, actor: CustomUser) -> Dict:
    """
    Get teacher count per school in workstream.
    
    Returns:
        {
            'workstream_id': int,
            'workstream_name': str,
            'total_teachers': int,
            'by_school': [
                {
                    'school_id': int,
                    'school_name': str,
                    'teacher_count': int,
                    'teachers': [
                        {
                            'teacher_id': int,
                            'teacher_name': str,
                            'specialization': str | None,
                            'employment_status': str
                        }
                    ]
                }
            ]
        }
    """
    try:
        workstream = WorkStream.objects.get(id=workstream_id)
    except WorkStream.DoesNotExist:
        raise ValueError("Workstream not found.")
    
    _check_workstream_permission(actor, workstream_id)
    
    schools = School.objects.filter(work_stream_id=workstream_id)
    
    by_school = []
    total_teachers = 0
    
    for school in schools:
        teachers = Teacher.objects.filter(
            user__school_id=school.id
        ).select_related('user')
        
        teachers_data = [
            {
                'teacher_id': teacher.user_id,
                'teacher_name': teacher.user.full_name,
                'specialization': teacher.specialization,
                'employment_status': teacher.employment_status
            }
            for teacher in teachers
        ]
        
        by_school.append({
            'school_id': school.id,
            'school_name': school.school_name,
            'teacher_count': len(teachers_data),
            'teachers': teachers_data
        })
        total_teachers += len(teachers_data)
    
    return {
        'workstream_id': workstream_id,
        'workstream_name': workstream.name,
        'total_teachers': total_teachers,
        'by_school': by_school
    }


def get_classrooms_in_workstream(*, workstream_id: int, actor: CustomUser) -> Dict:
    """
    Get classroom distribution by school and grade in workstream.
    
    Returns:
        {
            'workstream_id': int,
            'workstream_name': str,
            'total_classrooms': int,
            'by_school': [
                {
                    'school_id': int,
                    'school_name': str,
                    'classroom_count': int,
                    'by_grade': [
                        {
                            'grade_id': int,
                            'grade_name': str,
                            'classroom_count': int,
                            'student_count': int
                        }
                    ]
                }
            ]
        }
    """
    try:
        workstream = WorkStream.objects.get(id=workstream_id)
    except WorkStream.DoesNotExist:
        raise ValueError("Workstream not found.")
    
    _check_workstream_permission(actor, workstream_id)
    
    schools = School.objects.filter(work_stream_id=workstream_id)
    
    by_school = []
    total_classrooms = 0
    
    for school in schools:
        # Get classrooms grouped by grade
        grade_stats = ClassRoom.objects.filter(
            school=school
        ).values(
            'grade__id', 'grade__name'
        ).annotate(
            classroom_count=Count('id'),
            student_count=Count(
                'enrollments__student',
                filter=Q(enrollments__status='active')
            )
        ).order_by('grade__numeric_level')
        
        by_grade = [
            {
                'grade_id': stat['grade__id'],
                'grade_name': stat['grade__name'],
                'classroom_count': stat['classroom_count'],
                'student_count': stat['student_count']
            }
            for stat in grade_stats
        ]
        
        school_classroom_count = sum(g['classroom_count'] for g in by_grade)
        
        by_school.append({
            'school_id': school.id,
            'school_name': school.school_name,
            'classroom_count': school_classroom_count,
            'by_grade': by_grade
        })
        total_classrooms += school_classroom_count
    
    return {
        'workstream_id': workstream_id,
        'workstream_name': workstream.name,
        'total_classrooms': total_classrooms,
        'by_school': by_school
    }


def get_workstream_dashboard_statistics(*, workstream_id: int, actor: CustomUser) -> Dict:
    """
    Get comprehensive workstream dashboard statistics.
    
    Returns combined statistics for workstream manager dashboard.
    """
    _check_workstream_permission(actor, workstream_id)
    
    return {
        'summary': get_workstream_summary(workstream_id=workstream_id, actor=actor),
        'schools': get_schools_in_workstream(workstream_id=workstream_id, actor=actor),
        'classrooms': get_classrooms_in_workstream(workstream_id=workstream_id, actor=actor)
    }

