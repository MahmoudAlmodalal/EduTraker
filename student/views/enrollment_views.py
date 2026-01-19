from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse

from accounts.permissions import IsStaffUser, IsAdminOrManagerOrSecretary
from student.models import StudentEnrollment
from student.selectors.enrollment_selectors import (
    student_enrollment_list,
    enrollment_get,
)
from student.services.enrollment_services import (
    enrollment_create,
    enrollment_update,
    enrollment_deactivate,
    enrollment_activate,
)


# =============================================================================
# Enrollment Serializers
# =============================================================================

class EnrollmentFilterSerializer(serializers.Serializer):
    """Filter serializer for enrollment list endpoint."""
    status = serializers.CharField(required=False, help_text="Filter by status")
    include_inactive = serializers.BooleanField(default=False, help_text="Include deactivated records")


class EnrollmentInputSerializer(serializers.Serializer):
    """Input serializer for creating/updating enrollments."""
    student_id = serializers.IntegerField(required=False, help_text="Student ID")
    class_room_id = serializers.IntegerField(required=False, help_text="Classroom ID")
    academic_year_id = serializers.IntegerField(required=False, help_text="Academic year ID")
    status = serializers.ChoiceField(choices=['enrolled', 'completed', 'withdrawn', 'transferred'], required=False, help_text="Enrollment status")
    completion_date = serializers.DateField(required=False, help_text="Completion date", allow_null=True)


class EnrollmentOutputSerializer(serializers.ModelSerializer):
    """Output serializer for enrollment responses."""
    student_name = serializers.CharField(source='student.user.full_name', read_only=True)
    classroom_name = serializers.CharField(source='class_room.classroom_name', read_only=True)
    academic_year_code = serializers.CharField(source='academic_year.academic_year_code', read_only=True)
    grade_name = serializers.CharField(source='class_room.grade.name', read_only=True)
    
    deactivated_by_name = serializers.CharField(source='deactivated_by.full_name', read_only=True, allow_null=True)

    class Meta:
        model = StudentEnrollment
        fields = [
            'id', 'student_id', 'student_name', 'class_room', 'classroom_name', 
            'academic_year', 'academic_year_code', 'grade_name', 'status',
            'is_active', 'deactivated_at', 'deactivated_by', 'deactivated_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'deactivated_by_name']


# =============================================================================
# Enrollment Views
# =============================================================================

class StudentEnrollmentListApi(APIView):
    """List enrollments for a specific student."""
    permission_classes = [IsStaffUser]

    @extend_schema(
        tags=['Student Enrollment'],
        summary='List student enrollments',
        description='Get all enrollments for a specific student.',
        parameters=[
            OpenApiParameter(name='student_id', type=int, location=OpenApiParameter.PATH, description='Student ID'),
            OpenApiParameter(name='status', type=str, description='Filter by status'),
            OpenApiParameter(name='include_inactive', type=bool, description='Include deactivated records'),
        ],
        responses={200: EnrollmentOutputSerializer(many=True)},
        examples=[
            OpenApiExample(
                'Enrollment List Response',
                value=[{
                    'id': 1,
                    'student_id': 5,
                    'student_name': 'John Student',
                    'class_room': 1,
                    'classroom_name': 'Class 1A',
                    'academic_year': 1,
                    'academic_year_code': '2024-2025',
                    'grade_name': 'Grade 1',
                    'status': 'enrolled'
                }],
                response_only=True
            )
        ]
    )
    def get(self, request, student_id):
        filter_serializer = EnrollmentFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        enrollments = student_enrollment_list(
            student_id=student_id, 
            actor=request.user,
            include_inactive=filter_serializer.validated_data.get('include_inactive', False)
        )
        # Apply status filter if provided
        if status_filter := filter_serializer.validated_data.get('status'):
            enrollments = enrollments.filter(status=status_filter)
            
        return Response(EnrollmentOutputSerializer(enrollments, many=True).data)


class EnrollmentCreateApi(APIView):
    """Create a new enrollment."""
    permission_classes = [IsAdminOrManagerOrSecretary]

    @extend_schema(
        tags=['Student Enrollment'],
        summary='Create enrollment',
        description='Create a new student enrollment in a classroom.',
        request=EnrollmentInputSerializer,
        examples=[OpenApiExample('Create Request', value={'student_id': 1, 'class_room_id': 1, 'academic_year_id': 1, 'status': 'enrolled'}, request_only=True)],
        responses={
            201: OpenApiResponse(
                response=EnrollmentOutputSerializer,
                examples=[
                    OpenApiExample(
                        'Enrollment Created',
                        value={
                            'id': 10,
                            'student_id': 5,
                            'student_name': 'John Student',
                            'class_room': 2,
                            'classroom_name': 'Class 2A',
                            'academic_year': 2,
                            'academic_year_code': '2025-2026',
                            'grade_name': 'Grade 2',
                            'status': 'enrolled'
                        }
                    )
                ]
            ),
            400: OpenApiResponse(description='Validation error')
        }
    )
    def post(self, request):
        serializer = EnrollmentInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        required = ['student_id', 'class_room_id', 'academic_year_id']
        missing = [f for f in required if f not in data]
        if missing:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({f: "This field is required." for f in missing})
        enrollment = enrollment_create(
            creator=request.user, student_id=data['student_id'],
            class_room_id=data['class_room_id'], academic_year_id=data['academic_year_id'], status=data.get('status', 'enrolled'),
        )
        return Response(EnrollmentOutputSerializer(enrollment).data, status=status.HTTP_201_CREATED)


class EnrollmentDetailApi(APIView):
    """Retrieve, update, or deactivate a specific enrollment."""
    permission_classes = [IsAdminOrManagerOrSecretary]

    @extend_schema(
        tags=['Student Enrollment'],
        summary='Get enrollment details',
        description='Retrieve details of a specific enrollment.',
        parameters=[OpenApiParameter(name='enrollment_id', type=int, location=OpenApiParameter.PATH, description='Enrollment ID')],
        responses={
            200: OpenApiResponse(
                response=EnrollmentOutputSerializer,
                examples=[
                    OpenApiExample(
                        'Enrollment Details',
                        value={
                            'id': 1,
                            'student_id': 5,
                            'student_name': 'John Student',
                            'class_room': 1,
                            'classroom_name': 'Class 1A',
                            'academic_year': 1,
                            'academic_year_code': '2024-2025',
                            'grade_name': 'Grade 1',
                            'status': 'enrolled'
                        }
                    )
                ]
            )
        }
    )
    def get(self, request, enrollment_id):
        enrollment = enrollment_get(enrollment_id=enrollment_id, actor=request.user)
        return Response(EnrollmentOutputSerializer(enrollment).data)

    @extend_schema(
        tags=['Student Enrollment'],
        summary='Update enrollment',
        description='Update an enrollment status.',
        parameters=[OpenApiParameter(name='enrollment_id', type=int, location=OpenApiParameter.PATH, description='Enrollment ID')],
        request=EnrollmentInputSerializer,
        examples=[OpenApiExample('Update Request', value={'status': 'completed'}, request_only=True)],
        responses={
            200: OpenApiResponse(
                response=EnrollmentOutputSerializer,
                examples=[
                    OpenApiExample(
                        'Enrollment Updated',
                        value={
                            'id': 1,
                            'student_id': 5,
                            'student_name': 'John Student',
                            'class_room': 1,
                            'classroom_name': 'Class 1A',
                            'academic_year': 1,
                            'academic_year_code': '2024-2025',
                            'grade_name': 'Grade 1',
                            'status': 'completed'
                        }
                    )
                ]
            )
        }
    )
    def patch(self, request, enrollment_id):
        enrollment = enrollment_get(enrollment_id=enrollment_id, actor=request.user)
        serializer = EnrollmentInputSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_enrollment = enrollment_update(enrollment=enrollment, actor=request.user, data=serializer.validated_data)
        return Response(EnrollmentOutputSerializer(updated_enrollment).data)


class EnrollmentDeactivateApi(APIView):
    """Deactivate an enrollment."""
    permission_classes = [IsAdminOrManagerOrSecretary]

    @extend_schema(
        tags=['Student Enrollment'],
        summary='Deactivate enrollment',
        description='Deactivate an enrollment (soft delete).',
        parameters=[OpenApiParameter(name='enrollment_id', type=int, location=OpenApiParameter.PATH, description='Enrollment ID')],
        responses={204: OpenApiResponse(description='Deactivated successfully')}
    )
    def post(self, request, enrollment_id):
        enrollment = enrollment_get(enrollment_id=enrollment_id, actor=request.user)
        enrollment_deactivate(enrollment=enrollment, actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class EnrollmentActivateApi(APIView):
    """Activate an enrollment."""
    permission_classes = [IsAdminOrManagerOrSecretary]

    @extend_schema(
        tags=['Student Enrollment'],
        summary='Activate enrollment',
        description='Activate a previously deactivated enrollment.',
        parameters=[OpenApiParameter(name='enrollment_id', type=int, location=OpenApiParameter.PATH, description='Enrollment ID')],
        responses={204: OpenApiResponse(description='Activated successfully')}
    )
    def post(self, request, enrollment_id):
        enrollment = enrollment_get(enrollment_id=enrollment_id, actor=request.user, include_inactive=True)
        enrollment_activate(enrollment=enrollment, actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
