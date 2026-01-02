from rest_framework import status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.exceptions import PermissionDenied, ValidationError

from workstream.models import WorkStream
from workstream.selectors.workstream_selectors import workstream_list, workstream_get
from workstream.services.workstream_services import (
    workstream_create,
    workstream_update,
    workstream_delete,
    workstream_deactivate,
)
from accounts.permissions import IsSuperAdmin, IsAdminOrManager


class WorkstreamListView(APIView):
    """
    GET: List all workstreams (with role-based filtering)
    """
    permission_classes = [IsAdminOrManager]

    class FilterSerializer(serializers.Serializer):
        search = serializers.CharField(required=False)
        is_active = serializers.BooleanField(required=False)

    class OutputSerializer(serializers.ModelSerializer):
        total_users = serializers.IntegerField(
            source='users.count',
            read_only=True
        )
        
        class Meta:
            model = WorkStream
            fields = [
                'id',
                'name',
                'description',
                'capacity',
                'is_active',
                'total_users',
                'created_at',
                'updated_at',
            ]

    def get(self, request):
        filter_serializer = self.FilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        
        workstreams = workstream_list(
            filters=filter_serializer.validated_data,
            user=request.user
        )
        
        data = self.OutputSerializer(workstreams, many=True).data
        return Response(data)


class WorkstreamCreateView(APIView):
    """
    POST: Create a new workstream (Admin only)
    """
    permission_classes = [IsSuperAdmin]

    class InputSerializer(serializers.Serializer):
        name = serializers.CharField(max_length=200)
        description = serializers.CharField(required=False, allow_blank=True)
        capacity = serializers.IntegerField(default=0, min_value=0)

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            workstream = workstream_create(
                creator=request.user,
                **serializer.validated_data
            )
            
            return Response(
                WorkstreamListApi.OutputSerializer(workstream).data,
                status=status.HTTP_201_CREATED
            )
        
        except ValidationError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except PermissionDenied as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_403_FORBIDDEN
            )



class WorkstreamDetailView(APIView):
    """
    GET: Get workstream details
    """
    permission_classes = [IsAdminOrManager]

    def get(self, request, workstream_id):
        try:
            workstream = workstream_get(
                workstream_id=workstream_id,
                actor=request.user
            )
            return Response(
                WorkstreamListApi.OutputSerializer(workstream).data
            )
        
        except PermissionDenied as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_403_FORBIDDEN
            )


class WorkstreamUpdateView(APIView):
    """
    PATCH: Update workstream
    """
    permission_classes = [IsAdminOrManager]

    class InputSerializer(serializers.Serializer):
        name = serializers.CharField(max_length=200, required=False)
        description = serializers.CharField(required=False, allow_blank=True)
        capacity = serializers.IntegerField(required=False, min_value=0)
        is_active = serializers.BooleanField(required=False)

    def patch(self, request, workstream_id):
        try:
            workstream = workstream_get(
                workstream_id=workstream_id,
                actor=request.user
            )
            
            serializer = self.InputSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            updated_workstream = workstream_update(
                workstream=workstream,
                actor=request.user,
                data=serializer.validated_data
            )
            
            return Response(
                WorkstreamListApi.OutputSerializer(updated_workstream).data
            )
        
        except ValidationError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except PermissionDenied as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
            
class WorkstreamDeactivateView(APIView):
    """
    POST: Deactivate workstream (soft delete)
    """
    permission_classes = [IsSuperAdmin]

    def post(self, request, workstream_id):
        try:
            workstream = workstream_get(
                workstream_id=workstream_id,
                actor=request.user
            )
            
            deactivated_workstream = workstream_deactivate(
                workstream=workstream,
                actor=request.user
            )
            
            return Response(
                {
                    'detail': 'Workstream deactivated successfully.',
                    'workstream': WorkstreamListApi.OutputSerializer(
                        deactivated_workstream
                    ).data
                },
                status=status.HTTP_200_OK
            )
        
        except ValidationError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except PermissionDenied as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_403_FORBIDDEN
            )