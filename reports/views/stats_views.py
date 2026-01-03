from rest_framework import status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.exceptions import PermissionDenied, ValidationError

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
    
    def get(self, request):
        user = request.user
        stats = {}
        
        try:
            if user.role == 'admin':
                from student.models import Student
                from teacher.models import Teacher
                from workstream.models import WorkStream
                from manager.models import School, ClassRoom
                
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
                from manager.models import School
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