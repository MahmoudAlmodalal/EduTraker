from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse

from accounts.permissions import IsAdminOrManagerWorkstream
from accounts.pagination import PaginatedAPIMixin
from school.selectors.school_selectors import school_list, school_get
from school.services.school_services import (
    UNSET,
    create_school,
    update_school,
    deactivate_school,
    activate_school,
)
from workstream.models import WorkStream
from accounts.models import Role

from school.serializers.school_serializers import (
    SchoolOutputSerializer,
    SchoolListQuerySerializer,
    SchoolCreateInputSerializer,
    SchoolUpdateInputSerializer,
)


class SchoolListAPIView(PaginatedAPIMixin, APIView):
    """List all schools accessible to the current user."""
    permission_classes = [IsAdminOrManagerWorkstream]

    @extend_schema(
        tags=['School Management'],
        summary='List schools',
        description='Get all schools accessible to the current user based on their role and permissions.',
        parameters=[
            OpenApiParameter(
                name='work_stream_id',
                type=int,
                description='Filter by workstream ID'
            ),
            OpenApiParameter(
                name='page',
                type=int,
                description='Page number'
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=SchoolOutputSerializer(many=True),
                examples=[
                    OpenApiExample(
                        'School List Response',
                        value=[{
                            'id': 1,
                            'school_name': 'Global Academy',
                            'work_stream': 1,
                            'work_stream_code': 'WS-001',
                            'manager': 5,
                            'manager_name': 'John Manager',
                            'is_active': True,
                            'created_at': '2026-01-01T00:00:00Z',
                            'updated_at': '2026-01-15T10:30:00Z'
                        }]
                    )
                ]
            )
        }
    )
    def get(self, request):
        query_ser = SchoolListQuerySerializer(data=request.query_params)
        query_ser.is_valid(raise_exception=True)

        schools = school_list(
            actor=request.user,
            work_stream_id=query_ser.validated_data.get("work_stream_id"),
            include_inactive=query_ser.validated_data.get("include_inactive", False)
        )

        page = self.paginate_queryset(schools)
        if page is not None:
            return self.get_paginated_response(SchoolOutputSerializer(page, many=True).data)

        return Response(SchoolOutputSerializer(schools, many=True).data, status=status.HTTP_200_OK)


class SchoolCreateAPIView(APIView):
    """Create a new school."""
    permission_classes = [IsAdminOrManagerWorkstream]

    @extend_schema(
        tags=['School Management'],
        summary='Create school',
        description='Create a new school within a specified workstream.',
        request=SchoolCreateInputSerializer,
        examples=[
            OpenApiExample(
                'Create School Request',
                value={
                    'school_name': 'New Academy',
                    'work_stream': 1
                },
                request_only=True
            )
        ],
        responses={
            201: OpenApiResponse(
                description='School created successfully',
                examples=[
                    OpenApiExample(
                        'School Created',
                        value={'id': 10}
                    )
                ]
            ),
            400: OpenApiResponse(description='Validation error'),
            403: OpenApiResponse(description='Permission denied')
        }
    )
    def post(self, request):
        in_ser = SchoolCreateInputSerializer(data=request.data)
        in_ser.is_valid(raise_exception=True)

        # Prefer explicit work_stream from payload; otherwise fall back to the
        # authenticated user's work_stream (typical for manager_workstream role).
        workstream = in_ser.validated_data.get("work_stream") or getattr(request.user, "work_stream", None)

        if workstream is None:
            return Response(
                {"work_stream": ["This field is required for this operation."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        school = create_school(
            actor=request.user,
            school_name=in_ser.validated_data["school_name"],
            work_stream=workstream,
            manager=None,
            location=in_ser.validated_data.get("location"),
            capacity=in_ser.validated_data.get("capacity"),
        )

        return Response({"id": school.id}, status=status.HTTP_201_CREATED)


class SchoolUpdateAPIView(APIView):
    """Update an existing school."""
    permission_classes = [IsAdminOrManagerWorkstream]

    @extend_schema(
        tags=['School Management'],
        summary='Update school',
        description='Update an existing school\'s details. Supports partial updates via PATCH.',
        parameters=[
            OpenApiParameter(
                name='school_id',
                type=int,
                location=OpenApiParameter.PATH,
                description='School ID'
            ),
        ],
        request=SchoolUpdateInputSerializer,
        examples=[
            OpenApiExample(
                'Update School Request',
                value={'school_name': 'Updated Academy Name'},
                request_only=True
            )
        ],
        responses={
            204: OpenApiResponse(description='School updated successfully'),
            400: OpenApiResponse(description='Validation error'),
            403: OpenApiResponse(description='Permission denied'),
            404: OpenApiResponse(description='School not found')
        }
    )
    def put(self, request, school_id: int):
        return self.update(request, school_id)

    @extend_schema(
        tags=['School Management'],
        summary='Partial update school',
        description='Partially update an existing school\'s details.',
        parameters=[
            OpenApiParameter(
                name='school_id',
                type=int,
                location=OpenApiParameter.PATH,
                description='School ID'
            ),
        ],
        request=SchoolUpdateInputSerializer,
        responses={
            204: OpenApiResponse(description='School updated successfully'),
            400: OpenApiResponse(description='Validation error'),
            403: OpenApiResponse(description='Permission denied'),
            404: OpenApiResponse(description='School not found')
        }
    )
    def patch(self, request, school_id: int):
        return self.update(request, school_id)

    def update(self, request, school_id: int):
        school = school_get(actor=request.user, school_id=school_id)

        in_ser = SchoolUpdateInputSerializer(data=request.data, partial=True)
        in_ser.is_valid(raise_exception=True)

        update_school(
            actor=request.user,
            school=school,
            school_name=in_ser.validated_data.get("school_name", UNSET),
            location=in_ser.validated_data.get("location", UNSET),
            capacity=in_ser.validated_data.get("capacity", UNSET),
        )

        return Response(status=status.HTTP_204_NO_CONTENT)


class SchoolDeactivateAPIView(APIView):
    """Deactivate a school."""
    permission_classes = [IsAdminOrManagerWorkstream]

    @extend_schema(
        tags=['School Management'],
        summary='Deactivate school',
        description='Deactivate a school (soft delete). This will mark the school as inactive.',
        parameters=[
            OpenApiParameter(
                name='school_id',
                type=int,
                location=OpenApiParameter.PATH,
                description='School ID'
            ),
        ],
        request=None,
        responses={
            204: OpenApiResponse(description='School deactivated successfully'),
            403: OpenApiResponse(description='Permission denied'),
            404: OpenApiResponse(description='School not found')
        }
    )
    def post(self, request, school_id: int):
        school = school_get(actor=request.user, school_id=school_id)
        deactivate_school(actor=request.user, school=school)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SchoolActivateAPIView(APIView):
    """Activate a school."""
    permission_classes = [IsAdminOrManagerWorkstream]

    @extend_schema(
        tags=['School Management'],
        summary='Activate school',
        description='Activate a previously deactivated school.',
        parameters=[
            OpenApiParameter(
                name='school_id',
                type=int,
                location=OpenApiParameter.PATH,
                description='School ID'
            ),
        ],
        request=None,
        responses={
            204: OpenApiResponse(description='School activated successfully'),
            403: OpenApiResponse(description='Permission denied'),
            404: OpenApiResponse(description='School not found')
        }
    )
    def post(self, request, school_id: int):
        school = school_get(actor=request.user, school_id=school_id, include_inactive=True)
        activate_school(actor=request.user, school=school)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SchoolBulkActivateAPIView(APIView):
    """Activate all inactive schools accessible to the current user (within their scope)."""
    permission_classes = [IsAdminOrManagerWorkstream]

    @extend_schema(
        tags=['School Management'],
        summary='Bulk activate schools',
        description='Activate all inactive schools in the current admin/workstream manager scope.',
        request=None,
        responses={
            200: OpenApiResponse(
                description='Bulk activation completed',
                examples=[
                    OpenApiExample(
                        'Bulk Activation Result',
                        value={
                            'activated': 3,
                            'errors': [
                                {'id': 5, 'error': 'Workstream \"WS-1\" has reached its maximum capacity of 5 active schools.'}
                            ]
                        }
                    )
                ]
            ),
            403: OpenApiResponse(description='Permission denied'),
        }
    )
    def post(self, request):
        from school.models import School

        actor = request.user
        activated_count = 0
        errors = []

        # Start with all inactive schools visible to this actor
        qs = School.all_objects.filter(is_active=False)

        if actor.role == Role.MANAGER_WORKSTREAM:
            qs = qs.filter(work_stream_id=actor.work_stream_id)

        # Optional explicit work_stream filter (for admins)
        work_stream_id = request.data.get('work_stream_id') or request.query_params.get('work_stream_id')
        if work_stream_id:
            qs = qs.filter(work_stream_id=work_stream_id)

        for school in qs:
            try:
                activate_school(actor=actor, school=school)
                activated_count += 1
            except Exception as e:
                errors.append({'id': school.id, 'error': str(e)})

        return Response(
            {'activated': activated_count, 'errors': errors},
            status=status.HTTP_200_OK
        )
