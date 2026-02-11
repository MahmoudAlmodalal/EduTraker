from django.db.models import Count, Q, Sum, Prefetch
from django.core.exceptions import PermissionDenied
from accounts.models import CustomUser, Role
from teacher.models import CourseAllocation, Assignment, Attendance, Mark
from student.models import Student, StudentEnrollment
from typing import Dict


ACTIVE_ENROLLMENT_STATUSES = ['enrolled', 'active']


def _check_student_permission(actor: CustomUser, student_id: int, student: Student = None) -> None:
    """Check if actor has permission to access student data."""
    if actor.role == Role.ADMIN:
        return
    if actor.role == Role.MANAGER_WORKSTREAM:
        # Check if student is in the same workstream (via user.school)
        if student is None:
            student = Student.objects.filter(user_id=student_id).select_related('user__school__work_stream').first()
        if student and student.user.school and actor.work_stream_id == student.user.school.work_stream_id:
            return
        raise PermissionDenied("Access denied. Student not in your workstream.")
    if actor.role == Role.MANAGER_SCHOOL:
        # Check if student is in the same school (via user.school_id)
        if student is None:
            student = Student.objects.filter(user_id=student_id).select_related('user').first()
        if student and actor.school_id == student.user.school_id:
            return
        raise PermissionDenied("Access denied. Student not in your school.")
    if actor.role == Role.TEACHER:
        # Check if teacher teaches this student
        if student is None:
            student = Student.objects.filter(user_id=student_id).first()
        if student:
            teaches_student = CourseAllocation.objects.filter(
                teacher__user_id=actor.id,
                class_room__enrollments__student=student
            ).exists()
            if teaches_student:
                return
        raise PermissionDenied("Access denied. You don't teach this student.")
    if actor.role == Role.STUDENT:
        if actor.id == student_id:
            return
        raise PermissionDenied("Access denied. You can only view your own statistics.")
    if actor.role == Role.GUARDIAN:
        # Guardians can view their children's data
        # Note: This assumes a guardian relationship model exists
        # For now, we'll deny access - implement based on your guardian model
        raise PermissionDenied("Access denied. Guardian access not configured.")
    raise PermissionDenied("Access denied.")


def _get_active_enrollments(student: Student):
    cached_enrollments = getattr(student, 'active_enrollments', None)
    if cached_enrollments is not None:
        return cached_enrollments

    return list(StudentEnrollment.objects.filter(
        student=student,
        status__in=ACTIVE_ENROLLMENT_STATUSES
    ).select_related(
        'class_room', 'class_room__grade', 'class_room__academic_year',
        'class_room__homeroom_teacher__user'
    ))


def _get_current_enrollment(student: Student):
    active_enrollments = _get_active_enrollments(student)
    return active_enrollments[0] if active_enrollments else None


def get_student_profile_summary(
    *,
    student_id: int,
    actor: CustomUser,
    student=None,
    skip_permission_check: bool = False
) -> Dict:
    """
    Get basic enrollment info for a student.
    """
    if not student:
        try:
            student = Student.objects.select_related(
                'user', 'user__school'
            ).get(user_id=student_id)
        except Student.DoesNotExist:
            raise ValueError("Student not found.")
    
    if not skip_permission_check:
        _check_student_permission(actor, student.user_id, student=student)

    current_enrollment = _get_current_enrollment(student)
    
    current_classroom = None
    current_grade = None
    if current_enrollment:
        classroom = current_enrollment.class_room
        current_classroom = {
            'classroom_id': classroom.id,
            'classroom_name': classroom.classroom_name,
            'grade_name': classroom.grade.name,
            'academic_year': classroom.academic_year.academic_year_code,
            'homeroom_teacher': classroom.homeroom_teacher.user.full_name if classroom.homeroom_teacher else None
        }
        current_grade = {
            'grade_id': classroom.grade.id,
            'grade_name': classroom.grade.name
        }
    
    return {
        'student_id': student.user_id,
        'student_name': student.user.full_name,
        'email': student.user.email,
        'school_id': student.user.school_id,
        'school_name': student.user.school.school_name if student.user.school else None,
        'current_grade': current_grade,
        'current_status': student.enrollment_status,
        'admission_date': str(student.admission_date),
        'current_classroom': current_classroom
    }


def get_student_courses(
    *,
    student_id: int,
    actor: CustomUser,
    student=None,
    skip_permission_check: bool = False
) -> Dict:
    """
    Get enrolled courses with teachers for a student.
    """
    if not student:
        try:
            student = Student.objects.select_related('user').get(user_id=student_id)
        except Student.DoesNotExist:
            raise ValueError("Student not found.")
    
    if not skip_permission_check:
        _check_student_permission(actor, student.user_id, student=student)

    enrollments = [enrollment.class_room_id for enrollment in _get_active_enrollments(student)]
    
    # Get course allocations for those classrooms
    allocations = CourseAllocation.objects.filter(
        class_room_id__in=enrollments
    ).select_related(
        'course', 'course__grade', 'class_room', 'teacher__user'
    )
    
    courses = [
        {
            'course_id': alloc.course.id,
            'course_code': alloc.course.course_code,
            'course_name': alloc.course.name,
            'grade_name': alloc.course.grade.name,
            'classroom_id': alloc.class_room.id,
            'classroom_name': alloc.class_room.classroom_name,
            'teacher_id': alloc.teacher.user_id,
            'teacher_name': alloc.teacher.user.full_name
        }
        for alloc in allocations
    ]
    
    return {
        'student_id': student.user_id,
        'student_name': student.user.full_name,
        'total_courses': len(courses),
        'courses': courses
    }


def get_student_grades_summary(
    *,
    student_id: int,
    actor: CustomUser,
    student=None,
    skip_permission_check: bool = False
) -> Dict:
    """
    Get marks/scores overview for a student.
    """
    if not student:
        try:
            student = Student.objects.select_related('user').get(user_id=student_id)
        except Student.DoesNotExist:
            raise ValueError("Student not found.")

    if not skip_permission_check:
        _check_student_permission(actor, student.user_id, student=student)

    marks_qs = Mark.objects.filter(
        student=student
    ).select_related(
        'assignment',
        'assignment__course_allocation',
        'assignment__course_allocation__course'
    )

    aggregated_totals = marks_qs.aggregate(
        graded_assignments=Count('id'),
        total_score=Sum('score'),
        total_full_mark=Sum('assignment__full_mark')
    )

    graded_assignments = aggregated_totals['graded_assignments'] or 0
    total_score = float(aggregated_totals['total_score'] or 0)
    total_full_mark = float(aggregated_totals['total_full_mark'] or 0)

    exam_type_aggregates = marks_qs.values(
        'assignment__exam_type', 'assignment__assignment_type'
    ).annotate(
        count=Count('id'),
        total_score=Sum('score'),
        total_full_mark=Sum('assignment__full_mark')
    )

    by_type = {}
    for stats in exam_type_aggregates:
        exam_type = stats['assignment__exam_type'] or stats['assignment__assignment_type'] or 'assignment'
        exam_total_score = float(stats['total_score'] or 0)
        exam_total_full_mark = float(stats['total_full_mark'] or 0)
        by_type[exam_type] = {
            'count': stats['count'],
            'average_percentage': round(
                (exam_total_score / exam_total_full_mark) * 100, 2
            ) if exam_total_full_mark > 0 else 0
        }

    marks_data = []
    for mark in marks_qs:
        assignment = mark.assignment
        course_allocation = assignment.course_allocation
        course = course_allocation.course if course_allocation else None

        score = float(mark.score)
        full_mark = float(assignment.full_mark)
        percentage = round((score / full_mark) * 100, 2) if full_mark > 0 else 0

        marks_data.append({
            'assignment_id': assignment.id,
            'assignment_code': assignment.assignment_code,
            'title': assignment.title,
            'course_id': course.id if course else None,
            'course_name': course.name if course else "Unknown",
            'course_code': course.course_code if course else None,
            'exam_type': assignment.exam_type or assignment.assignment_type,
            'score': score,
            'full_mark': full_mark,
            'percentage': percentage,
            'due_date': str(assignment.due_date) if assignment.due_date else None
        })

    enrollment_classroom_ids = [enrollment.class_room_id for enrollment in _get_active_enrollments(student)]
    total_assignments = Assignment.objects.filter(
        course_allocation__class_room_id__in=enrollment_classroom_ids
    ).count() if enrollment_classroom_ids else 0

    overall_average = round(
        (total_score / total_full_mark) * 100, 2
    ) if total_full_mark > 0 else None

    return {
        'student_id': student.user_id,
        'student_name': student.user.full_name,
        'total_assignments': total_assignments,
        'graded_assignments': graded_assignments,
        'overall_average': overall_average,
        'by_type': by_type,
        'marks': marks_data
    }


def get_student_attendance_summary(
    *,
    student_id: int,
    actor: CustomUser,
    student=None,
    skip_permission_check: bool = False
) -> Dict:
    """
    Get attendance statistics for a student.
    """
    if not student:
        try:
            student = Student.objects.select_related('user').get(user_id=student_id)
        except Student.DoesNotExist:
            raise ValueError("Student not found.")
    
    if not skip_permission_check:
        _check_student_permission(actor, student.user_id, student=student)
    
    # Get all attendance records for this student (now via course_allocation)
    attendance_records = Attendance.objects.filter(student=student).select_related(
        'course_allocation__course'
    )
    
    # Count by status
    status_counts = attendance_records.values('status').annotate(count=Count('id'))
    by_status = {item['status']: item['count'] for item in status_counts}
    
    total_records = sum(by_status.values())
    present_and_late = by_status.get('present', 0) + by_status.get('late', 0)
    attendance_rate = round(
        (present_and_late / total_records) * 100, 2
    ) if total_records > 0 else 0
    
    # Get attendance by course (via course_allocation)
    course_stats = attendance_records.values(
        'course_allocation__course__id', 'course_allocation__course__name'
    ).annotate(
        total_records=Count('id'),
        present_count=Count('id', filter=Q(status='present')),
        absent_count=Count('id', filter=Q(status='absent')),
        late_count=Count('id', filter=Q(status='late')),
        excused_count=Count('id', filter=Q(status='excused'))
    )
    
    by_course = [
        {
            'course_id': stat['course_allocation__course__id'],
            'course_name': stat['course_allocation__course__name'],
            'total_records': stat['total_records'],
            'present_count': stat['present_count'],
            'absent_count': stat['absent_count'],
            'late_count': stat['late_count'],
            'excused_count': stat['excused_count'],
            'attendance_rate': round(
                (stat['present_count'] + stat['late_count']) / stat['total_records'] * 100, 2
            ) if stat['total_records'] > 0 else 0
        }
        for stat in course_stats
    ]
    
    return {
        'student_id': student.user_id,
        'student_name': student.user.full_name,
        'total_records': total_records,
        'attendance_rate': attendance_rate,
        'by_status': by_status,
        'by_course': by_course
    }


def get_classmates_count(
    *,
    student_id: int,
    actor: CustomUser,
    student=None,
    skip_permission_check: bool = False
) -> Dict:
    """
    Get number of classmates in current classroom.
    """
    if not student:
        try:
            student = Student.objects.select_related('user').get(user_id=student_id)
        except Student.DoesNotExist:
            raise ValueError("Student not found.")
    
    if not skip_permission_check:
        _check_student_permission(actor, student.user_id, student=student)

    current_enrollment = _get_current_enrollment(student)
    
    if not current_enrollment:
        return {
            'student_id': student.user_id,
            'student_name': student.user.full_name,
            'classroom_id': None,
            'classroom_name': None,
            'total_classmates': 0,
            'active_classmates': 0
        }
    
    classroom = current_enrollment.class_room
    
    classmates = StudentEnrollment.objects.filter(
        class_room=classroom
    ).exclude(
        student=student
    )

    classmates_totals = classmates.aggregate(
        total_classmates=Count('id'),
        active_classmates=Count('id', filter=Q(student__enrollment_status='active'))
    )

    return {
        'student_id': student.user_id,
        'student_name': student.user.full_name,
        'classroom_id': classroom.id,
        'classroom_name': classroom.classroom_name,
        'total_classmates': classmates_totals['total_classmates'] or 0,
        'active_classmates': classmates_totals['active_classmates'] or 0
    }


def get_student_dashboard_statistics(*, student_id: int, actor: CustomUser) -> Dict:
    """
    Get comprehensive student dashboard statistics.
    """
    try:
        active_enrollments_qs = StudentEnrollment.objects.filter(
            status__in=ACTIVE_ENROLLMENT_STATUSES
        ).select_related(
            'class_room',
            'class_room__grade',
            'class_room__academic_year',
            'class_room__homeroom_teacher__user'
        )

        student = Student.objects.select_related('user', 'user__school').prefetch_related(
            Prefetch('enrollments', queryset=active_enrollments_qs, to_attr='active_enrollments')
        ).get(user_id=student_id)
    except Student.DoesNotExist:
        raise ValueError("Student not found.")

    _check_student_permission(actor, student_id, student=student)
    
    return {
        'profile': get_student_profile_summary(
            student_id=student_id,
            actor=actor,
            student=student,
            skip_permission_check=True
        ),
        'courses': get_student_courses(
            student_id=student_id,
            actor=actor,
            student=student,
            skip_permission_check=True
        ),
        'grades': get_student_grades_summary(
            student_id=student_id,
            actor=actor,
            student=student,
            skip_permission_check=True
        ),
        'attendance': get_student_attendance_summary(
            student_id=student_id,
            actor=actor,
            student=student,
            skip_permission_check=True
        ),
        'classmates': get_classmates_count(
            student_id=student_id,
            actor=actor,
            student=student,
            skip_permission_check=True
        )
    }
