from django.db.models import Count, Q, Prefetch
from django.core.exceptions import PermissionDenied
from accounts.models import CustomUser, Role
from workstream.models import WorkStream
from manager.models import School, ClassRoom, Course
from teacher.models import Teacher, CourseAllocation
from student.models import Student, StudentEnrollment
from typing import Dict, List, Optional


def get_student_count_by_teacher(*, teacher_id: int, actor: CustomUser) -> Dict:
    """
    Get student count for a specific teacher across all their courses and classrooms.
    
    Returns:
        {
            'teacher_id': int,
            'teacher_name': str,
            'total_students': int,
            'by_course': [
                {
                    'course_id': int,
                    'course_name': str,
                    'student_count': int
                }
            ],
            'by_classroom': [
                {
                    'classroom_id': int,
                    'classroom_name': str,
                    'student_count': int
                }
            ]
        }
    """
    try:
        teacher = Teacher.objects.select_related('user').get(user_id=teacher_id)
    except Teacher.DoesNotExist:
        raise ValueError("Teacher not found.")
    
    # Permission check
    if actor.role not in [Role.ADMIN, Role.MANAGER_WORKSTREAM, Role.MANAGER_SCHOOL]:
        if actor.id != teacher_id:
            raise PermissionDenied("Access denied.")
    
    # Get all course allocations for this teacher
    allocations = CourseAllocation.objects.filter(
        teacher=teacher
    ).select_related('course', 'class_room')
    
    # Count students by course
    by_course = []
    classroom_ids = set()
    
    for allocation in allocations:
        classroom_ids.add(allocation.class_room_id)
        
        student_count = StudentEnrollment.objects.filter(
            class_room=allocation.class_room,
            student__current_status='active'
        ).count()
        
        by_course.append({
            'course_id': allocation.course.id,
            'course_name': allocation.course.name,
            'course_code': allocation.course.course_code,
            'classroom_id': allocation.class_room.id,
            'classroom_name': allocation.class_room.classroom_name,
            'student_count': student_count
        })
    
    # Count students by classroom (unique)
    by_classroom = []
    for classroom_id in classroom_ids:
        classroom = ClassRoom.objects.get(id=classroom_id)
        student_count = StudentEnrollment.objects.filter(
            class_room_id=classroom_id,
            student__current_status='active'
        ).count()
        
        by_classroom.append({
            'classroom_id': classroom.id,
            'classroom_name': classroom.classroom_name,
            'grade': classroom.grade.name,
            'student_count': student_count
        })
    
    # Calculate total unique students
    total_students = Student.objects.filter(
        enrollments__class_room_id__in=classroom_ids,
        current_status='active'
    ).distinct().count()
    
    return {
        'teacher_id': teacher_id,
        'teacher_name': teacher.user.full_name,
        'total_students': total_students,
        'by_course': by_course,
        'by_classroom': by_classroom
    }


def get_student_count_by_workstream(*, workstream_id: int, actor: CustomUser) -> Dict:
    """
    Get student count for a specific workstream.
    
    Returns:
        {
            'workstream_id': int,
            'workstream_name': str,
            'total_students': int,
            'by_school': [...]
        }
    """
    try:
        workstream = WorkStream.objects.get(id=workstream_id)
    except WorkStream.DoesNotExist:
        raise ValueError("Workstream not found.")
    
    # Permission check
    if actor.role == Role.MANAGER_WORKSTREAM:
        if actor.work_stream_id != workstream_id:
            raise PermissionDenied("Access denied.")
    elif actor.role not in [Role.ADMIN]:
        raise PermissionDenied("Access denied.")
    
    # Count total students in workstream
    total_students = Student.objects.filter(
        school__work_stream_id=workstream_id,
        current_status='active'
    ).count()
    
    # Count by school
    schools = School.objects.filter(work_stream_id=workstream_id)
    by_school = []
    
    for school in schools:
        student_count = Student.objects.filter(
            school=school,
            current_status='active'
        ).count()
        
        by_school.append({
            'school_id': school.id,
            'school_name': school.school_name,
            'student_count': student_count
        })
    
    return {
        'workstream_id': workstream_id,
        'workstream_name': workstream.name,
        'total_students': total_students,
        'school_count': schools.count(),
        'by_school': by_school
    }


def get_student_count_by_school(*, school_id: int, actor: CustomUser) -> Dict:
    """
    Get student count for a specific school with breakdown by grade and classroom.
    
    Returns:
        {
            'school_id': int,
            'school_name': str,
            'total_students': int,
            'by_grade': [...],
            'by_classroom': [...]
        }
    """
    try:
        school = School.objects.select_related('work_stream').get(id=school_id)
    except School.DoesNotExist:
        raise ValueError("School not found.")
    
    # Permission check
    if actor.role == Role.MANAGER_SCHOOL:
        if actor.school_id != school_id:
            raise PermissionDenied("Access denied.")
    elif actor.role == Role.MANAGER_WORKSTREAM:
        if actor.work_stream_id != school.work_stream_id:
            raise PermissionDenied("Access denied.")
    elif actor.role not in [Role.ADMIN]:
        raise PermissionDenied("Access denied.")
    
    # Total students
    total_students = Student.objects.filter(
        school=school,
        current_status='active'
    ).count()
    
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
    by_classroom = []
    classrooms = ClassRoom.objects.filter(school=school).select_related(
        'grade', 'academic_year', 'homeroom_teacher__user'
    )
    
    for classroom in classrooms:
        student_count = StudentEnrollment.objects.filter(
            class_room=classroom,
            student__current_status='active'
        ).count()
        
        by_classroom.append({
            'classroom_id': classroom.id,
            'classroom_name': classroom.classroom_name,
            'grade': classroom.grade.name,
            'academic_year': classroom.academic_year.academic_year_code,
            'homeroom_teacher': classroom.homeroom_teacher.user.full_name if classroom.homeroom_teacher else None,
            'student_count': student_count
        })
    
    return {
        'school_id': school_id,
        'school_name': school.school_name,
        'workstream': school.work_stream.name,
        'total_students': total_students,
        'by_grade': list(by_grade),
        'by_classroom': by_classroom
    }


def get_student_count_by_school_manager(*, manager_id: int, actor: CustomUser) -> Dict:
    """
    Get student count for all schools managed by a school manager.
    
    Returns:
        {
            'manager_id': int,
            'manager_name': str,
            'total_students': int,
            'schools': [...]
        }
    """
    try:
        manager = CustomUser.objects.get(id=manager_id, role=Role.MANAGER_SCHOOL)
    except CustomUser.DoesNotExist:
        raise ValueError("School manager not found.")
    
    # Permission check
    if actor.role == Role.MANAGER_SCHOOL:
        if actor.id != manager_id:
            raise PermissionDenied("Access denied.")
    elif actor.role == Role.MANAGER_WORKSTREAM:
        if actor.work_stream_id != manager.work_stream_id:
            raise PermissionDenied("Access denied.")
    elif actor.role not in [Role.ADMIN]:
        raise PermissionDenied("Access denied.")
    
    # Get all schools managed by this manager
    schools = School.objects.filter(manager=manager)
    
    total_students = 0
    schools_data = []
    
    for school in schools:
        student_count = Student.objects.filter(
            school=school,
            current_status='active'
        ).count()
        
        total_students += student_count
        
        schools_data.append({
            'school_id': school.id,
            'school_name': school.school_name,
            'student_count': student_count
        })
    
    return {
        'manager_id': manager_id,
        'manager_name': manager.full_name,
        'total_students': total_students,
        'school_count': schools.count(),
        'schools': schools_data
    }


def get_student_count_by_course(*, course_id: int, actor: CustomUser) -> Dict:
    """
    Get student count for a specific course across all classrooms.
    
    Returns:
        {
            'course_id': int,
            'course_name': str,
            'course_code': str,
            'total_students': int,
            'by_classroom': [...]
        }
    """
    try:
        course = Course.objects.select_related('school', 'grade').get(id=course_id)
    except Course.DoesNotExist:
        raise ValueError("Course not found.")
    
    # Permission check
    if actor.role == Role.MANAGER_SCHOOL:
        if actor.school_id != course.school_id:
            raise PermissionDenied("Access denied.")
    elif actor.role == Role.MANAGER_WORKSTREAM:
        if actor.work_stream_id != course.school.work_stream_id:
            raise PermissionDenied("Access denied.")
    elif actor.role not in [Role.ADMIN, Role.TEACHER]:
        raise PermissionDenied("Access denied.")
    
    # Get all allocations for this course
    allocations = CourseAllocation.objects.filter(
        course=course
    ).select_related('class_room', 'teacher__user')
    
    by_classroom = []
    total_students = 0
    
    for allocation in allocations:
        student_count = StudentEnrollment.objects.filter(
            class_room=allocation.class_room,
            student__current_status='active'
        ).count()
        
        total_students += student_count
        
        by_classroom.append({
            'classroom_id': allocation.class_room.id,
            'classroom_name': allocation.class_room.classroom_name,
            'teacher_id': allocation.teacher.user_id,
            'teacher_name': allocation.teacher.user.full_name,
            'student_count': student_count
        })
    
    return {
        'course_id': course_id,
        'course_name': course.name,
        'course_code': course.course_code,
        'grade': course.grade.name,
        'school': course.school.school_name,
        'total_students': total_students,
        'by_classroom': by_classroom
    }


def get_student_count_by_classroom(*, classroom_id: int, actor: CustomUser) -> Dict:
    """
    Get detailed student count for a specific classroom.
    
    Returns:
        {
            'classroom_id': int,
            'classroom_name': str,
            'total_students': int,
            'students': [...],
            'by_status': {...}
        }
    """
    try:
        classroom = ClassRoom.objects.select_related(
            'school', 'grade', 'academic_year', 'homeroom_teacher__user'
        ).get(id=classroom_id)
    except ClassRoom.DoesNotExist:
        raise ValueError("Classroom not found.")
    
    # Permission check
    if actor.role == Role.MANAGER_SCHOOL:
        if actor.school_id != classroom.school_id:
            raise PermissionDenied("Access denied.")
    elif actor.role == Role.MANAGER_WORKSTREAM:
        if actor.work_stream_id != classroom.school.work_stream_id:
            raise PermissionDenied("Access denied.")
    elif actor.role not in [Role.ADMIN, Role.TEACHER, Role.SECRETARY]:
        raise PermissionDenied("Access denied.")
    
    # Get all enrollments
    enrollments = StudentEnrollment.objects.filter(
        class_room=classroom
    ).select_related('student__user', 'student__grade')
    
    # Count by status
    by_status = Student.objects.filter(
        enrollments__class_room=classroom
    ).values('current_status').annotate(count=Count('user_id'))
    
    students = []
    for enrollment in enrollments:
        students.append({
            'student_id': enrollment.student.user_id,
            'student_name': enrollment.student.user.full_name,
            'status': enrollment.student.current_status,
            'enrollment_status': enrollment.status
        })
    
    return {
        'classroom_id': classroom_id,
        'classroom_name': classroom.classroom_name,
        'grade': classroom.grade.name,
        'academic_year': classroom.academic_year.academic_year_code,
        'school': classroom.school.school_name,
        'homeroom_teacher': classroom.homeroom_teacher.user.full_name if classroom.homeroom_teacher else None,
        'total_students': len(students),
        'active_students': len([s for s in students if s['status'] == 'active']),
        'by_status': {item['current_status']: item['count'] for item in by_status},
        'students': students
    }


def get_comprehensive_statistics(*, actor: CustomUser) -> Dict:
    """
    Get comprehensive statistics based on user role.
    Admins see everything, managers see their scope.
    
    Returns a comprehensive statistics object.
    """
    stats = {
        'user_role': actor.role,
        'statistics': {}
    }
    
    if actor.role == Role.ADMIN:
        # Global statistics
        stats['statistics'] = {
            'total_students': Student.objects.filter(current_status='active').count(),
            'total_teachers': Teacher.objects.count(),
            'total_workstreams': WorkStream.objects.filter(is_active=True).count(),
            'total_schools': School.objects.count(),
            'total_classrooms': ClassRoom.objects.count(),
            'total_courses': Course.objects.count()
        }
    
    elif actor.role == Role.MANAGER_WORKSTREAM:
        # Workstream scope
        stats['statistics'] = get_student_count_by_workstream(
            workstream_id=actor.work_stream_id,
            actor=actor
        )
    
    elif actor.role == Role.MANAGER_SCHOOL:
        # School scope
        stats['statistics'] = get_student_count_by_school(
            school_id=actor.school_id,
            actor=actor
        )
    
    elif actor.role == Role.TEACHER:
        # Teacher scope
        stats['statistics'] = get_student_count_by_teacher(
            teacher_id=actor.id,
            actor=actor
        )
    
    return stats