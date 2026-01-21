from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError

from accounts.permissions import IsSuperAdmin  # keep your style
from guardian.selectors.guardian_selectors import (
    guardian_get_by_user_id,
    guardian_list_qs,
    guardian_student_link_get,
    guardian_student_links_qs,
)
from guardian.services.guardian_services import (
    guardian_create,
    guardian_update,
    guardian_deactivate,
    guardian_reactivate,
    guardian_student_link_create,
    guardian_student_link_update,
    guardian_student_link_delete,
)
from guardian.serializers import (
    GuardianSerializer,
    GuardianCreateSerializer,
    GuardianUpdateSerializer,
    GuardianStudentLinkSerializer,
    GuardianStudentLinkCreateSerializer,
    GuardianStudentLinkUpdateSerializer,
)
from student.models import Student

User = get_user_model()


class GuardianListCreateView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        qs = guardian_list_qs()
        return Response(GuardianSerializer(qs, many=True).data)

    def post(self, request):
        serializer = GuardianCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.get(id=serializer.validated_data["user_id"])
        guardian = guardian_create(
            user=user,
            phone_number=serializer.validated_data.get("phone_number"),
        )
        return Response(GuardianSerializer(guardian).data, status=status.HTTP_201_CREATED)


class GuardianRetrieveUpdateView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request, guardian_user_id: int):
        guardian = guardian_get_by_user_id(user_id=guardian_user_id)
        return Response(GuardianSerializer(guardian).data)

    def patch(self, request, guardian_user_id: int):
        guardian = guardian_get_by_user_id(user_id=guardian_user_id)

        serializer = GuardianUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        guardian = guardian_update(
            guardian=guardian,
            phone_number=serializer.validated_data.get("phone_number"),
        )
        return Response(GuardianSerializer(guardian).data)


class GuardianDeactivateView(APIView):
    permission_classes = [IsSuperAdmin]

    def post(self, request, guardian_user_id: int):
        guardian = guardian_get_by_user_id(user_id=guardian_user_id)
        guardian = guardian_deactivate(guardian=guardian)
        return Response(GuardianSerializer(guardian).data)


class GuardianReactivateView(APIView):
    permission_classes = [IsSuperAdmin]

    def post(self, request, guardian_user_id: int):
        guardian = guardian_get_by_user_id(user_id=guardian_user_id)
        guardian = guardian_reactivate(guardian=guardian)
        return Response(GuardianSerializer(guardian).data)


class GuardianStudentLinkListCreateView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request, guardian_user_id: int):
        _ = guardian_get_by_user_id(user_id=guardian_user_id)  # ensure exists
        qs = guardian_student_links_qs(guardian_user_id=guardian_user_id)
        return Response(GuardianStudentLinkSerializer(qs, many=True).data)

    def post(self, request, guardian_user_id: int):
        guardian = guardian_get_by_user_id(user_id=guardian_user_id)

        serializer = GuardianStudentLinkCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        student = Student.objects.get(id=serializer.validated_data["student_id"])

        try:
            link = guardian_student_link_create(
                guardian=guardian,
                student=student,
                relationship_type=serializer.validated_data["relationship_type"],
            )
        except DjangoValidationError as e:
            return Response(e.message_dict, status=status.HTTP_400_BAD_REQUEST)

        return Response(GuardianStudentLinkSerializer(link).data, status=status.HTTP_201_CREATED)


class GuardianStudentLinkUpdateDeleteView(APIView):
    permission_classes = [IsSuperAdmin]

    def patch(self, request, guardian_user_id: int, student_id: int):
        link = guardian_student_link_get(guardian_user_id=guardian_user_id, student_id=student_id)

        serializer = GuardianStudentLinkUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        link = guardian_student_link_update(
            link=link,
            relationship_type=serializer.validated_data["relationship_type"],
        )
        return Response(GuardianStudentLinkSerializer(link).data)

    def delete(self, request, guardian_user_id: int, student_id: int):
        link = guardian_student_link_get(guardian_user_id=guardian_user_id, student_id=student_id)
        guardian_student_link_delete(link=link)
        return Response(status=status.HTTP_204_NO_CONTENT)
