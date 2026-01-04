from django.db.models import Count, Q
from django.core.exceptions import PermissionDenied
from accounts.models import CustomUser, Role
from manager.models import School, ClassRoom, Course
from teacher.models import Teacher, CourseAllocation
from student.models import Student, StudentEnrollment
from typing import Dict


def _check_school_permission(actor: CustomUser, school_id: int) -> None:
    """Check if actor has permission to access school data."""
    if actor.role == Role.ADMIN:
        return
    if actor.role == Role.MANAGER_WORKSTREAM:
        # Workstream manager can view schools in their workstream
        school = School.objects.filter(id=school_id).first()
        if school and actor.work_stream_id == school.work_stream_id:
            return
        raise PermissionDenied("Access denied. School not in your workstream.")
    if actor.role == Role.MANAGER_SCHOOL:
        if actor.school_id == school_id:
            return
        raise PermissionDenied("Access denied. You can only view your own school.")
    raise PermissionDenied("Access denied. School manager or higher role required.")


def get_school_summary(*, school_id: int, actor: CustomUser) -> Dict:
    """
    Get overview statistics for a specific school.
    
    Returns:
        {
            'school_id': int,
            'school_name': str,
            'workstream_id': int,
            'workstream_name': str,
            'manager_name': str | None,
            'total_students': int,
            'active_students': int,
            'total_teachers': int,
            'total_classrooms': int,
            'total_courses': int,
            'by_grade': [...],
            'by_classroom': [...]
        }
    """
    try:
        school = School.objects.select_related('work_stream', 'manager').get(id=school_id)
    except School.DoesNotExist:
        raise ValueError("School not found.")
    
    _check_school_permission(actor, school_id)
    
    # Total students
    total_students = Student.objects.filter(school=school).count()
    active_students = Student.objects.filter(
        school=school,
        current_status='active'
    ).count()
    
    # Total teachers
    total_teachers = Teacher.objects.filter(user__school_id=school_id).count()
    
    # Total classrooms and courses
    total_classrooms = ClassRoom.objects.filter(school=school).count()
    total_courses = Course.objects.filter(school=school).count()
    
    # Count by grade
    by_grade = Student.objects.filter(
        school=school,
        current_status='active'
    ).values(
        'grade__id',
        'grade__name',
        'grade__numeric_level'
    ).annotate(
        student_count=Count('user_id')
    ).order_by('grade__numeric_level')
    
    # Count by classroom
    classrooms = ClassRoom.objects.filter(
        school=school
    ).select_related(
        'grade', 'academic_year', 'homeroom_teacher__user'
    ).annotate(
        student_count=Count(
            'enrollments__student',
            filter=Q(enrollments__student__current_status='active')
        )
    )
    
    by_classroom = [
        {
            'classroom_id': classroom.id,
            'classroom_name': classroom.classroom_name,
            'grade': classroom.grade.name,
            'academic_year': classroom.academic_year.academic_year_code,
            'homeroom_teacher': classroom.homeroom_teacher.user.full_name if classroom.homeroom_teacher else None,
            'student_count': classroom.student_count
        }
        for classroom in classrooms
    ]
    
    return {
        'school_id': school_id,
        'school_name': school.school_name,
        'workstream_id': school.work_stream_id,
        'workstream_name': school.work_stream.name,
        'manager_name': school.manager.full_name if school.manager else None,
        'total_students': total_students,
        'active_students': active_students,
        'total_teachers': total_teachers,
        'total_classrooms': total_classrooms,
        'total_courses': total_courses,
        'by_grade': list(by_grade),
        'by_classroom': by_classroom
    }


def get_students_by_grade(*, school_id: int, actor: CustomUser) -> Dict:
    """
    Get student distribution by grade for a school.
    
    Returns:
        {
            'school_id': int,
            'school_name': str,
            'total_students': int,
            'by_grade': [
                {
                    'grade_id': int,
                    'grade_name': str,
                    'numeric_level': int,
                    'total_count': int,
                    'active_count': int,
                    'inactive_count': int
                }
            ]
        }
    """
    try:
        school = School.objects.get(id=school_id)
    except School.DoesNotExist:
        raise ValueError("School not found.")
    
    _check_school_permission(actor, school_id)
    
    # Get all students grouped by grade with status breakdown
    grade_stats = Student.objects.filter(
        school=school
    ).values(
        'grade__id',
        'grade__name',
        'grade__numeric_level'
    ).annotate(
        total_count=Count('user_id'),
        active_count=Count('user_id', filter=Q(current_status='active')),
        inactive_count=Count('user_id', filter=~Q(current_status='active'))
    ).order_by('grade__numeric_level')
    
    by_grade = [
        {
            'grade_id': stat['grade__id'],
            'grade_name': stat['grade__name'],
            'numeric_level': stat['grade__numeric_level'],
            'total_count': stat['total_count'],
            'active_count': stat['active_count'],
            'inactive_count': stat['inactive_count']
        }
        for stat in grade_stats
    ]
    
    total_students = sum(g['total_count'] for g in by_grade)
    
    return {
        'school_id': school_id,
        'school_name': school.school_name,
        'total_students': total_students,
        'by_grade': by_grade
    }


def get_students_by_classroom(*, school_id: int, actor: CustomUser) -> Dict:
    """
    Get student distribution by classroom for a school.
    
    Returns:
        {
            'school_id': int,
            'school_name': str,
            'total_classrooms': int,
            'classrooms': [
                {
                    'classroom_id': int,
                    'classroom_name': str,
                    'grade_name': str,
                    'academic_year': str,
                    'homeroom_teacher': str | None,
                    'total_students': int,
                    'active_students': int
                }
            ]
        }
    """
    try:
        school = School.objects.get(id=school_id)
    except School.DoesNotExist:
        raise ValueError("School not found.")
    
    _check_school_permission(actor, school_id)
    
    classrooms = ClassRoom.objects.filter(
        school=school
    ).select_related(
        'grade', 'academic_year', 'homeroom_teacher__user'
    ).annotate(
        total_students=Count('enrollments__student'),
        active_students=Count(
            'enrollments__student',
            filter=Q(enrollments__student__current_status='active')
        )
    ).order_by('grade__numeric_level', 'classroom_name')
    
    classrooms_data = [
        {
            'classroom_id': classroom.id,
            'classroom_name': classroom.classroom_name,
            'grade_name': classroom.grade.name,
            'academic_year': classroom.academic_year.academic_year_code,
            'homeroom_teacher': classroom.homeroom_teacher.user.full_name if classroom.homeroom_teacher else None,
            'total_students': classroom.total_students,
            'active_students': classroom.active_students
        }
        for classroom in classrooms
    ]
    
    return {
        'school_id': school_id,
        'school_name': school.school_name,
        'total_classrooms': len(classrooms_data),
        'classrooms': classrooms_data
    }


def get_teachers_in_school(*, school_id: int, actor: CustomUser) -> Dict:
    """
    Get all teachers with course allocations for a school.
    
    Returns:
        {
            'school_id': int,
            'school_name': str,
            'total_teachers': int,
            'teachers': [
                {
                    'teacher_id': int,
                    'teacher_name': str,
                    'specialization': str | None,
                    'employment_status': str,
                    'course_count': int,
                    'classroom_count': int,
                    'student_count': int
                }
            ]
        }
    """
    try:
        school = School.objects.get(id=school_id)
    except School.DoesNotExist:
        raise ValueError("School not found.")
    
    _check_school_permission(actor, school_id)
    
    teachers = Teacher.objects.filter(
        user__school_id=school_id
    ).select_related('user').annotate(
        course_count=Count('course_allocations__course', distinct=True),
        classroom_count=Count('course_allocations__class_room', distinct=True),
        student_count=Count(
            'course_allocations__class_room__enrollments__student',
            filter=Q(course_allocations__class_room__enrollments__student__current_status='active'),
            distinct=True
        )
    )
    
    teachers_data = [
        {
            'teacher_id': teacher.user_id,
            'teacher_name': teacher.user.full_name,
            'specialization': teacher.specialization,
            'employment_status': teacher.employment_status,
            'course_count': teacher.course_count,
            'classroom_count': teacher.classroom_count,
            'student_count': teacher.student_count
        }
        for teacher in teachers
    ]
    
    return {
        'school_id': school_id,
        'school_name': school.school_name,
        'total_teachers': len(teachers_data),
        'teachers': teachers_data
    }


def get_courses_in_school(*, school_id: int, actor: CustomUser) -> Dict:
    """
    Get course list with student enrollment counts for a school.
    
    Returns:
        {
            'school_id': int,
            'school_name': str,
            'total_courses': int,
            'courses': [
                {
                    'course_id': int,
                    'course_code': str,
                    'course_name': str,
                    'grade_name': str,
                    'teacher_count': int,
                    'classroom_count': int,
                    'student_count': int
                }
            ]
        }
    """
    try:
        school = School.objects.get(id=school_id)
    except School.DoesNotExist:
        raise ValueError("School not found.")
    
    _check_school_permission(actor, school_id)
    
    courses = Course.objects.filter(
        school=school
    ).select_related('grade').annotate(
        teacher_count=Count('allocations__teacher', distinct=True),
        classroom_count=Count('allocations__class_room', distinct=True),
        student_count=Count(
            'allocations__class_room__enrollments__student',
            filter=Q(allocations__class_room__enrollments__student__current_status='active'),
            distinct=True
        )
    ).order_by('grade__numeric_level', 'name')
    
    courses_data = [
        {
            'course_id': course.id,
            'course_code': course.course_code,
            'course_name': course.name,
            'grade_name': course.grade.name,
            'teacher_count': course.teacher_count,
            'classroom_count': course.classroom_count,
            'student_count': course.student_count
        }
        for course in courses
    ]
    
    return {
        'school_id': school_id,
        'school_name': school.school_name,
        'total_courses': len(courses_data),
        'courses': courses_data
    }


def get_classroom_details(*, classroom_id: int, actor: CustomUser) -> Dict:
    """
    Get detailed view of a specific classroom.
    
    Returns:
        {
            'classroom_id': int,
            'classroom_name': str,
            'grade': str,
            'academic_year': str,
            'school_id': int,
            'school_name': str,
            'homeroom_teacher': str | None,
            'total_students': int,
            'active_students': int,
            'by_status': {...},
            'students': [...],
            'courses': [...]
        }
    """
    try:
        classroom = ClassRoom.objects.select_related(
            'school', 'grade', 'academic_year', 'homeroom_teacher__user'
        ).get(id=classroom_id)
    except ClassRoom.DoesNotExist:
        raise ValueError("Classroom not found.")
    
    _check_school_permission(actor, classroom.school_id)
    
    # Get all enrollments with related data
    enrollments = StudentEnrollment.objects.filter(
        class_room=classroom
    ).select_related('student__user')
    
    # Count by status
    status_counts = StudentEnrollment.objects.filter(
        class_room=classroom
    ).values(
        'student__current_status'
    ).annotate(
        count=Count('student')
    )
    
    by_status = {item['student__current_status']: item['count'] for item in status_counts}
    
    # Build students list
    students = []
    total_students = 0
    active_students = 0
    
    for enrollment in enrollments:
        student_status = enrollment.student.current_status
        students.append({
            'student_id': enrollment.student.user_id,
            'student_name': enrollment.student.user.full_name,
            'status': student_status,
            'enrollment_status': enrollment.status
        })
        total_students += 1
        if student_status == 'active':
            active_students += 1
    
    # Get courses taught in this classroom
    allocations = CourseAllocation.objects.filter(
        class_room=classroom
    ).select_related('course', 'teacher__user')
    
    courses = [
        {
            'course_id': alloc.course.id,
            'course_code': alloc.course.course_code,
            'course_name': alloc.course.name,
            'teacher_id': alloc.teacher.user_id,
            'teacher_name': alloc.teacher.user.full_name
        }
        for alloc in allocations
    ]
    
    return {
        'classroom_id': classroom_id,
        'classroom_name': classroom.classroom_name,
        'grade': classroom.grade.name,
        'academic_year': classroom.academic_year.academic_year_code,
        'school_id': classroom.school_id,
        'school_name': classroom.school.school_name,
        'homeroom_teacher': classroom.homeroom_teacher.user.full_name if classroom.homeroom_teacher else None,
        'total_students': total_students,
        'active_students': active_students,
        'by_status': by_status,
        'students': students,
        'courses': courses
    }


def get_school_dashboard_statistics(*, school_id: int, actor: CustomUser) -> Dict:
    """
    Get comprehensive school dashboard statistics.
    
    Returns combined statistics for school manager dashboard.
    """
    _check_school_permission(actor, school_id)
    
    return {
        'summary': get_school_summary(school_id=school_id, actor=actor),
        'students_by_grade': get_students_by_grade(school_id=school_id, actor=actor),
        'teachers': get_teachers_in_school(school_id=school_id, actor=actor),
        'courses': get_courses_in_school(school_id=school_id, actor=actor)
    }

