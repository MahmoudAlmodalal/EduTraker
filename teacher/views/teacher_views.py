from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse

from accounts.permissions import IsAdminOrManagerOrSecretary
from teacher.models import Teacher
from teacher.selectors.teacher_selectors import teacher_list, teacher_get
from teacher.services.teacher_services import (
    teacher_create,
    teacher_update,
    teacher_deactivate,
    teacher_activate,
)


# =============================================================================
# Teacher Serializers
# =============================================================================

class TeacherFilterSerializer(serializers.Serializer):
    """Filter serializer for teacher list endpoint."""
    school_id = serializers.IntegerField(required=False, help_text="Filter by school")
    specialization = serializers.CharField(required=False, help_text="Filter by specialization")
    search = serializers.CharField(required=False, help_text="Search by name or email")
    include_inactive = serializers.BooleanField(default=False, help_text="Include deactivated records")


class TeacherInputSerializer(serializers.Serializer):
    """Input serializer for creating/updating teachers."""
    email = serializers.EmailField(required=False, help_text="Email address")
    full_name = serializers.CharField(max_length=150, required=False, help_text="Full name")
    password = serializers.CharField(write_only=True, required=False, help_text="Password")
    school_id = serializers.IntegerField(required=False, help_text="School ID")
    specialization = serializers.CharField(max_length=100, required=False, allow_blank=True, allow_null=True, help_text="Specialization")
    hire_date = serializers.DateField(required=False, help_text="Hire date")
    employment_status = serializers.ChoiceField(choices=['full_time', 'part_time', 'contract', 'substitute'], required=False, help_text="Employment status")
    highest_degree = serializers.CharField(max_length=100, required=False, allow_blank=True, allow_null=True, help_text="Highest degree")
    years_of_experience = serializers.IntegerField(required=False, allow_null=True, help_text="Years of experience")
    office_location = serializers.CharField(max_length=100, required=False, allow_blank=True, allow_null=True, help_text="Office location")


class TeacherOutputSerializer(serializers.ModelSerializer):
    """Output serializer for teacher responses."""
    email = serializers.EmailField(source='user.email', read_only=True)
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    is_active = serializers.BooleanField(source='user.is_active', read_only=True)
    school_id = serializers.IntegerField(source='user.school_id', read_only=True, allow_null=True)
    school_name = serializers.CharField(source='user.school.school_name', read_only=True, allow_null=True)
    
    deactivated_at = serializers.DateTimeField(source='user.deactivated_at', read_only=True)
    deactivated_by_name = serializers.CharField(source='user.deactivated_by.full_name', read_only=True, allow_null=True)

    class Meta:
        model = Teacher
        fields = [
            'user_id', 'email', 'full_name', 'is_active',
            'school_id', 'school_name', 'specialization', 'hire_date',
            'employment_status', 'highest_degree', 'years_of_experience',
            'office_location', 'deactivated_at', 'deactivated_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user_id', 'created_at', 'updated_at', 'deactivated_by_name']


# =============================================================================
# Teacher Views
# =============================================================================

class TeacherListApi(APIView):
    """List all teachers accessible to the current user."""
    permission_classes = [IsAdminOrManagerOrSecretary]

    @extend_schema(
        tags=['Teacher Management'],
        summary='List teachers',
        description='Get all teachers filtered by permissions and filters.',
        parameters=[
            OpenApiParameter(name='school_id', type=int, description='Filter by school'),
            OpenApiParameter(name='specialization', type=str, description='Filter by specialization'),
            OpenApiParameter(name='search', type=str, description='Search by name or email'),
            OpenApiParameter(name='include_inactive', type=bool, description='Include deactivated records'),
        ],
        responses={200: TeacherOutputSerializer(many=True)},
        examples=[
            OpenApiExample(
                'Teacher List Response',
                value=[{
                    'user_id': 30,
                    'email': 'teacher1@example.com',
                    'full_name': 'Jane Teacher',
                    'is_active': True,
                    'school_id': 1,
                    'school_name': 'Global Academy',
                    'specialization': 'Mathematics',
                    'hire_date': '2020-08-15',
                    'employment_status': 'full_time'
                }],
                response_only=True
            )
        ]
    )
    def get(self, request):
        filter_serializer = TeacherFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        teachers = teacher_list(
            filters=filter_serializer.validated_data, 
            user=request.user,
            include_inactive=filter_serializer.validated_data.get('include_inactive', False)
        )
        return Response(TeacherOutputSerializer(teachers, many=True).data)


class TeacherCreateApi(APIView):
    """Create a new teacher."""
    permission_classes = [IsAdminOrManagerOrSecretary]

    @extend_schema(
        tags=['Teacher Management'],
        summary='Create teacher',
        description='Create a new teacher with user account.',
        request=TeacherInputSerializer,
        examples=[OpenApiExample('Create Request', value={
            'email': 'teacher@school.com', 'full_name': 'Jane Teacher', 'password': 'SecurePass123!',
            'school_id': 1, 'hire_date': '2024-01-01', 'employment_status': 'full_time'
        }, request_only=True)],
        responses={
            201: OpenApiResponse(
                response=TeacherOutputSerializer,
                examples=[
                    OpenApiExample(
                        'Teacher Created',
                        value={
                            'user_id': 31,
                            'email': 'jane.doe@example.com',
                            'full_name': 'Jane Doe',
                            'is_active': True,
                            'school_id': 1,
                            'school_name': 'Global Academy',
                            'specialization': 'Science',
                            'hire_date': '2024-01-01',
                            'employment_status': 'full_time'
                        }
                    )
                ]
            ),
            400: OpenApiResponse(description='Validation error')
        }
    )
    def post(self, request):
        serializer = TeacherInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        required = ['email', 'full_name', 'password', 'school_id', 'hire_date', 'employment_status']
        missing = [f for f in required if f not in data]
        if missing:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({f: "This field is required." for f in missing})
        teacher = teacher_create(
            creator=request.user, email=data['email'], full_name=data['full_name'], password=data['password'],
            school_id=data['school_id'], hire_date=data['hire_date'], employment_status=data['employment_status'],
            specialization=data.get('specialization'), highest_degree=data.get('highest_degree'),
            years_of_experience=data.get('years_of_experience'), office_location=data.get('office_location'),
        )
        return Response(TeacherOutputSerializer(teacher).data, status=status.HTTP_201_CREATED)


class TeacherDetailApi(APIView):
    """Retrieve, update, or deactivate a specific teacher."""
    permission_classes = [IsAdminOrManagerOrSecretary]

    @extend_schema(
        tags=['Teacher Management'],
        summary='Get teacher details',
        description='Retrieve details of a specific teacher.',
        parameters=[OpenApiParameter(name='teacher_id', type=int, location=OpenApiParameter.PATH, description='Teacher ID')],
        responses={
            200: OpenApiResponse(
                response=TeacherOutputSerializer,
                examples=[
                    OpenApiExample(
                        'Teacher Details',
                        value={
                            'user_id': 30,
                            'email': 'teacher1@example.com',
                            'full_name': 'Jane Teacher',
                            'is_active': True,
                            'school_id': 1,
                            'school_name': 'Global Academy',
                            'specialization': 'Mathematics',
                            'hire_date': '2020-08-15',
                            'employment_status': 'full_time'
                        }
                    )
                ]
            )
        }
    )
    def get(self, request, teacher_id):
        teacher = teacher_get(teacher_id=teacher_id, actor=request.user)
        return Response(TeacherOutputSerializer(teacher).data)

    @extend_schema(
        tags=['Teacher Management'],
        summary='Update teacher',
        description='Update a teacher with partial data.',
        parameters=[OpenApiParameter(name='teacher_id', type=int, location=OpenApiParameter.PATH, description='Teacher ID')],
        request=TeacherInputSerializer,
        examples=[OpenApiExample('Update Request', value={'specialization': 'Physics'}, request_only=True)],
        responses={
            200: OpenApiResponse(
                response=TeacherOutputSerializer,
                examples=[
                    OpenApiExample(
                        'Teacher Updated',
                        value={
                            'user_id': 30,
                            'email': 'teacher1@example.com',
                            'full_name': 'Jane Teacher',
                            'is_active': True,
                            'school_id': 1,
                            'school_name': 'Global Academy',
                            'specialization': 'Physics',
                            'hire_date': '2020-08-15',
                            'employment_status': 'full_time'
                        }
                    )
                ]
            )
        }
    )
    def patch(self, request, teacher_id):
        teacher = teacher_get(teacher_id=teacher_id, actor=request.user)
        serializer = TeacherInputSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_teacher = teacher_update(teacher=teacher, actor=request.user, data=serializer.validated_data)
        return Response(TeacherOutputSerializer(updated_teacher).data)


class TeacherDeactivateApi(APIView):
    """Deactivate a teacher profile."""
    permission_classes = [IsAdminOrManagerOrSecretary]

    @extend_schema(
        tags=['Teacher Management'],
        summary='Deactivate teacher',
        description='Deactivate a teacher profile (soft delete).',
        parameters=[OpenApiParameter(name='teacher_id', type=int, location=OpenApiParameter.PATH, description='Teacher ID')],
        responses={204: OpenApiResponse(description='Deactivated successfully')}
    )
    def post(self, request, teacher_id):
        teacher = teacher_get(teacher_id=teacher_id, actor=request.user)
        teacher_deactivate(teacher=teacher, actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TeacherActivateApi(APIView):
    """Activate a teacher profile."""
    permission_classes = [IsAdminOrManagerOrSecretary]

    @extend_schema(
        tags=['Teacher Management'],
        summary='Activate teacher',
        description='Activate a previously deactivated teacher profile.',
        parameters=[OpenApiParameter(name='teacher_id', type=int, location=OpenApiParameter.PATH, description='Teacher ID')],
        responses={204: OpenApiResponse(description='Activated successfully')}
    )
    def post(self, request, teacher_id):
        teacher = teacher_get(teacher_id=teacher_id, actor=request.user, include_inactive=True)
        teacher_activate(teacher=teacher, actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
