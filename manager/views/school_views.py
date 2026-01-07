from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse

from accounts.models import CustomUser
from accounts.permissions import IsAdminOrManager
from school.models import School
from manager.selectors.school_selectors import school_list, school_get
from manager.services.school_services import school_create, school_update, school_delete


# =============================================================================
# School Serializers
# =============================================================================

class SchoolInputSerializer(serializers.Serializer):
    """Input serializer for creating/updating schools."""
    school_name = serializers.CharField(max_length=255, help_text="School name")
    work_stream_id = serializers.IntegerField(help_text="Workstream ID")
    manager_id = serializers.IntegerField(help_text="Manager user ID")


class SchoolOutputSerializer(serializers.ModelSerializer):
    """Output serializer for school responses."""
    work_stream_name = serializers.CharField(source='work_stream.name', read_only=True)
    manager_name = serializers.CharField(source='manager.full_name', read_only=True, allow_null=True)

    class Meta:
        model = School
        fields = ['id', 'school_name', 'work_stream', 'work_stream_name', 'manager', 'manager_name']
        read_only_fields = ['id']


class SchoolFilterSerializer(serializers.Serializer):
    """Filter serializer for school list endpoint."""
    name = serializers.CharField(required=False, help_text="Filter by name")
    work_stream_id = serializers.IntegerField(required=False, help_text="Filter by workstream")
    manager_id = serializers.IntegerField(required=False, help_text="Filter by manager")

# =============================================================================
# School Views
# =============================================================================

class SchoolListApi(APIView):
    """List all schools accessible to the current user."""
    permission_classes = [IsAdminOrManager]

    @extend_schema(
        tags=['School Management'],
        summary='List all schools',
        description='Get a list of all schools. Filtered by user role permissions.',
        parameters=[
            OpenApiParameter(name='name', type=str, description='Filter by school name'),
            OpenApiParameter(name='work_stream_id', type=int, description='Filter by workstream ID'),
            OpenApiParameter(name='manager_id', type=int, description='Filter by manager ID'),
        ],
        responses={
            200: SchoolOutputSerializer(many=True),
        },
        examples=[
            OpenApiExample(
                'School List',
                value=[{'id': 1, 'school_name': 'Main School', 'work_stream': 1, 'work_stream_name': 'Main Workstream', 'manager': 2, 'manager_name': 'John Manager'}],
                response_only=True, status_codes=['200']
            )
        ]
    )
    def get(self, request):
        """Return list of schools filtered by user permissions."""
        filter_serializer = SchoolFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)

        schools = school_list(
            filters=filter_serializer.validated_data,
            user=request.user
        )

        return Response(SchoolOutputSerializer(schools, many=True).data)


class SchoolCreateApi(APIView):
    """Create a new school."""
    permission_classes = [IsAdminOrManager]

    @extend_schema(
        tags=['School Management'],
        summary='Create a new school',
        description='Create a new school with specified workstream and manager.',
        request=SchoolInputSerializer,
        examples=[
            OpenApiExample(
                'Create School Request',
                value={
                    'school_name': 'New School',
                    'work_stream_id': 1,
                    'manager_id': 2
                },
                request_only=True,
            ),
        ],
        responses={
            201: OpenApiResponse(
                response=SchoolOutputSerializer,
                examples=[OpenApiExample('Created School', value={'id': 5, 'school_name': 'New School', 'work_stream': 1, 'work_stream_name': 'Main Workstream', 'manager': 2, 'manager_name': 'John Manager'})]
            ),
            400: OpenApiResponse(description='Validation error'),
        }
    )
    def post(self, request):
        """Create a new school."""
        serializer = SchoolInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        school = school_create(
            creator=request.user,
            school_name=serializer.validated_data['school_name'],
            work_stream_id=serializer.validated_data['work_stream_id'],
            manager_id=serializer.validated_data['manager_id'],
        )

        return Response(
            SchoolOutputSerializer(school).data,
            status=status.HTTP_201_CREATED
        )


class SchoolDetailApi(APIView):
    """Retrieve, update, or delete a specific school."""
    permission_classes = [IsAdminOrManager]

    @extend_schema(
        tags=['School Management'],
        summary='Get school details',
        description='Retrieve details of a specific school.',
        parameters=[OpenApiParameter(name='school_id', type=int, location=OpenApiParameter.PATH, description='School ID')],
        responses={
            200: OpenApiResponse(
                response=SchoolOutputSerializer,
                examples=[OpenApiExample('School Details', value={'id': 1, 'school_name': 'Main School', 'work_stream': 1, 'work_stream_name': 'Main Workstream', 'manager': 2, 'manager_name': 'John Manager'})]
            )
        }
    )
    def get(self, request, school_id):
        """Retrieve a single school by ID."""
        school = school_get(school_id=school_id, actor=request.user)
        return Response(SchoolOutputSerializer(school).data)

    @extend_schema(
        tags=['School Management'],
        summary='Update a school',
        description='Update school details.',
        parameters=[OpenApiParameter(name='school_id', type=int, location=OpenApiParameter.PATH, description='School ID')],
        request=SchoolInputSerializer,
        examples=[
            OpenApiExample(
                'Update School Request',
                value={'school_name': 'Updated School Name'},
                request_only=True,
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=SchoolOutputSerializer,
                examples=[OpenApiExample('Updated School', value={'id': 1, 'school_name': 'Updated School Name', 'work_stream': 1, 'work_stream_name': 'Main Workstream', 'manager': 2, 'manager_name': 'John Manager'})]
            )
        }
    )
    def patch(self, request, school_id):
        """Update a school with partial data."""
        school = school_get(school_id=school_id, actor=request.user)

        serializer = SchoolInputSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        updated_school = school_update(
            school=school,
            actor=request.user,
            data=serializer.validated_data
        )

        return Response(SchoolOutputSerializer(updated_school).data)

    @extend_schema(
        tags=['School Management'],
        summary='Delete a school',
        description='Delete a school permanently.',
        parameters=[OpenApiParameter(name='school_id', type=int, location=OpenApiParameter.PATH, description='School ID')],
        responses={204: OpenApiResponse(description='School deleted successfully')}
    )
    def delete(self, request, school_id):
        """Delete a school."""
        school = school_get(school_id=school_id, actor=request.user)
        school_delete(school=school, actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)