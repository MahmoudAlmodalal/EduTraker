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

from accounts.permissions import IsStaffUser, IsAdminOrManager
from reports.services.count_services import (
    get_student_count_by_teacher,
    get_student_count_by_workstream,
    get_student_count_by_school,
    get_student_count_by_school_manager,
    get_student_count_by_course,
    get_student_count_by_classroom,
    get_comprehensive_statistics
)


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
    permission_classes = [IsStaffUser]
    
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
    permission_classes = [IsStaffUser]
    
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
                    }
                },
                response_only=True
            )
        ]
    )
    def get(self, request):
        user = request.user
        stats = {}
        
        try:
            if user.role == 'admin':
                from student.models import Student
                from teacher.models import Teacher
                from workstream.models import WorkStream
                from school.models import School, ClassRoom
                
                stats = {
                    'total_students': Student.objects.filter(current_status='active').count(),
                    'total_teachers': Teacher.objects.count(),
                    'total_workstreams': WorkStream.objects.filter(is_active=True).count(),
                    'total_schools': School.objects.count(),
                    'total_classrooms': ClassRoom.objects.count(),
                    'inactive_students': Student.objects.exclude(current_status='active').count()
                }
            
            elif user.role == 'manager_workstream':
                data = get_student_count_by_workstream(
                    workstream_id=user.work_stream_id,
                    actor=user
                )
                stats = {
                    'workstream_name': data['workstream_name'],
                    'total_students': data['total_students'],
                    'school_count': data['school_count'],
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
                    'by_grade': data['by_grade'],
                    'classroom_count': len(data['by_classroom'])
                }
            
            elif user.role == 'teacher':
                data = get_student_count_by_teacher(
                    teacher_id=user.id,
                    actor=user
                )
                stats = {
                    'teacher_name': data['teacher_name'],
                    'total_students': data['total_students'],
                    'course_count': len(data['by_course']),
                    'classroom_count': len(data['by_classroom'])
                }
            
            elif user.role == 'secretary':
                from school.models import School
                from student.models import Student
                
                school = School.objects.get(id=user.school_id)
                stats = {
                    'school_name': school.school_name,
                    'total_students': Student.objects.filter(
                        school_id=user.school_id,
                        current_status='active'
                    ).count()
                }
            
            return Response({
                'role': user.role,
                'statistics': stats
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )