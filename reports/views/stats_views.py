from rest_framework import status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse
from django.core.exceptions import PermissionDenied, ValidationError

from reports.serializers import (
    TeacherStudentCountSerializer,
    WorkstreamStudentCountSerializer,
    SchoolStudentCountSerializer,
    CourseStudentCountSerializer,
    ClassroomStudentCountSerializer,
    ComprehensiveStatisticsSerializer,
    DashboardStatisticsSerializer
)

from accounts.permissions import IsStaffUser, IsAdminOrManager, IsStudent
from rest_framework.permissions import IsAuthenticated
from reports.services.count_services import (
    get_student_count_by_course,
    get_student_count_by_classroom,
    get_comprehensive_statistics,
    get_school_performance_trend,
    get_subject_performance_distribution,
    get_student_count_by_school,
    get_student_count_by_school_manager,
    get_student_count_by_teacher,
    get_student_count_by_workstream
)
from reports.services.activity_services import get_login_activity_chart
from teacher.models import Teacher, CourseAllocation, Assignment, Attendance, Mark
from student.models import StudentEnrollment
from django.db.models import Avg, Count, Q
from django.utils import timezone

class TeacherStudentCountView(APIView):
    """
    GET: Get student count for a specific teacher
    """
    permission_classes = [IsStaffUser]
    
    @extend_schema(
        tags=['Reports & Statistics'],
        summary='Get student count by teacher',
        description='Returns student count and breakdown by course/classroom for a specific teacher.',
        parameters=[OpenApiParameter(name='teacher_id', type=int, location=OpenApiParameter.PATH, description='Teacher User ID')],
        responses={
            200: TeacherStudentCountSerializer,
            403: OpenApiResponse(description='Permission Denied'),
            404: OpenApiResponse(description='Teacher not found')
        },
        examples=[
            OpenApiExample(
                'Teacher Stats Response',
                value={
                    'teacher_id': 5,
                    'teacher_name': 'John Teacher',
                    'total_students': 45,
                    'by_course': [{'course_id': 1, 'course_name': 'Math', 'count': 25}],
                    'by_classroom': [{'classroom_id': 1, 'classroom_name': '1A', 'count': 25}]
                },
                response_only=True
            )
        ]
    )
    def get(self, request, teacher_id):
        try:
            data = get_student_count_by_teacher(
                teacher_id=teacher_id,
                actor=request.user
            )
            return Response(data, status=status.HTTP_200_OK)
        
        except ValueError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except PermissionDenied as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_403_FORBIDDEN
            )


class WorkstreamStudentCountView(APIView):
    """
    GET: Get student count for a specific workstream
    """
    permission_classes = [IsAdminOrManager]
    
    @extend_schema(
        tags=['Reports & Statistics'],
        summary='Get student count by workstream',
        description='Returns student count and breakdown by school for a specific workstream.',
        parameters=[OpenApiParameter(name='workstream_id', type=int, location=OpenApiParameter.PATH, description='Workstream ID')],
        responses={
            200: WorkstreamStudentCountSerializer,
            403: OpenApiResponse(description='Permission Denied'),
            404: OpenApiResponse(description='Workstream not found')
        },
        examples=[
            OpenApiExample(
                'Workstream Stats Response',
                value={
                    'workstream_id': 1,
                    'workstream_name': 'Primary Education',
                    'total_students': 1200,
                    'school_count': 5,
                    'by_school': [{'school_id': 1, 'school_name': 'West School', 'count': 300}]
                },
                response_only=True
            )
        ]
    )
    def get(self, request, workstream_id):
        try:
            data = get_student_count_by_workstream(
                workstream_id=workstream_id,
                actor=request.user
            )
            return Response(data, status=status.HTTP_200_OK)
        
        except ValueError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except PermissionDenied as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_403_FORBIDDEN
            )


class SchoolStudentCountView(APIView):
    """
    GET: Get student count for a specific school
    """
    permission_classes = [IsAdminOrManager]
    
    @extend_schema(
        tags=['Reports & Statistics'],
        summary='Get student count by school',
        description='Returns student count and breakdown by grade/classroom for a specific school.',
        parameters=[OpenApiParameter(name='school_id', type=int, location=OpenApiParameter.PATH, description='School ID')],
        responses={
            200: SchoolStudentCountSerializer,
            403: OpenApiResponse(description='Permission Denied'),
            404: OpenApiResponse(description='School not found')
        },
        examples=[
            OpenApiExample(
                'School Stats Response',
                value={
                    'school_id': 1,
                    'school_name': 'West School',
                    'total_students': 300,
                    'by_grade': [{'grade_id': 1, 'grade_name': 'Grade 1', 'count': 50}],
                    'by_classroom': [{'classroom_id': 1, 'classroom_name': '1A', 'count': 25}]
                },
                response_only=True
            )
        ]
    )
    def get(self, request, school_id):
        try:
            data = get_student_count_by_school(
                school_id=school_id,
                actor=request.user
            )
            return Response(data, status=status.HTTP_200_OK)
        
        except ValueError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except PermissionDenied as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_403_FORBIDDEN
            )


class SchoolManagerStudentCountView(APIView):
    """
    GET: Get student count for all schools managed by a school manager
    """
    permission_classes = [IsAdminOrManager]
    
    @extend_schema(
        tags=['Reports & Statistics'],
        summary='Get student count by school manager',
        description='Returns student count across all schools managed by a specific school manager.',
        parameters=[OpenApiParameter(name='manager_id', type=int, location=OpenApiParameter.PATH, description='Manager User ID')],
        responses={
            200: OpenApiResponse(
                description='Manager stats',
                examples=[
                    OpenApiExample(
                        'Manager Stats Response',
                        value={
                            'manager_id': 2,
                            'manager_name': 'Jane Manager',
                            'total_schools': 2,
                            'total_students': 550,
                            'schools': [{'school_id': 1, 'school_name': 'West School', 'count': 300}]
                        }
                    )
                ]
            ),
            403: OpenApiResponse(description='Permission Denied'),
            404: OpenApiResponse(description='Manager not found')
        },
        examples=[
            OpenApiExample(
                'Manager Stats Response',
                value={
                    'manager_id': 2,
                    'manager_name': 'Jane Manager',
                    'total_schools': 2,
                    'total_students': 550,
                    'schools': [{'school_id': 1, 'school_name': 'West School', 'count': 300}]
                },
                response_only=True
            )
        ]
    )
    def get(self, request, manager_id):
        try:
            data = get_student_count_by_school_manager(
                manager_id=manager_id,
                actor=request.user
            )
            return Response(data, status=status.HTTP_200_OK)
        
        except ValueError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except PermissionDenied as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_403_FORBIDDEN
            )


class CourseStudentCountView(APIView):
    """
    GET: Get student count for a specific course
    """
    permission_classes = [IsStaffUser]
    
    @extend_schema(
        tags=['Reports & Statistics'],
        summary='Get student count by course',
        description='Returns student count and breakdown by classroom for a specific course.',
        parameters=[OpenApiParameter(name='course_id', type=int, location=OpenApiParameter.PATH, description='Course ID')],
        responses={
            200: CourseStudentCountSerializer,
            403: OpenApiResponse(description='Permission Denied'),
            404: OpenApiResponse(description='Course not found')
        },
        examples=[
            OpenApiExample(
                'Course Stats Response',
                value={
                    'course_id': 1,
                    'course_name': 'Mathematics 101',
                    'total_students': 150,
                    'by_classroom': [{'classroom_id': 1, 'classroom_name': '1A', 'count': 25}]
                },
                response_only=True
            )
        ]
    )
    def get(self, request, course_id):
        try:
            data = get_student_count_by_course(
                course_id=course_id,
                actor=request.user
            )
            return Response(data, status=status.HTTP_200_OK)
        
        except ValueError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except PermissionDenied as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_403_FORBIDDEN
            )


class ClassroomStudentCountView(APIView):
    """
    GET: Get student count for a specific classroom
    """
    permission_classes = [IsStaffUser]
    
    @extend_schema(
        tags=['Reports & Statistics'],
        summary='Get student count by classroom',
        description='Returns total student count for a specific classroom.',
        parameters=[OpenApiParameter(name='classroom_id', type=int, location=OpenApiParameter.PATH, description='Classroom ID')],
        responses={
            200: ClassroomStudentCountSerializer,
            403: OpenApiResponse(description='Permission Denied'),
            404: OpenApiResponse(description='Classroom not found')
        },
        examples=[
            OpenApiExample(
                'Classroom Stats Response',
                value={
                    'classroom_id': 1,
                    'classroom_name': '1A',
                    'total_students': 25
                },
                response_only=True
            )
        ]
    )
    def get(self, request, classroom_id):
        try:
            data = get_student_count_by_classroom(
                classroom_id=classroom_id,
                actor=request.user
            )
            return Response(data, status=status.HTTP_200_OK)
        
        except ValueError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except PermissionDenied as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_403_FORBIDDEN
            )


class ComprehensiveStatisticsView(APIView):
    """
    GET: Get comprehensive statistics based on user role
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        tags=['Reports & Statistics'],
        summary='Get comprehensive statistics',
        description='Get statistics tailored to the authenticated user role.',
        responses={
            200: ComprehensiveStatisticsSerializer,
            403: OpenApiResponse(description='Permission Denied')
        },
        examples=[
            OpenApiExample(
                'Comprehensive Stats Response',
                value={
                    'role': 'admin',
                    'generated_at': '2026-01-06T12:00:00Z',
                    'statistics': {'total_students': 5000, 'total_teachers': 200}
                },
                response_only=True
            )
        ]
    )
    def get(self, request):
        try:
            data = get_comprehensive_statistics(actor=request.user)
            data['activity_chart'] = get_login_activity_chart()
            return Response(data, status=status.HTTP_200_OK)
        
        except PermissionDenied as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_403_FORBIDDEN
            )


class DashboardStatisticsView(APIView):
    """
    GET: Get dashboard statistics for the current user
    This provides quick stats relevant to the user's role
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        tags=['Reports & Statistics'],
        summary='Get dashboard statistics',
        description='Get quick statistics for the dashboard based on user role.',
        responses={
            200: DashboardStatisticsSerializer,
            400: OpenApiResponse(description='Error processing request')
        },
        examples=[
            OpenApiExample(
                'Dashboard Stats Response',
                value={
                    'role': 'teacher',
                    'statistics': {
                        'teacher_name': 'John Teacher',
                        'total_students': 45,
                        'course_count': 2,
                        'classroom_count': 2
                    },
                    'recent_activity': [],
                    'activity_chart': []
                },
                response_only=True
            )
        ]
    )
    def get(self, request):
        user = request.user
        stats = {}
        recent_activity = []
        activity_chart = []
        
        try:
            # Common: Fetch recent activity relevant to the user
            from django.utils import timezone
            from datetime import timedelta
            
            # 1. Fetch Recent Activity
            from reports.models import ActivityLog
            if user.role == 'admin':
                recent_activity_qs = ActivityLog.objects.all().order_by('-created_at')[:10]
            
            elif user.role == 'manager_workstream':
                from school.models import School
                from django.db.models import Q
                
                workstream_id = getattr(user, 'work_stream_id', None)
                
                query = Q(actor=user)
                
                if workstream_id:
                    # Include events for this workstream
                    query |= Q(entity_type='Workstream', entity_id=str(workstream_id))
                    
                    # Include events for schools in this workstream
                    school_ids = list(School.objects.filter(work_stream_id=workstream_id).values_list('id', flat=True))
                    if school_ids:
                        query |= Q(entity_type='School', entity_id__in=[str(sid) for sid in school_ids])
                
                recent_activity_qs = ActivityLog.objects.filter(query).order_by('-created_at')[:10]
                
            elif user.role == 'manager_school':
                from django.db.models import Q
                school_id = getattr(user, 'school_id', None)
                
                query = Q(actor=user)
                if school_id:
                    query |= Q(entity_type='School', entity_id=str(school_id))
                    
                recent_activity_qs = ActivityLog.objects.filter(query).order_by('-created_at')[:10]
                
            else:
                # For basic users, just their own actions
                recent_activity_qs = ActivityLog.objects.filter(actor=user).order_by('-created_at')[:10]

            from reports.serializers import ActivityLogSerializer
            recent_activity = ActivityLogSerializer(recent_activity_qs, many=True).data
            
            # 2. Fetch Activity Chart (Login Frequency)
            activity_chart = get_login_activity_chart()

            if user.role == 'admin':
                from student.models import Student
                from teacher.models import Teacher
                from workstream.models import WorkStream
                from school.models import School, ClassRoom
                from accounts.models import CustomUser
                
                # Get current counts
                current_workstreams = WorkStream.objects.filter(is_active=True).count()
                current_schools = School.objects.count()
                current_users = CustomUser.objects.filter(is_active=True).count()
                
                # Calculate date 30 days ago for comparison
                thirty_days_ago = timezone.now() - timedelta(days=30)
                
                # Get counts from 30 days ago (items created before 30 days ago)
                old_workstreams = WorkStream.objects.filter(
                    is_active=True,
                    created_at__lt=thirty_days_ago
                ).count() if hasattr(WorkStream, 'created_at') else current_workstreams
                
                old_schools = School.objects.filter(
                    created_at__lt=thirty_days_ago
                ).count() if hasattr(School, 'created_at') else current_schools
                
                old_users = CustomUser.objects.filter(
                    is_active=True,
                    date_joined__lt=thirty_days_ago
                ).count()
                
                # Calculate percentage changes
                def calculate_change(current, old):
                    if old == 0:
                        return 100.0 if current > 0 else 0.0
                    return round(((current - old) / old) * 100, 1)
                
                workstreams_change = calculate_change(current_workstreams, old_workstreams)
                schools_change = calculate_change(current_schools, old_schools)
                users_change = calculate_change(current_users, old_users)
                
                stats = {
                    'total_students': Student.objects.filter(enrollment_status='active').count(),
                    'total_teachers': Teacher.objects.count(),
                    'total_workstreams': current_workstreams,
                    'total_schools': current_schools,
                    'total_classrooms': ClassRoom.objects.count(),
                    'inactive_students': Student.objects.exclude(enrollment_status='active').count(),
                    'total_users': current_users,
                    'workstreams_change': workstreams_change,
                    'schools_change': schools_change,
                    'users_change': users_change
                }
            
            elif user.role == 'manager_workstream':
                data = get_student_count_by_workstream(
                    workstream_id=user.work_stream_id,
                    actor=user
                )
                stats = {
                    'workstream_name': data['workstream_name'],
                    'total_students': data['total_students'],
                    'total_teachers': data['total_teachers'],
                    'school_count': data['school_count'],
                    'manager_count': data.get('manager_count', 0),
                    'classroom_count': data['classroom_count'],
                    'schools': data['by_school']
                }
            
            elif user.role == 'manager_school':
                data = get_student_count_by_school(
                    school_id=user.school_id,
                    actor=user
                )
                stats = {
                    'school_name': data['school_name'],
                    'total_students': data['total_students'],
                    'total_teachers': data['total_teachers'],
                    'total_secretaries': data['total_secretaries'],
                    'classroom_count': data['total_classrooms'],
                    'course_count': data['total_courses'],
                    'by_grade': data['by_grade'],
                    'subject_performance': get_subject_performance_distribution(school_id=user.school_id, actor=user)
                }
            
            elif user.role == 'teacher':
                
                teacher = Teacher.objects.filter(user_id=user.id).first()
                if not teacher:
                    return Response({'detail': 'Teacher profile not found'}, status=404)
                
                # Basic teacher summary data
                data = get_student_count_by_teacher(
                    teacher_id=user.id,
                    actor=user
                )
                
                # 1. Average Attendance
                # Get all course allocations for this teacher
                alloc_ids = CourseAllocation.objects.filter(teacher=teacher).values_list('id', flat=True)
                
                # Get attendance records for these allocations
                attendance_qs = Attendance.objects.filter(course_allocation_id__in=alloc_ids)
                total_att = attendance_qs.count()
                if total_att > 0:
                    present_late = attendance_qs.filter(status__in=['present', 'late']).count()
                    avg_attendance = (present_late / total_att) * 100
                else:
                    avg_attendance = 0
                
                # 2. Pending Assignments (Published assignments where due date is in the future)
                now = timezone.now()
                pending_assignments_count = Assignment.objects.filter(
                    created_by=teacher,
                    is_published=True,
                    due_date__gt=now
                ).count()
                
                # 3. Total Submissions to Grade
                # We'll define this as (Total Students * Published Assignments) - Total Marks
                # This is an approximation since a student might not be enrolled when an assignment was created,
                # but it's a reasonable start.
                
                # Get all published assignments by this teacher
                published_assignments = Assignment.objects.filter(
                    created_by=teacher,
                    is_published=True
                )
                
                total_to_grade = 0
                for assignment in published_assignments:
                    # Get enrollment count for the classroom assigned to this assignment
                    if assignment.course_allocation:
                        student_count = StudentEnrollment.objects.filter(
                            class_room=assignment.course_allocation.class_room,
                            student__enrollment_status='active'
                        ).count()
                        
                        # Get marks already recorded for this assignment
                        graded_count = Mark.objects.filter(assignment=assignment).count()
                        
                        # Ungraded = Student Count - Graded Count
                        ungraded = max(0, student_count - graded_count)
                        total_to_grade += ungraded
                
                stats = {
                    'teacher_name': data['teacher_name'],
                    'total_students': data['total_students'],
                    'course_count': len(data['by_course']),
                    'classroom_count': len(data['by_classroom']),
                    'average_attendance': avg_attendance,
                    'pending_assignments_count': pending_assignments_count,
                    'total_submissions_to_grade': total_to_grade
                }
            
            elif user.role == 'secretary':
                from school.models import School
                from student.models import Student
                from teacher.models import Attendance
                
                from django.utils import timezone
                
                school = School.objects.get(id=user.school_id)
                today = timezone.now().date()
                
                stats = {
                    'school_name': school.school_name,
                    'total_students': Student.objects.filter(
                        user__school_id=user.school_id,
                        enrollment_status='active'
                    ).count(),
                    'absent_today': Attendance.objects.filter(
                        student__user__school_id=user.school_id,
                        date=today,
                        status='Absent'
                    ).count(),
                    'unread_messages': 0 # Will be set correctly below
                }
                
                # Let's check the Message model in accounts or user_messages
                # Actually, looking at imports in this file:
                # from accounts.serializers import MessageSerializer
                # But wait, there is a user_messages app.
                
                from user_messages.models import MessageReceipt
                stats['unread_messages'] = MessageReceipt.objects.filter(
                    recipient=user,
                    is_read=False,
                    is_deleted=False
                ).count()
            
            elif user.role == 'student':
                from reports.services.count__student_services import get_student_dashboard_statistics
                stats = get_student_dashboard_statistics(student_id=user.id, actor=user)
            
            elif user.role == 'guardian':
                from guardian.models import GuardianStudentLink
                from django.db.models import Count, Avg
                from datetime import datetime
                
                links = GuardianStudentLink.objects.filter(guardian_id=user.id).select_related('student', 'student__user')
                student_ids = links.values_list('student_id', flat=True)
                
                # Fetch upcoming assignments for linked students
                upcoming_events = []
                if student_ids:
                    from student.models import StudentEnrollment
                    # Get all classrooms for these students
                    enrollments = StudentEnrollment.objects.filter(
                        student_id__in=student_ids
                    ).select_related('student', 'student__user', 'class_room')
                    
                    classroom_ids = enrollments.values_list('class_room_id', flat=True).distinct()
                    
                    # Get upcoming assignments for these classrooms
                    now = timezone.now()
                    upcoming_assignments = Assignment.objects.filter(
                        course_allocation__class_room_id__in=classroom_ids,
                        is_published=True,
                        due_date__gt=now
                    ).select_related('course_allocation', 'course_allocation__class_room').order_by('due_date')[:10]
                    
                    # Create a mapping of classroom to students
                    classroom_to_students = {}
                    for enrollment in enrollments:
                        classroom_id = enrollment.class_room_id
                        if classroom_id not in classroom_to_students:
                            classroom_to_students[classroom_id] = []
                        classroom_to_students[classroom_id].append(enrollment.student.user.full_name)
                    
                    # Format events for frontend
                    for assignment in upcoming_assignments:
                        classroom_id = assignment.course_allocation.class_room_id
                        students_in_class = classroom_to_students.get(classroom_id, [])
                        
                        # Format date as "MMM DD, YYYY"
                        formatted_date = assignment.due_date.strftime("%b %d, %Y")
                        
                        upcoming_events.append({
                            'id': assignment.id,
                            'title': assignment.title,
                            'date': formatted_date,
                            'child': ', '.join(students_in_class) if students_in_class else 'N/A'
                        })
                
                stats = {
                    'total_children': links.count(),
                    'children': [
                        {
                            'id': link.student_id,
                            'name': link.student.user.full_name,
                            'grade': link.student.grade.grade_name if link.student.grade else "N/A",
                            'gpa': str(link.student.current_gpa) if link.student.current_gpa else "0.0",
                        } for link in links
                    ],
                    'total_absences': sum(link.student.total_absences for link in links),
                    'upcoming_events': upcoming_events,
                }

            return Response({
                'role': user.role,
                'statistics': stats,
                'recent_activity': recent_activity,
                'activity_chart': activity_chart
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
class SchoolPerformanceView(APIView):
    """
    GET: Get academic performance trends and subject distribution for a school
    """
    permission_classes = [IsAdminOrManager]
    
    @extend_schema(
        tags=['Reports & Statistics'],
        summary='Get school performance data',
        parameters=[OpenApiParameter(name='school_id', type=int, location=OpenApiParameter.PATH, description='School ID')],
        responses={
            200: OpenApiResponse(
                description='Performance data',
                examples=[
                    OpenApiExample(
                        'School Performance Response',
                        value={
                            'performance_trend': [
                                {'month': 'Jan 2024', 'score': 85.5}
                            ],
                            'subject_performance': [
                                {'subject': 'Math', 'score': 82.0}
                            ]
                        }
                    )
                ]
            )
        }
    )
    def get(self, request, school_id=None):
        # If school_id not in path, use user school_id
        target_school_id = school_id or getattr(request.user, 'school_id', None)
        if not target_school_id:
            return Response({'detail': 'School ID required'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            trend = get_school_performance_trend(school_id=target_school_id, actor=request.user)
            distribution = get_subject_performance_distribution(school_id=target_school_id, actor=request.user)
            return Response({
                'performance_trend': trend,
                'subject_performance': distribution
            }, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
