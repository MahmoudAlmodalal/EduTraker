from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from drf_spectacular.utils import extend_schema, OpenApiParameter
from teacher.models import CourseAllocation
from teacher.serializers.course_allocation_serializers import CourseAllocationSerializer

class TeacherScheduleApi(APIView):
    """
    API view to retrieve the teacher's schedule.
    Currently returns slots derived from CourseAllocation with dummy time data.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=['Teacher - Schedule'],
        summary='Get teacher schedule',
        description='Retrieve the daily schedule for the authenticated teacher.',
        parameters=[
            OpenApiParameter(name='date', type=str, description='Date for the schedule (YYYY-MM-DD)'),
        ],
        responses={200: CourseAllocationSerializer(many=True)}
    )
    def get(self, request):
        user = request.user
        
        # Ensure user has a teacher profile
        if not hasattr(user, 'teacher_profile'):
            return Response({"detail": "User is not a teacher."}, status=status.HTTP_403_FORBIDDEN)

        # Retrieve active course allocations for the teacher
        allocations = CourseAllocation.objects.filter(
            teacher=user.teacher_profile,
            is_active=True
        ).select_related('course', 'class_room')

        # Use CourseAllocationSerializer
        # We'll allow the serializer to provide the mock time/status for now as defined in its implementation
        serializer = CourseAllocationSerializer(allocations, many=True)
        return Response(serializer.data)
