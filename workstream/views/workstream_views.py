from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse, inline_serializer
from rest_framework import serializers

from accounts.permissions import IsSuperAdmin
from accounts.models import CustomUser
from accounts.pagination import PaginatedAPIMixin

from workstream.models import WorkStream
from workstream.selectors.workstream_selectors import (
    workstream_list,
    workstream_get,
)
from workstream.services.workstream_services import (
    workstream_create,
    workstream_update,
    workstream_deactivate,
)
from workstream.serializers import (
    WorkstreamListQuerySerializer,
    WorkstreamOutputSerializer,
    WorkstreamCreateInputSerializer,
    WorkstreamUpdateInputSerializer,
)

from rest_framework.permissions import AllowAny


class WorkstreamInfoView(APIView):
    """
    Public endpoint to get basic workstream info (id and name only).
    Used on the login page to display workstream name.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Workstream"],
        summary="Get public workstream info",
        description="Public endpoint to get basic workstream info (id and name only). Used on the login page to display workstream name.",
        parameters=[
            OpenApiParameter(
                name="slug",
                type=str,
                location=OpenApiParameter.PATH,
                description="The slug of the workstream to retrieve info for.",
            ),
        ],
        responses={
            200: inline_serializer(
                name="WorkstreamInfoResponse",
                fields={
                    "id": serializers.IntegerField(),
                    "name": serializers.CharField(),
                    "slug": serializers.SlugField(),
                },
            ),
            404: OpenApiResponse(description="Workstream not found."),
        },
        examples=[
            OpenApiExample(
                "Successful Response",
                value={"id": 1, "name": "EduTrack Main Campus", "slug": "edutrack-main-campus"},
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                "Workstream Not Found",
                value={"detail": "Not found."},
                response_only=True,
                status_codes=["404"],
            ),
        ],
    )
    def get(self, request, slug: str):
        workstream = get_object_or_404(WorkStream, slug=slug, is_active=True)
        return Response(
            {"id": workstream.id, "name": workstream.workstream_name, "slug": workstream.slug},
            status=status.HTTP_200_OK,
        )


class WorkstreamListCreateAPIView(PaginatedAPIMixin, APIView):
    permission_classes = [IsSuperAdmin]

    @extend_schema(
        tags=["Workstream"],
        summary="List all workstreams",
        description="Retrieve a list of all workstreams. SuperAdmin only. Supports filtering by search term and active status.",
        parameters=[
            OpenApiParameter(
                name="search",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Search term to filter workstreams by name.",
                required=False,
            ),
            OpenApiParameter(
                name="is_active",
                type=bool,
                location=OpenApiParameter.QUERY,
                description="Filter by active status.",
                required=False,
            ),
            OpenApiParameter(
                name="page",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Page number.",
                required=False,
            ),
        ],
        responses={200: WorkstreamOutputSerializer(many=True)},
        examples=[
            OpenApiExample(
                "Successful Response",
                value=[
                    {
                        "name": "EduTrack Main Campus",
                        "description": "Main campus workstream",
                        "manager_id": 5,
                        "max_user": 100,
                        "is_active": True,
                    },
                    {
                        "name": "EduTrack Branch A",
                        "description": "Branch A workstream",
                        "manager_id": 10,
                        "max_user": 50,
                        "is_active": True,
                    },
                ],
                response_only=True,
                status_codes=["200"],
            ),
        ],
    )
    def get(self, request):
        query_ser = WorkstreamListQuerySerializer(data=request.query_params)
        query_ser.is_valid(raise_exception=True)

        workstreams = workstream_list(
            filters=query_ser.validated_data,
            user=request.user,
        )

        page = self.paginate_queryset(workstreams)
        if page is not None:
            return self.get_paginated_response(
                WorkstreamOutputSerializer(page, many=True).data
            )

        return Response(
            WorkstreamOutputSerializer(workstreams, many=True).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["Workstream"],
        summary="Create a new workstream",
        description="Create a new workstream. SuperAdmin only.",
        request=WorkstreamCreateInputSerializer,
        responses={
            201: WorkstreamOutputSerializer,
            400: OpenApiResponse(description="Validation error."),
            404: OpenApiResponse(description="Manager not found."),
        },
        examples=[
            OpenApiExample(
                "Create Workstream Request",
                value={
                    "name": "New Campus",
                    "description": "A new campus workstream",
                    "manager_id": 5,
                    "max_user": 100,
                },
                request_only=True,
            ),
            OpenApiExample(
                "Successful Response",
                value={
                    "id": 3,
                    "name": "New Campus",
                    "description": "A new campus workstream",
                    "manager_id": 5,
                    "max_user": 100,
                },
                response_only=True,
                status_codes=["201"],
            ),
            OpenApiExample(
                "Validation Error",
                value={"name": ["This field is required."]},
                response_only=True,
                status_codes=["400"],
            ),
            OpenApiExample(
                "Manager Not Found",
                value={"detail": "Not found."},
                response_only=True,
                status_codes=["404"],
            ),
        ],
    )
    def post(self, request):
        in_ser = WorkstreamCreateInputSerializer(data=request.data)
        in_ser.is_valid(raise_exception=True)

        manager = None
        manager_id = in_ser.validated_data.get("manager_id")
        if manager_id:
            manager = get_object_or_404(CustomUser, id=manager_id)

        try:
            workstream = workstream_create(
                creator=request.user,
                workstream_name=in_ser.validated_data["workstream_name"],
                description=in_ser.validated_data.get("description"),
                manager=manager,
                capacity=in_ser.validated_data.get("capacity", 100),
            )
        except ValidationError as e:
            return Response(
                {"detail": e.messages if hasattr(e, 'messages') else str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            WorkstreamOutputSerializer(workstream).data,
            status=status.HTTP_201_CREATED,
        )


class WorkstreamUpdateAPIView(APIView):
    permission_classes = [IsSuperAdmin]
    serializer_class = WorkstreamUpdateInputSerializer

    @extend_schema(
        tags=["Workstream"],
        summary="Update a workstream",
        description="Update an existing workstream by ID. SuperAdmin only. All fields are optional.",
        parameters=[
            OpenApiParameter(
                name="workstream_id",
                type=int,
                location=OpenApiParameter.PATH,
                description="The ID of the workstream to update.",
            ),
        ],
        request=WorkstreamUpdateInputSerializer,
        responses={
            200: WorkstreamOutputSerializer,
            400: OpenApiResponse(description="Validation error."),
            404: OpenApiResponse(description="Workstream not found."),
        },
        examples=[
            OpenApiExample(
                "Update Workstream Request",
                value={
                    "name": "Updated Campus Name",
                    "description": "Updated description",
                    "manager_id": 2,
                    "max_user": 150,
                    "is_active": False,
                },
                request_only=True,
            ),
            OpenApiExample(
                "Validation Error",
                value={"max_user": ["Ensure this value is greater than or equal to 1."]},
                response_only=True,
                status_codes=["400"],
            ),
            OpenApiExample(
                "Workstream Not Found",
                value={"detail": "Not found."},
                response_only=True,
                status_codes=["404"],
            ),
        ],
    )
    def put(self, request, workstream_id: int):
        workstream = workstream_get(
            actor=request.user,
            workstream_id=workstream_id,
        )

        in_ser = WorkstreamUpdateInputSerializer(data=request.data)
        in_ser.is_valid(raise_exception=True)

        data = in_ser.validated_data

        if "manager_id" in data:
            data["manager"] = get_object_or_404(
                CustomUser,
                id=data.pop("manager_id"),
            )

        try:
            workstream_update(
                actor=request.user,
                workstream=workstream,
                data=data,
            )
        except ValidationError as e:
            return Response(
                {"detail": e.messages if hasattr(e, 'messages') else str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            WorkstreamOutputSerializer(workstream).data,
            status=status.HTTP_200_OK,
        )

    def patch(self, request, workstream_id: int):
        """Handle PATCH requests by delegating to the same logic as PUT."""
        return self.put(request, workstream_id)


class WorkstreamDeactivateAPIView(APIView):
    permission_classes = [IsSuperAdmin]

    @extend_schema(
        tags=["Workstream"],
        summary="Deactivate a workstream",
        description="Deactivate an existing workstream by ID. SuperAdmin only. This does not delete the workstream, only sets it as inactive.",
        parameters=[
            OpenApiParameter(
                name="workstream_id",
                type=int,
                location=OpenApiParameter.PATH,
                description="The ID of the workstream to deactivate.",
            ),
        ],
        request=None,
        responses={
            200: inline_serializer(
                name="WorkstreamDeactivateResponse",
                fields={"message": serializers.CharField()},
            ),
            404: OpenApiResponse(description="Workstream not found."),
        },
        examples=[
            OpenApiExample(
                "Successful Response",
                value={"message": "Workstream deactivated successfully."},
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                "Workstream Not Found",
                value={"detail": "Not found."},
                response_only=True,
                status_codes=["404"],
            ),
        ],
    )
    def post(self, request, workstream_id: int):
        workstream = workstream_get(
            actor=request.user,
            workstream_id=workstream_id,
        )

        workstream_deactivate(
            actor=request.user,
            workstream=workstream,
        )

        return Response(
            {"message": "Workstream deactivated successfully."},
            status=status.HTTP_200_OK,
        )
