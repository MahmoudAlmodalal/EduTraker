from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from accounts.permissions import IsWorkStreamManager
from school.selectors.academic_year_selectors import get_academic_year
from school.services.academic_year_services import (
    create_academic_year,
    update_academic_year,
    deactivate_academic_year,
)
from school.serializers.academic_year_serializers import (
    AcademicYearCreateInputSerializer,
    AcademicYearUpdateInputSerializer,
    AcademicYearOutputSerializer,
)


class AcademicYearCreateAPIView(APIView):
    permission_classes = [IsWorkStreamManager]

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


class AcademicYearUpdateAPIView(APIView):
    permission_classes = [IsWorkStreamManager]

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
    permission_classes = [IsWorkStreamManager]

    def post(self, request, academic_year_id: int):
        ay = get_academic_year(actor=request.user, academic_year_id=academic_year_id)
        deactivate_academic_year(actor=request.user, academic_year=ay)
        return Response(status=status.HTTP_204_NO_CONTENT)
