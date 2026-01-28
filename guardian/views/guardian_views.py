"""
Guardian management API views.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse

from accounts.permissions import IsAdminOrManagerOrSecretary, IsStaffUser, IsTeacher, IsGuardian
from accounts.pagination import PaginatedAPIMixin
from guardian.models import Guardian, GuardianStudentLink
from guardian.selectors.guardian_selectors import guardian_list, guardian_get, guardian_student_list
from guardian.services.guardian_services import (
    guardian_create,
    guardian_update,
    guardian_deactivate,
    guardian_activate,
    guardian_student_link_create,
    guardian_student_link_update,
    guardian_student_link_deactivate,
)
from student.selectors.student_selectors import student_get

from guardian.serializers import (
    GuardianFilterSerializer,
    GuardianInputSerializer,
    GuardianOutputSerializer,
    GuardianStudentLinkInputSerializer,
    GuardianStudentLinkOutputSerializer,
)


# =============================================================================
# Guardian Views
# =============================================================================

class GuardianListApi(PaginatedAPIMixin, APIView):
    """List guardians."""
    permission_classes = [IsAdminOrManagerOrSecretary]

    @extend_schema(
        tags=["Guardian Management"],
        summary="List guardians",
        parameters=[
            OpenApiParameter(name='school_id', type=int, description='Filter by school'),
            OpenApiParameter(name='search', type=str, description='Search by name or email'),
            OpenApiParameter(name='include_inactive', type=bool, description='Include deactivated records'),
            OpenApiParameter(name='page', type=int, description='Page number'),
        ],
        responses={200: GuardianOutputSerializer(many=True)},
    )
    def get(self, request):
        filter_serializer = GuardianFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)

        guardians = guardian_list(
            filters=filter_serializer.validated_data,
            user=request.user,
            include_inactive=filter_serializer.validated_data.get("include_inactive", False),
        )
        page = self.paginate_queryset(guardians)
        if page is not None:
            return self.get_paginated_response(GuardianOutputSerializer(page, many=True).data)
        return Response(GuardianOutputSerializer(guardians, many=True).data)


class GuardianCreateApi(APIView):
    """Create guardian (Admin/Manager/Secretary)."""
    permission_classes = [IsAdminOrManagerOrSecretary]

    @extend_schema(
        tags=["Guardian Management"],
        summary="Create guardian",
        request=GuardianInputSerializer,
        responses={201: GuardianOutputSerializer},
    )
    def post(self, request):
        serializer = GuardianInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        required = ["email", "full_name", "password", "school_id"]
        missing = [f for f in required if f not in data]
        if missing:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({f: "This field is required." for f in missing})

        guardian = guardian_create(
            creator=request.user,
            email=data["email"],
            full_name=data["full_name"],
            password=data["password"],
            school_id=data["school_id"],
            phone_number=data.get("phone_number"),
        )
        return Response(GuardianOutputSerializer(guardian).data, status=status.HTTP_201_CREATED)


class GuardianDetailApi(APIView):
    """Detail API."""
    permission_classes = [IsAdminOrManagerOrSecretary | IsTeacher | IsStaffUser | IsGuardian]

    @extend_schema(
        tags=["Guardian Management"],
        summary="Get guardian details",
        responses={200: GuardianOutputSerializer},
    )
    def get(self, request, guardian_id: int):
        guardian = guardian_get(guardian_id=guardian_id, actor=request.user)
        return Response(GuardianOutputSerializer(guardian).data)

    @extend_schema(
        tags=["Guardian Management"],
        summary="Update guardian",
        request=GuardianInputSerializer,
        responses={200: GuardianOutputSerializer},
    )
    def patch(self, request, guardian_id: int):
        guardian = guardian_get(guardian_id=guardian_id, actor=request.user)
        serializer = GuardianInputSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        updated = guardian_update(guardian=guardian, actor=request.user, data=serializer.validated_data)
        return Response(GuardianOutputSerializer(updated).data)


class GuardianDeactivateApi(APIView):
    """Deactivate guardian (Admin/Manager/Secretary)."""
    permission_classes = [IsAdminOrManagerOrSecretary]

    @extend_schema(
        tags=["Guardian Management"],
        summary="Deactivate guardian",
        request=None,
        responses={204: OpenApiResponse(description="Deactivated successfully")},
    )
    def post(self, request, guardian_id: int):
        guardian = guardian_get(guardian_id=guardian_id, actor=request.user)
        guardian_deactivate(guardian=guardian, actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class GuardianActivateApi(APIView):
    """Activate guardian (Admin/Managers)."""
    permission_classes = [IsAdminOrManagerOrSecretary]

    @extend_schema(
        tags=["Guardian Management"],
        summary="Activate guardian",
        request=None,
        responses={204: OpenApiResponse(description="Activated successfully")},
    )
    def post(self, request, guardian_id: int):
        guardian = guardian_get(guardian_id=guardian_id, actor=request.user, include_inactive=True)
        guardian_activate(guardian=guardian, actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class GuardianStudentLinkApi(PaginatedAPIMixin, APIView):
    """Link student to guardian."""
    permission_classes = [IsAdminOrManagerOrSecretary | IsGuardian]

    @extend_schema(
        tags=['Guardian Management'],
        summary='List linked students',
        parameters=[
            OpenApiParameter(name='page', type=int, description='Page number'),
        ],
        responses={200: GuardianStudentLinkOutputSerializer(many=True)}
    )
    def get(self, request, guardian_id: int):
        links = guardian_student_list(guardian_id=guardian_id, actor=request.user)
        page = self.paginate_queryset(links)
        if page is not None:
            return self.get_paginated_response(GuardianStudentLinkOutputSerializer(page, many=True).data)
        return Response(GuardianStudentLinkOutputSerializer(links, many=True).data)

    @extend_schema(
        tags=["Guardian Management"],
        summary="Link student to guardian",
        request=GuardianStudentLinkInputSerializer,
        responses={201: GuardianStudentLinkOutputSerializer},
    )
    def post(self, request, guardian_id: int):
        # Only staff can create links
        if request.user.role not in [Role.ADMIN, Role.MANAGER_WORKSTREAM, Role.MANAGER_SCHOOL, Role.SECRETARY]:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("You don't have permission to create guardian links.")

        guardian = guardian_get(guardian_id=guardian_id, actor=request.user)

        serializer = GuardianStudentLinkInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        student = student_get(student_id=data["student_id"], actor=request.user)

        link = guardian_student_link_create(
            actor=request.user,
            guardian=guardian,
            student=student,
            relationship_type=data["relationship_type"],
            is_primary=data.get("is_primary", False),
            can_pickup=data.get("can_pickup", True),
        )
        return Response(GuardianStudentLinkOutputSerializer(link).data, status=status.HTTP_201_CREATED)


class GuardianStudentLinkDetailApi(APIView):
    """
    Update/deactivate a specific link by link_id.
    """
    permission_classes = [IsAdminOrManagerOrSecretary]

    @extend_schema(
        tags=["Guardian Management"],
        summary="Update guardian-student link",
        request=GuardianStudentLinkInputSerializer,
        responses={200: GuardianStudentLinkOutputSerializer},
    )
    def patch(self, request, link_id: int):
        # Only staff can modify links
        if request.user.role not in [Role.ADMIN, Role.MANAGER_WORKSTREAM, Role.MANAGER_SCHOOL, Role.SECRETARY]:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("You don't have permission to update guardian links.")

        link = guardian_student_link_get(link_id=link_id, actor=request.user)

        serializer = GuardianStudentLinkInputSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        updated = guardian_student_link_update(actor=request.user, link=link, data=serializer.validated_data)
        return Response(GuardianStudentLinkOutputSerializer(updated).data)

    @extend_schema(
        tags=["Guardian Management"],
        summary="Deactivate guardian-student link",
        request=None,
        responses={204: OpenApiResponse(description="Unlinked successfully")},
    )
    def post(self, request, link_id: int):
        # Only staff can deactivate links
        if request.user.role not in [Role.ADMIN, Role.MANAGER_WORKSTREAM, Role.MANAGER_SCHOOL, Role.SECRETARY]:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("You don't have permission to deactivate guardian links.")

        link = guardian_student_link_get(link_id=link_id, actor=request.user)
        guardian_student_link_deactivate(link=link, actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
