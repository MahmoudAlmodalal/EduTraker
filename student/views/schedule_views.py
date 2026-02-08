from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from accounts.permissions import IsStaffUser, IsStudent
from student.selectors.student_selectors import student_get
from student.models import StudentEnrollment
from teacher.models import CourseAllocation
from teacher.serializers.course_allocation_serializers import CourseAllocationSerializer

class StudentScheduleApi(APIView):
    """
    API view to retrieve a student's schedule.
    Returns slots derived from CourseAllocation for the student's enrolled classroom.
    """
    permission_classes = [IsStaffUser | IsStudent]

    @extend_schema(
        tags=['Student Management'],
        summary='Get student schedule',
        description='Retrieve the daily schedule for a specific student based on their enrollment.',
        parameters=[
            OpenApiParameter(name='student_id', type=int, location=OpenApiParameter.PATH, description='Student ID'),
            OpenApiParameter(name='date', type=str, description='Date for the schedule (YYYY-MM-DD)'),
        ],
        responses={200: CourseAllocationSerializer(many=True)}
    )
    def get(self, request, student_id):
        # 1. Get student and check permissions (student_get handles basic permission checks usually, 
        # but here we rely on permission_classes for role and student_get for object permission if needed)
        # Note: student_get might raise PermissionDenied if strict checking is enabled inside it,
        # otherwise we trust the view's permission classes.
        
        try:
           student = student_get(student_id=student_id, actor=request.user)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

        # 2. Get active enrollment to find the classroom
        enrollment = StudentEnrollment.objects.filter(
            student=student,
            status='active'
        ).select_related('class_room').first()

        if not enrollment or not enrollment.class_room:
            # Student not enrolled in any active class, return empty schedule
            return Response([])

        # 3. Retrieve active course allocations for the classroom
        allocations = CourseAllocation.objects.filter(
            class_room=enrollment.class_room,
            is_active=True
        ).select_related('course', 'class_room')

        # 4. Serialize
        # Use CourseAllocationSerializer which mocks time/status for now
        serializer = CourseAllocationSerializer(allocations, many=True)
        return Response(serializer.data)
