from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from accounts.permissions import IsSuperAdmin
from accounts.models import CustomUser

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
class WorkstreamListCreateAPIView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        query_ser = WorkstreamListQuerySerializer(data=request.query_params)
        query_ser.is_valid(raise_exception=True)

        workstreams = workstream_list(
            filters=query_ser.validated_data,
            user=request.user,
        )

        return Response(
            WorkstreamOutputSerializer(workstreams, many=True).data,
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        in_ser = WorkstreamCreateInputSerializer(data=request.data)
        in_ser.is_valid(raise_exception=True)

        manager = get_object_or_404(
            CustomUser,
            id=in_ser.validated_data["manager_id"],
        )

        workstream = workstream_create(
            creator=request.user,
            name=in_ser.validated_data["name"],
            description=in_ser.validated_data.get("description"),
            manager=manager,
            max_user=in_ser.validated_data["max_user"],
        )

        return Response(
            {"id": workstream.id},
            status=status.HTTP_201_CREATED,
        )
class WorkstreamUpdateAPIView(APIView):
    permission_classes = [IsSuperAdmin]

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

        workstream_update(
            actor=request.user,
            workstream=workstream,
            data=data,
        )

        return Response(status=status.HTTP_204_NO_CONTENT)
class WorkstreamDeactivateAPIView(APIView):
    permission_classes = [IsSuperAdmin]

    def post(self, request, workstream_id: int):
        workstream = workstream_get(
            actor=request.user,
            workstream_id=workstream_id,
        )

        workstream_deactivate(
            actor=request.user,
            workstream=workstream,
        )

        return Response(status=status.HTTP_204_NO_CONTENT)
