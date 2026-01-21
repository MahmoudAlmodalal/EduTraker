from django.db.models import Count, Q, Avg, Sum
from django.core.exceptions import PermissionDenied
from accounts.models import CustomUser, Role
from school.models import School, ClassRoom, Course
from teacher.models import Teacher, CourseAllocation, Assignment, Attendance, Mark
from student.models import Student, StudentEnrollment
from typing import Dict


def _check_teacher_permission(actor: CustomUser, teacher_id: int) -> None:
    """Check if actor has permission to access teacher data."""
    if actor.role == Role.ADMIN:
        return
    if actor.role == Role.MANAGER_WORKSTREAM:
        # Check if teacher is in the same workstream
        teacher = Teacher.objects.filter(user_id=teacher_id).select_related('user').first()
        if teacher and actor.work_stream_id == teacher.user.work_stream_id:
            return
        raise PermissionDenied("Access denied. Teacher not in your workstream.")
    if actor.role == Role.MANAGER_SCHOOL:
        # Check if teacher is in the same school
        teacher = Teacher.objects.filter(user_id=teacher_id).select_related('user').first()
        if teacher and actor.school_id == teacher.user.school_id:
            return
        raise PermissionDenied("Access denied. Teacher not in your school.")
    if actor.role == Role.TEACHER:
        if actor.id == teacher_id:
            return
        raise PermissionDenied("Access denied. You can only view your own statistics.")
    raise PermissionDenied("Access denied. Teacher or higher role required.")


def get_teacher_summary(*, teacher_id: int, actor: CustomUser) -> Dict:
    """
    Get overview of teacher's students across all courses and classrooms.
    
    Returns:
        {
            'teacher_id': int,
            'teacher_name': str,
            'school_name': str,
            'specialization': str | None,
            'total_students': int,
            'total_courses': int,
            'total_classrooms': int,
            'by_course': [...],
            'by_classroom': [...]
        }
    """
    try:
        teacher = Teacher.objects.select_related('user', 'user__school').get(user_id=teacher_id)
    except Teacher.DoesNotExist:
        raise ValueError("Teacher not found.")
    
    _check_teacher_permission(actor, teacher_id)
    
    # Get all course allocations with annotated student counts
    allocations = CourseAllocation.objects.filter(
        teacher=teacher
    ).select_related(
        'course', 'class_room', 'class_room__grade'
    ).annotate(
        student_count=Count(
            'class_room__enrollments__student',
            filter=Q(class_room__enrollments__student__enrollment_status='active')
        )
    )
    
    # Build by_course list
    by_course = [
        {
            'course_id': allocation.course.id,
            'course_name': allocation.course.name,
            'course_code': allocation.course.course_code,
            'classroom_id': allocation.class_room.id,
            'classroom_name': allocation.class_room.classroom_name,
            'student_count': allocation.student_count
        }
        for allocation in allocations
    ]
    
    # Get unique classroom IDs
    classroom_ids = list(allocations.values_list('class_room_id', flat=True).distinct())
    
    # Get classrooms with annotated student counts
    classrooms = ClassRoom.objects.filter(
        id__in=classroom_ids
    ).select_related('grade').annotate(
        student_count=Count(
            'enrollments__student',
            filter=Q(enrollments__student__enrollment_status='active')
        )
    )
    
    by_classroom = [
        {
            'classroom_id': classroom.id,
            'classroom_name': classroom.classroom_name,
            'grade': classroom.grade.name,
            'student_count': classroom.student_count
        }
        for classroom in classrooms
    ]
    
    # Calculate total unique students
    total_students = Student.objects.filter(
        enrollments__class_room_id__in=classroom_ids,
        enrollment_status='active'
    ).distinct().count()
    
    # Count unique courses and classrooms
    total_courses = allocations.values('course_id').distinct().count()
    total_classrooms = len(classroom_ids)
    
    return {
        'teacher_id': teacher_id,
        'teacher_name': teacher.user.full_name,
        'school_name': teacher.user.school.school_name if teacher.user.school else None,
        'specialization': teacher.specialization,
        'total_students': total_students,
        'total_courses': total_courses,
        'total_classrooms': total_classrooms,
        'by_course': by_course,
        'by_classroom': by_classroom
    }


def get_students_by_course(*, teacher_id: int, actor: CustomUser) -> Dict:
    """
    Get students per course taught by teacher.
    
    Returns:
        {
            'teacher_id': int,
            'teacher_name': str,
            'courses': [
                {
                    'course_id': int,
                    'course_code': str,
                    'course_name': str,
                    'grade_name': str,
                    'classrooms': [
                        {
                            'classroom_id': int,
                            'classroom_name': str,
                            'student_count': int,
                            'students': [...]
                        }
                    ]
                }
            ]
        }
    """
    try:
        teacher = Teacher.objects.select_related('user').get(user_id=teacher_id)
    except Teacher.DoesNotExist:
        raise ValueError("Teacher not found.")
    
    _check_teacher_permission(actor, teacher_id)
    
    allocations = CourseAllocation.objects.filter(
        teacher=teacher
    ).select_related('course', 'course__grade', 'class_room')
    
    # Group by course
    courses_dict = {}
    for alloc in allocations:
        course_id = alloc.course.id
        if course_id not in courses_dict:
            courses_dict[course_id] = {
                'course_id': course_id,
                'course_code': alloc.course.course_code,
                'course_name': alloc.course.name,
                'grade_name': alloc.course.grade.name,
                'classrooms': []
            }
        
        # Get students in this classroom
        enrollments = StudentEnrollment.objects.filter(
            class_room=alloc.class_room,
            student__enrollment_status='active'
        ).select_related('student__user')
        
        students = [
            {
                'student_id': e.student.user_id,
                'student_name': e.student.user.full_name
            }
            for e in enrollments
        ]
        
        courses_dict[course_id]['classrooms'].append({
            'classroom_id': alloc.class_room.id,
            'classroom_name': alloc.class_room.classroom_name,
            'student_count': len(students),
            'students': students
        })
    
    return {
        'teacher_id': teacher_id,
        'teacher_name': teacher.user.full_name,
        'courses': list(courses_dict.values())
    }


def get_students_by_classroom(*, teacher_id: int, actor: CustomUser) -> Dict:
    """
    Get students per assigned classroom for teacher.
    
    Returns:
        {
            'teacher_id': int,
            'teacher_name': str,
            'classrooms': [
                {
                    'classroom_id': int,
                    'classroom_name': str,
                    'grade_name': str,
                    'courses_taught': [...],
                    'student_count': int,
                    'students': [...]
                }
            ]
        }
    """
    try:
        teacher = Teacher.objects.select_related('user').get(user_id=teacher_id)
    except Teacher.DoesNotExist:
        raise ValueError("Teacher not found.")
    
    _check_teacher_permission(actor, teacher_id)
    
    # Get unique classrooms with courses
    allocations = CourseAllocation.objects.filter(
        teacher=teacher
    ).select_related('course', 'class_room', 'class_room__grade')
    
    # Group by classroom
    classrooms_dict = {}
    for alloc in allocations:
        classroom_id = alloc.class_room.id
        if classroom_id not in classrooms_dict:
            classrooms_dict[classroom_id] = {
                'classroom_id': classroom_id,
                'classroom_name': alloc.class_room.classroom_name,
                'grade_name': alloc.class_room.grade.name,
                'courses_taught': [],
                'students': None  # Will be populated once
            }
        
        classrooms_dict[classroom_id]['courses_taught'].append({
            'course_id': alloc.course.id,
            'course_code': alloc.course.course_code,
            'course_name': alloc.course.name
        })
    
    # Get students for each classroom
    for classroom_id, data in classrooms_dict.items():
        enrollments = StudentEnrollment.objects.filter(
            class_room_id=classroom_id,
            student__enrollment_status='active'
        ).select_related('student__user')
        
        students = [
            {
                'student_id': e.student.user_id,
                'student_name': e.student.user.full_name
            }
            for e in enrollments
        ]
        data['students'] = students
        data['student_count'] = len(students)
    
    return {
        'teacher_id': teacher_id,
        'teacher_name': teacher.user.full_name,
        'classrooms': list(classrooms_dict.values())
    }


def get_course_details(*, course_id: int, teacher_id: int, actor: CustomUser) -> Dict:
    """
    Get detailed course view for a teacher's assigned course.
    
    Returns:
        {
            'course_id': int,
            'course_code': str,
            'course_name': str,
            'grade_name': str,
            'school_name': str,
            'total_students': int,
            'by_classroom': [...]
        }
    """
    try:
        course = Course.objects.select_related('school', 'grade').get(id=course_id)
    except Course.DoesNotExist:
        raise ValueError("Course not found.")
    
    _check_teacher_permission(actor, teacher_id)
    
    # Get allocations for this teacher and course
    allocations = CourseAllocation.objects.filter(
        course=course,
        teacher__user_id=teacher_id
    ).select_related('class_room').annotate(
        student_count=Count(
            'class_room__enrollments__student',
            filter=Q(class_room__enrollments__student__enrollment_status='active')
        )
    )
    
    by_classroom = []
    total_students = 0
    
    for allocation in allocations:
        by_classroom.append({
            'classroom_id': allocation.class_room.id,
            'classroom_name': allocation.class_room.classroom_name,
            'student_count': allocation.student_count
        })
        total_students += allocation.student_count
    
    return {
        'course_id': course_id,
        'course_code': course.course_code,
        'course_name': course.name,
        'grade_name': course.grade.name,
        'school_name': course.school.school_name,
        'total_students': total_students,
        'by_classroom': by_classroom
    }


def get_attendance_summary(*, teacher_id: int, actor: CustomUser) -> Dict:
    """
    Get attendance statistics for teacher's classes.
    
    Returns:
        {
            'teacher_id': int,
            'teacher_name': str,
            'total_records': int,
            'by_status': {...},
            'by_course': [
                {
                    'course_id': int,
                    'course_name': str,
                    'total_records': int,
                    'present_count': int,
                    'absent_count': int,
                    'late_count': int,
                    'excused_count': int,
                    'attendance_rate': float
                }
            ]
        }
    """
    try:
        teacher = Teacher.objects.select_related('user').get(user_id=teacher_id)
    except Teacher.DoesNotExist:
        raise ValueError("Teacher not found.")
    
    _check_teacher_permission(actor, teacher_id)
    
    # Get all courses taught by this teacher
    allocations = CourseAllocation.objects.filter(
        teacher=teacher
    ).select_related('course', 'class_room')
    
    course_classroom_pairs = [
        (alloc.course_id, alloc.class_room_id)
        for alloc in allocations
    ]
    
    # Build Q filter for attendance records
    attendance_filter = Q()
    for course_id, classroom_id in course_classroom_pairs:
        attendance_filter |= Q(course_id=course_id, class_room_id=classroom_id)
    
    if not attendance_filter:
        return {
            'teacher_id': teacher_id,
            'teacher_name': teacher.user.full_name,
            'total_records': 0,
            'by_status': {},
            'by_course': []
        }
    
    # Get attendance summary by status
    status_summary = Attendance.objects.filter(
        attendance_filter
    ).values('status').annotate(count=Count('id'))
    
    by_status = {item['status']: item['count'] for item in status_summary}
    total_records = sum(by_status.values())
    
    # Get attendance by course
    course_summary = Attendance.objects.filter(
        attendance_filter
    ).values(
        'course__id', 'course__name'
    ).annotate(
        total_records=Count('id'),
        present_count=Count('id', filter=Q(status='present')),
        absent_count=Count('id', filter=Q(status='absent')),
        late_count=Count('id', filter=Q(status='late')),
        excused_count=Count('id', filter=Q(status='excused'))
    )
    
    by_course = [
        {
            'course_id': item['course__id'],
            'course_name': item['course__name'],
            'total_records': item['total_records'],
            'present_count': item['present_count'],
            'absent_count': item['absent_count'],
            'late_count': item['late_count'],
            'excused_count': item['excused_count'],
            'attendance_rate': round(
                (item['present_count'] + item['late_count']) / item['total_records'] * 100, 2
            ) if item['total_records'] > 0 else 0.0
        }
        for item in course_summary
    ]
    
    return {
        'teacher_id': teacher_id,
        'teacher_name': teacher.user.full_name,
        'total_records': total_records,
        'by_status': by_status,
        'by_course': by_course
    }


def get_assignment_stats(*, teacher_id: int, actor: CustomUser) -> Dict:
    """
    Get assignment and grade statistics for teacher.
    
    Returns:
        {
            'teacher_id': int,
            'teacher_name': str,
            'total_assignments': int,
            'by_type': {...},
            'assignments': [
                {
                    'assignment_id': int,
                    'assignment_code': str,
                    'title': str,
                    'exam_type': str,
                    'full_mark': float,
                    'due_date': str | None,
                    'graded_count': int,
                    'average_score': float | None,
                    'highest_score': float | None,
                    'lowest_score': float | None
                }
            ]
        }
    """
    try:
        teacher = Teacher.objects.select_related('user').get(user_id=teacher_id)
    except Teacher.DoesNotExist:
        raise ValueError("Teacher not found.")
    
    _check_teacher_permission(actor, teacher_id)
    
    # Get all assignments created by this teacher
    assignments = Assignment.objects.filter(
        created_by=teacher
    ).annotate(
        graded_count=Count('marks'),
        average_score=Avg('marks__score'),
        highest_score=Sum('marks__score') / Count('marks__score') if Count('marks__score') > 0 else None
    ).order_by('-due_date')
    
    # Count by type
    type_counts = Assignment.objects.filter(
        created_by=teacher
    ).values('exam_type').annotate(count=Count('id'))
    
    by_type = {item['exam_type']: item['count'] for item in type_counts}
    
    # Build assignments list with stats
    assignments_data = []
    for assignment in assignments:
        # Get score stats
        marks = Mark.objects.filter(assignment=assignment)
        mark_stats = marks.aggregate(
            avg=Avg('score'),
            highest=Sum('score'),  # Will calculate properly below
            lowest=Sum('score')
        )
        
        if marks.exists():
            scores = list(marks.values_list('score', flat=True))
            avg_score = sum(scores) / len(scores)
            highest = max(scores)
            lowest = min(scores)
        else:
            avg_score = None
            highest = None
            lowest = None
        
        assignments_data.append({
            'assignment_id': assignment.id,
            'assignment_code': assignment.assignment_code,
            'title': assignment.title,
            'exam_type': assignment.exam_type,
            'full_mark': float(assignment.full_mark),
            'due_date': str(assignment.due_date) if assignment.due_date else None,
            'graded_count': marks.count(),
            'average_score': round(float(avg_score), 2) if avg_score else None,
            'highest_score': float(highest) if highest else None,
            'lowest_score': float(lowest) if lowest else None
        })
    
    return {
        'teacher_id': teacher_id,
        'teacher_name': teacher.user.full_name,
        'total_assignments': len(assignments_data),
        'by_type': by_type,
        'assignments': assignments_data
    }


def get_teacher_dashboard_statistics(*, teacher_id: int, actor: CustomUser) -> Dict:
    """
    Get comprehensive teacher dashboard statistics.
    
    Returns combined statistics for teacher dashboard.
    """
    _check_teacher_permission(actor, teacher_id)
    
    return {
        'summary': get_teacher_summary(teacher_id=teacher_id, actor=actor),
        'attendance': get_attendance_summary(teacher_id=teacher_id, actor=actor),
        'assignments': get_assignment_stats(teacher_id=teacher_id, actor=actor)
    }

