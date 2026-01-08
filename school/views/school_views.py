from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound
from django.shortcuts import get_object_or_404

from accounts.permissions import IsAdminOrManagerWorkstream
from school.selectors.school_selectors import list_schools_for_actor, get_school
from school.services.school_services import create_school, update_school, deactivate_school
from workstream.models import WorkStream

from school.serializers.school_serializers import (
    SchoolOutputSerializer,
    SchoolListQuerySerializer,
    SchoolCreateInputSerializer,
    SchoolUpdateInputSerializer,
)


class SchoolListCreateAPIView(APIView):
    permission_classes = [IsAdminOrManagerWorkstream]

    def get(self, request):
        query_ser = SchoolListQuerySerializer(data=request.query_params)
        query_ser.is_valid(raise_exception=True)

        work_stream_id = query_ser.validated_data.get("work_stream_id")

        schools = list_schools_for_actor(
            actor=request.user,
            work_stream_id=work_stream_id,
        )

        return Response(SchoolOutputSerializer(schools, many=True).data, status=status.HTTP_200_OK)

    def post(self, request):
        in_ser = SchoolCreateInputSerializer(data=request.data)
        in_ser.is_valid(raise_exception=True)

        workstream = in_ser.validated_data["work_stream"]

        school = create_school(
            actor=request.user,
            school_name=in_ser.validated_data["school_name"],
            work_stream=workstream,
            manager=request.user,
        )

        return Response({"id": school.id}, status=status.HTTP_201_CREATED)


class SchoolUpdateAPIView(APIView):
    permission_classes = [IsAdminOrManagerWorkstream]

    def put(self, request, school_id: int):
        school = get_school(actor=request.user, school_id=school_id)

        in_ser = SchoolUpdateInputSerializer(data=request.data)
        in_ser.is_valid(raise_exception=True)

        update_school(
            actor=request.user,
            school=school,
            school_name=in_ser.validated_data.get("school_name"),
        )

        return Response(status=status.HTTP_204_NO_CONTENT)


class SchoolDeactivateAPIView(APIView):
    permission_classes = [IsAdminOrManagerWorkstream]

    def post(self, request, school_id: int):
        school = get_school(actor=request.user, school_id=school_id)
        deactivate_school(actor=request.user, school=school)
        return Response(status=status.HTTP_204_NO_CONTENT)
