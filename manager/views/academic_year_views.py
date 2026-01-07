from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse

from accounts.permissions import IsAdminOrManager
from school.models import AcademicYear
from manager.selectors.school_selectors import school_get
from manager.selectors.academic_year_selectors import academic_year_list, academic_year_get
from manager.services.academic_year_services import academic_year_create, academic_year_update, academic_year_delete


# =============================================================================
# AcademicYear Serializers
# =============================================================================

class AcademicYearInputSerializer(serializers.Serializer):
    """Input serializer for creating/updating academic years."""
    academic_year_code = serializers.CharField(max_length=20, required=False, help_text="Year code like '2025-2026'")
    start_date = serializers.DateField(required=False, help_text="Start date")
    end_date = serializers.DateField(required=False, help_text="End date")


class AcademicYearOutputSerializer(serializers.ModelSerializer):
    """Output serializer for academic year responses."""
    class Meta:
        model = AcademicYear
        fields = ['id', 'academic_year_code', 'school', 'start_date', 'end_date']
        read_only_fields = ['id', 'school']


class AcademicYearFilterSerializer(serializers.Serializer):
    """Filter serializer for academic year list endpoint."""
    academic_year_code = serializers.CharField(required=False, help_text="Filter by year code")


# =============================================================================
# AcademicYear Views
# =============================================================================

class AcademicYearListApi(APIView):
    """List academic years for a specific school."""
    permission_classes = [IsAdminOrManager]

    @extend_schema(
        tags=['Academic Year Management'],
        summary='List academic years',
        description='Get all academic years for a specific school.',
        parameters=[
            OpenApiParameter(name='school_id', type=int, location=OpenApiParameter.PATH, description='School ID'),
            OpenApiParameter(name='academic_year_code', type=str, description='Filter by year code'),
        ],
        responses={200: AcademicYearOutputSerializer(many=True)},
        examples=[
            OpenApiExample(
                'Academic Year List Response',
                value=[{
                    'id': 1,
                    'academic_year_code': '2024-2025',
                    'school': 1,
                    'start_date': '2024-09-01',
                    'end_date': '2025-06-30'
                }],
                response_only=True
            )
        ]
    )
    def get(self, request, school_id):
        school_get(school_id=school_id, actor=request.user)
        filter_serializer = AcademicYearFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        academic_years = academic_year_list(school_id=school_id, filters=filter_serializer.validated_data)
        return Response(AcademicYearOutputSerializer(academic_years, many=True).data)


class AcademicYearCreateApi(APIView):
    """Create a new academic year for a school."""
    permission_classes = [IsAdminOrManager]

    @extend_schema(
        tags=['Academic Year Management'],
        summary='Create academic year',
        description='Create a new academic year for the specified school.',
        parameters=[OpenApiParameter(name='school_id', type=int, location=OpenApiParameter.PATH, description='School ID')],
        request=AcademicYearInputSerializer,
        examples=[
            OpenApiExample('Create Request', value={'academic_year_code': '2025-2026', 'start_date': '2025-09-01', 'end_date': '2026-06-30'}, request_only=True),
        ],
        responses={
            201: OpenApiResponse(
                response=AcademicYearOutputSerializer,
                examples=[
                    OpenApiExample(
                        'Academic Year Created',
                        value={
                            'id': 10,
                            'academic_year_code': '2025-2026',
                            'school': 1,
                            'start_date': '2025-09-01',
                            'end_date': '2026-06-30'
                        }
                    )
                ]
            ),
            400: OpenApiResponse(description='Validation error')
        }
    )
    def post(self, request, school_id):
        serializer = AcademicYearInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        academic_year = academic_year_create(
            creator=request.user, school_id=school_id,
            academic_year_code=serializer.validated_data['academic_year_code'],
            start_date=serializer.validated_data['start_date'],
            end_date=serializer.validated_data['end_date'],
        )
        return Response(AcademicYearOutputSerializer(academic_year).data, status=status.HTTP_201_CREATED)


class AcademicYearDetailApi(APIView):
    """Retrieve, update, or delete a specific academic year."""
    permission_classes = [IsAdminOrManager]

    @extend_schema(
        tags=['Academic Year Management'],
        summary='Get academic year details',
        description='Retrieve details of a specific academic year.',
        parameters=[
            OpenApiParameter(name='school_id', type=int, location=OpenApiParameter.PATH, description='School ID'),
            OpenApiParameter(name='academic_year_id', type=int, location=OpenApiParameter.PATH, description='Academic Year ID'),
        ],
        responses={
            200: OpenApiResponse(
                response=AcademicYearOutputSerializer,
                examples=[
                    OpenApiExample(
                        'Academic Year Details',
                        value={
                            'id': 1,
                            'academic_year_code': '2024-2025',
                            'school': 1,
                            'start_date': '2024-09-01',
                            'end_date': '2025-06-30'
                        }
                    )
                ]
            )
        }
    )
    def get(self, request, school_id, academic_year_id):
        academic_year = academic_year_get(academic_year_id=academic_year_id, school_id=school_id, actor=request.user)
        return Response(AcademicYearOutputSerializer(academic_year).data)

    @extend_schema(
        tags=['Academic Year Management'],
        summary='Update academic year',
        description='Update an academic year with partial data.',
        parameters=[
            OpenApiParameter(name='school_id', type=int, location=OpenApiParameter.PATH, description='School ID'),
            OpenApiParameter(name='academic_year_id', type=int, location=OpenApiParameter.PATH, description='Academic Year ID'),
        ],
        request=AcademicYearInputSerializer,
        examples=[OpenApiExample('Update Request', value={'academic_year_code': '2025-2026'}, request_only=True)],
        responses={
            200: OpenApiResponse(
                response=AcademicYearOutputSerializer,
                examples=[
                    OpenApiExample(
                        'Academic Year Updated',
                        value={
                            'id': 1,
                            'academic_year_code': '2025-2026',
                            'school': 1,
                            'start_date': '2025-09-01',
                            'end_date': '2026-06-30'
                        }
                    )
                ]
            )
        }
    )
    def patch(self, request, school_id, academic_year_id):
        academic_year = academic_year_get(academic_year_id=academic_year_id, school_id=school_id, actor=request.user)
        serializer = AcademicYearInputSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_year = academic_year_update(academic_year=academic_year, actor=request.user, data=serializer.validated_data)
        return Response(AcademicYearOutputSerializer(updated_year).data)

    @extend_schema(
        tags=['Academic Year Management'],
        summary='Delete academic year',
        description='Delete an academic year permanently.',
        parameters=[
            OpenApiParameter(name='school_id', type=int, location=OpenApiParameter.PATH, description='School ID'),
            OpenApiParameter(name='academic_year_id', type=int, location=OpenApiParameter.PATH, description='Academic Year ID'),
        ],
        responses={204: OpenApiResponse(description='Deleted successfully')}
    )
    def delete(self, request, school_id, academic_year_id):
        academic_year = academic_year_get(academic_year_id=academic_year_id, school_id=school_id, actor=request.user)
        academic_year_delete(academic_year=academic_year, actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)