from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse

from accounts.permissions import IsWorkStreamManager
from accounts.pagination import PaginatedAPIMixin
from school.selectors.academic_year_selectors import get_academic_year, list_academic_years
from school.services.academic_year_services import (
    create_academic_year,
    update_academic_year,
    deactivate_academic_year,
    activate_academic_year,
)
from school.serializers.academic_year_serializers import (
    AcademicYearCreateInputSerializer,
    AcademicYearUpdateInputSerializer,
    AcademicYearOutputSerializer,
    AcademicYearListQuerySerializer,
)


class AcademicYearListAPIView(PaginatedAPIMixin, APIView):
    """List academic years for a school."""
    permission_classes = [IsWorkStreamManager]

    @extend_schema(
        operation_id='academic_years_list',
        tags=['Academic Year Management'],
        summary='List academic years',
        description='Get all academic years for the specified school.',
        parameters=[
            OpenApiParameter(
                name='school_id',
                type=int,
                description='Filter by school ID'
            ),
            OpenApiParameter(
                name='include_inactive',
                type=bool,
                description='Include deactivated records'
            ),
            OpenApiParameter(
                name='page',
                type=int,
                description='Page number'
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=AcademicYearOutputSerializer(many=True),
                examples=[
                    OpenApiExample(
                        'Academic Year List Response',
                        value=[{
                            'id': 1,
                            'academic_year_code': '2025-2026',
                            'school': 1,
                            'school_name': 'Global Academy',
                            'start_date': '2025-09-01',
                            'end_date': '2026-06-30',
                            'is_active': True,
                            'created_at': '2025-08-01T00:00:00Z',
                            'updated_at': '2025-08-15T10:30:00Z'
                        }]
                    )
                ]
            )
        }
    )
    def get(self, request):
        query_ser = AcademicYearListQuerySerializer(data=request.query_params)
        query_ser.is_valid(raise_exception=True)

        academic_years = list_academic_years(
            actor=request.user,
            school_id=query_ser.validated_data.get("school_id"),
            include_inactive=query_ser.validated_data.get("include_inactive", False),
        )

        page = self.paginate_queryset(academic_years)
        if page is not None:
            return self.get_paginated_response(AcademicYearOutputSerializer(page, many=True).data)

        return Response(AcademicYearOutputSerializer(academic_years, many=True).data)


class AcademicYearCreateAPIView(APIView):
    """Create a new academic year."""
    permission_classes = [IsWorkStreamManager]

    @extend_schema(
        tags=['Academic Year Management'],
        summary='Create academic year',
        description='Create a new academic year for a specified school.',
        request=AcademicYearCreateInputSerializer,
        examples=[
            OpenApiExample(
                'Create Academic Year Request',
                value={
                    'school': 1,
                    'start_date': '2026-09-01',
                    'end_date': '2027-06-30'
                },
                request_only=True
            )
        ],
        responses={
            201: OpenApiResponse(
                description='Academic year created successfully',
                examples=[
                    OpenApiExample(
                        'Academic Year Created',
                        value={'id': 5}
                    )
                ]
            ),
            400: OpenApiResponse(description='Validation error'),
            403: OpenApiResponse(description='Permission denied')
        }
    )
    def post(self, request):
        in_ser = AcademicYearCreateInputSerializer(data=request.data)
        in_ser.is_valid(raise_exception=True)

        ay = create_academic_year(
            actor=request.user,
            school=in_ser.validated_data["school"],
            start_date=in_ser.validated_data["start_date"],
            end_date=in_ser.validated_data["end_date"],
        )

        return Response({"id": ay.id}, status=status.HTTP_201_CREATED)


class AcademicYearDetailAPIView(APIView):
    """Retrieve details of a specific academic year."""
    permission_classes = [IsWorkStreamManager]

    @extend_schema(
        operation_id='academic_years_detail',
        tags=['Academic Year Management'],
        summary='Get academic year details',
        description='Retrieve details of a specific academic year.',
        parameters=[
            OpenApiParameter(
                name='academic_year_id',
                type=int,
                location=OpenApiParameter.PATH,
                description='Academic Year ID'
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=AcademicYearOutputSerializer,
                examples=[
                    OpenApiExample(
                        'Academic Year Details',
                        value={
                            'id': 1,
                            'academic_year_code': '2025-2026',
                            'school': 1,
                            'school_name': 'Global Academy',
                            'start_date': '2025-09-01',
                            'end_date': '2026-06-30',
                            'is_active': True,
                            'created_at': '2025-08-01T00:00:00Z',
                            'updated_at': '2025-08-15T10:30:00Z'
                        }
                    )
                ]
            ),
            404: OpenApiResponse(description='Academic year not found')
        }
    )
    def get(self, request, academic_year_id: int):
        ay = get_academic_year(actor=request.user, academic_year_id=academic_year_id)
        return Response(AcademicYearOutputSerializer(ay).data)


class AcademicYearUpdateAPIView(APIView):
    """Update an existing academic year."""
    permission_classes = [IsWorkStreamManager]

    @extend_schema(
        tags=['Academic Year Management'],
        summary='Update academic year',
        description='Update an existing academic year\'s details.',
        parameters=[
            OpenApiParameter(
                name='academic_year_id',
                type=int,
                location=OpenApiParameter.PATH,
                description='Academic Year ID'
            ),
        ],
        request=AcademicYearUpdateInputSerializer,
        examples=[
            OpenApiExample(
                'Update Academic Year Request',
                value={
                    'start_date': '2026-09-15',
                    'end_date': '2027-07-15'
                },
                request_only=True
            )
        ],
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
                            'school_name': 'Global Academy',
                            'start_date': '2026-09-15',
                            'end_date': '2027-07-15',
                            'is_active': True,
                            'created_at': '2025-08-01T00:00:00Z',
                            'updated_at': '2026-01-17T09:00:00Z'
                        }
                    )
                ]
            ),
            400: OpenApiResponse(description='Validation error'),
            403: OpenApiResponse(description='Permission denied'),
            404: OpenApiResponse(description='Academic year not found')
        }
    )
    def put(self, request, academic_year_id: int):
        ay = get_academic_year(actor=request.user, academic_year_id=academic_year_id)

        in_ser = AcademicYearUpdateInputSerializer(data=request.data)
        in_ser.is_valid(raise_exception=True)

        ay = update_academic_year(
            actor=request.user,
            academic_year=ay,
            start_date=in_ser.validated_data.get("start_date"),
            end_date=in_ser.validated_data.get("end_date"),
        )

        return Response(AcademicYearOutputSerializer(ay).data, status=status.HTTP_200_OK)


class AcademicYearDeactivateAPIView(APIView):
    """Deactivate an academic year."""
    permission_classes = [IsWorkStreamManager]

    @extend_schema(
        tags=['Academic Year Management'],
        summary='Deactivate academic year',
        description='Deactivate an academic year (soft delete). This will mark the academic year as inactive.',
        parameters=[
            OpenApiParameter(
                name='academic_year_id',
                type=int,
                location=OpenApiParameter.PATH,
                description='Academic Year ID'
            ),
        ],
        request=None,
        responses={
            204: OpenApiResponse(description='Academic year deactivated successfully'),
            403: OpenApiResponse(description='Permission denied'),
            404: OpenApiResponse(description='Academic year not found')
        }
    )
    def post(self, request, academic_year_id: int):
        ay = get_academic_year(actor=request.user, academic_year_id=academic_year_id)
        deactivate_academic_year(actor=request.user, academic_year=ay)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AcademicYearActivateAPIView(APIView):
    """Activate an academic year."""
    permission_classes = [IsWorkStreamManager]

    @extend_schema(
        tags=['Academic Year Management'],
        summary='Activate academic year',
        description='Activate a previously deactivated academic year.',
        parameters=[
            OpenApiParameter(
                name='academic_year_id',
                type=int,
                location=OpenApiParameter.PATH,
                description='Academic Year ID'
            ),
        ],
        request=None,
        responses={
            204: OpenApiResponse(description='Academic year activated successfully'),
            403: OpenApiResponse(description='Permission denied'),
            404: OpenApiResponse(description='Academic year not found')
        }
    )
    def post(self, request, academic_year_id: int):
        ay = get_academic_year(actor=request.user, academic_year_id=academic_year_id, include_inactive=True)
        activate_academic_year(actor=request.user, academic_year=ay)
        return Response(status=status.HTTP_204_NO_CONTENT)
