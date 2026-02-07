from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse

from accounts.permissions import IsAdminOrManager, IsAdminOrManagerOrSecretary
from accounts.pagination import PaginatedAPIMixin
from school.models import Grade
from school.selectors.grade_selectors import grade_list, grade_get
from school.services.grade_services import grade_create, grade_update, grade_deactivate, grade_activate


# =============================================================================
# Grade Serializers
# =============================================================================

class GradeInputSerializer(serializers.Serializer):
    """Input serializer for creating/updating grades."""
    name = serializers.CharField(max_length=50, required=False, help_text="Grade name")
    numeric_level = serializers.IntegerField(required=False, help_text="Numeric level (e.g., 1-12)")
    min_age = serializers.IntegerField(required=False, help_text="Minimum age")
    max_age = serializers.IntegerField(required=False, help_text="Maximum age")


class GradeOutputSerializer(serializers.ModelSerializer):
    """Output serializer for grade responses."""
    deactivated_by_name = serializers.CharField(source='deactivated_by.full_name', read_only=True, allow_null=True)

    class Meta:
        model = Grade
        fields = [
            'id', 'name', 'numeric_level', 'min_age', 'max_age',
            'is_active', 'deactivated_at', 'deactivated_by', 'deactivated_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'deactivated_by_name']


class GradeFilterSerializer(serializers.Serializer):
    """Filter serializer for grade list endpoint."""
    name = serializers.CharField(required=False, help_text="Filter by name")
    numeric_level = serializers.IntegerField(required=False, help_text="Filter by level")
    include_inactive = serializers.BooleanField(default=False, help_text="Include deactivated records")


# =============================================================================
# Grade Views
# =============================================================================

class GradeListApi(PaginatedAPIMixin, APIView):
    """List all grades."""
    permission_classes = [IsAdminOrManagerOrSecretary]

    @extend_schema(
        tags=['Grade Management'],
        summary='List grades',
        description='Get all available grades.',
        parameters=[
            OpenApiParameter(name='name', type=str, description='Filter by name'),
            OpenApiParameter(name='numeric_level', type=int, description='Filter by level'),
            OpenApiParameter(name='include_inactive', type=bool, description='Include deactivated records'),
            OpenApiParameter(name='page', type=int, description='Page number'),
        ],
        responses={200: GradeOutputSerializer(many=True)},
        examples=[
            OpenApiExample(
                'Grade List Response',
                value=[{
                    'id': 1,
                    'name': 'Grade 1',
                    'numeric_level': 1,
                    'min_age': 6,
                    'max_age': 7
                }],
                response_only=True
            )
        ]
    )
    def get(self, request):
        filter_serializer = GradeFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        grades = grade_list(
            actor=request.user,
            filters=filter_serializer.validated_data,
            include_inactive=filter_serializer.validated_data.get('include_inactive', False)
        )
        page = self.paginate_queryset(grades)
        if page is not None:
            return self.get_paginated_response(GradeOutputSerializer(page, many=True).data)
        return Response(GradeOutputSerializer(grades, many=True).data)


class GradeCreateApi(APIView):
    """Create a new grade."""
    permission_classes = [IsAdminOrManager]

    @extend_schema(
        tags=['Grade Management'],
        summary='Create grade',
        description='Create a new grade. Admin only.',
        request=GradeInputSerializer,
        examples=[OpenApiExample('Create Request', value={'name': 'Grade 1', 'numeric_level': 1, 'min_age': 6, 'max_age': 7}, request_only=True)],
        responses={
            201: OpenApiResponse(
                response=GradeOutputSerializer,
                examples=[
                    OpenApiExample(
                        'Grade Created',
                        value={
                            'id': 10,
                            'name': 'Grade 10',
                            'numeric_level': 10,
                            'min_age': 15,
                            'max_age': 16
                        }
                    )
                ]
            ),
            400: OpenApiResponse(description='Validation error')
        }
    )
    def post(self, request):
        serializer = GradeInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        grade = grade_create(
            creator=request.user,
            name=serializer.validated_data['name'],
            numeric_level=serializer.validated_data['numeric_level'],
            min_age=serializer.validated_data['min_age'],
            max_age=serializer.validated_data['max_age'],
        )
        return Response(GradeOutputSerializer(grade).data, status=status.HTTP_201_CREATED)


class GradeDetailApi(APIView):
    """Retrieve, update, or deactivate a specific grade."""
    permission_classes = [IsAdminOrManager]

    @extend_schema(
        tags=['Grade Management'],
        summary='Get grade details',
        description='Retrieve details of a specific grade.',
        parameters=[OpenApiParameter(name='grade_id', type=int, location=OpenApiParameter.PATH, description='Grade ID')],
        responses={
            200: OpenApiResponse(
                response=GradeOutputSerializer,
                examples=[
                    OpenApiExample(
                        'Grade Details',
                        value={
                            'id': 1,
                            'name': 'Grade 1',
                            'numeric_level': 1,
                            'min_age': 6,
                            'max_age': 7
                        }
                    )
                ]
            )
        }
    )
    def get(self, request, grade_id):
        grade = grade_get(actor=request.user, grade_id=grade_id)
        return Response(GradeOutputSerializer(grade).data)

    @extend_schema(
        tags=['Grade Management'],
        summary='Update grade',
        description='Update a grade with partial data.',
        parameters=[OpenApiParameter(name='grade_id', type=int, location=OpenApiParameter.PATH, description='Grade ID')],
        request=GradeInputSerializer,
        examples=[OpenApiExample('Update Request', value={'name': 'Grade 2'}, request_only=True)],
        responses={
            200: OpenApiResponse(
                response=GradeOutputSerializer,
                examples=[
                    OpenApiExample(
                        'Grade Updated',
                        value={
                            'id': 1,
                            'name': 'Grade 2',
                            'numeric_level': 2,
                            'min_age': 7,
                            'max_age': 8
                        }
                    )
                ]
            )
        }
    )
    def patch(self, request, grade_id):
        grade = grade_get(actor=request.user, grade_id=grade_id)
        serializer = GradeInputSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_grade = grade_update(grade=grade, actor=request.user, data=serializer.validated_data)
        return Response(GradeOutputSerializer(updated_grade).data)


class GradeDeactivateApi(APIView):
    """Deactivate a grade."""
    permission_classes = [IsAdminOrManager]

    @extend_schema(
        tags=['Grade Management'],
        summary='Deactivate grade',
        description='Deactivate a grade (soft delete).',
        parameters=[OpenApiParameter(name='grade_id', type=int, location=OpenApiParameter.PATH, description='Grade ID')],
        request=None,
        responses={204: OpenApiResponse(description='Deactivated successfully')}
    )
    def post(self, request, grade_id):
        grade = grade_get(actor=request.user, grade_id=grade_id)
        grade_deactivate(grade=grade, actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class GradeActivateApi(APIView):
    """Activate a grade."""
    permission_classes = [IsAdminOrManager]

    @extend_schema(
        tags=['Grade Management'],
        summary='Activate grade',
        description='Activate a previously deactivated grade.',
        parameters=[OpenApiParameter(name='grade_id', type=int, location=OpenApiParameter.PATH, description='Grade ID')],
        request=None,
        responses={204: OpenApiResponse(description='Activated successfully')}
    )
    def post(self, request, grade_id):
        grade = grade_get(actor=request.user, grade_id=grade_id, include_inactive=True)
        grade_activate(grade=grade, actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)