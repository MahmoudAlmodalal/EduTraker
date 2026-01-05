from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
from django.core.exceptions import ValidationError, PermissionDenied
from workstream.services.workstream_services import workstream_create
from accounts.models import CustomUser
from accounts.permissions import IsSuperAdmin
from workstream.models import WorkStream
from workstream.services.workstream_services import workstream_update
from workstream.services.workstream_services import workstream_deactivate


class WorkstreamListView(APIView):
    permission_classes = [IsSuperAdmin]
    
    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = WorkStream
            fields = ['id', 'name', 'description', 'max_user', 'is_active']

    def get(self, request):
        from workstream.selectors.workstream_selectors import workstream_list
        filters = request.query_params.dict()
        workstreams = workstream_list(filters=filters, user=request.user)
        return Response(self.OutputSerializer(workstreams, many=True).data)

class WorkstreamDetailView(APIView):
    permission_classes = [IsSuperAdmin]
    
    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = WorkStream
            fields = ['id', 'name', 'description', 'max_user', 'is_active']

    def get(self, request, workstream_id):
        from workstream.selectors.workstream_selectors import workstream_get
        workstream = workstream_get(workstream_id=workstream_id, actor=request.user)
        return Response(self.OutputSerializer(workstream).data)

class WorkstreamCreateView(APIView):
    """
    Create a new WorkStream.
    Admin-only endpoint.
    """
    permission_classes = [IsSuperAdmin]
    class InputSerializer(serializers.Serializer):
        name = serializers.CharField(max_length=255)
        description = serializers.CharField(required=False, allow_blank=True)
        manager_id = serializers.IntegerField(required=True)
        max_user = serializers.IntegerField(required=True, min_value=1)

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        name = serializers.CharField()
        description = serializers.CharField()
        manager = serializers.IntegerField(source="manager.id")
        max_user = serializers.IntegerField()
        is_active = serializers.BooleanField()


    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            manager = CustomUser.objects.get(id=serializer.validated_data["manager_id"])

            workstream = workstream_create(
                creator=request.user,
                name=serializer.validated_data["name"],
                description=serializer.validated_data.get("description"),
                manager=manager,
                max_user=serializer.validated_data["max_user"],
            )

            return Response(
                self.OutputSerializer(workstream).data,
                status=status.HTTP_201_CREATED,
            )

        except CustomUser.DoesNotExist:
            return Response(
                {"detail": "Manager not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ValidationError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except PermissionDenied as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_403_FORBIDDEN,
            )

class WorkstreamUpdateView(APIView):
    permission_classes = [IsSuperAdmin]
    class InputSerializer(serializers.Serializer):
        name = serializers.CharField(required=False)
        description = serializers.CharField(required=False, allow_blank=True)
        manager_id = serializers.IntegerField(required=False)
        max_user = serializers.IntegerField(required=False, min_value=1)
        is_active = serializers.BooleanField(required=False)

    def patch(self, request, workstream_id):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            workstream = WorkStream.objects.get(id=workstream_id)

            data = serializer.validated_data

            if "manager_id" in data:
                data["manager"] = CustomUser.objects.get(id=data.pop("manager_id"))

            workstream = workstream_update(
                actor=request.user,
                workstream=workstream,
                data=data,
            )

            return Response(
                {"id": workstream.id, "name": workstream.name, "message": "Workstream updated successfully.","data": WorkstreamCreateView.OutputSerializer(workstream).data },
                status=status.HTTP_200_OK,
            )

        except WorkStream.DoesNotExist:
            return Response({"detail": "Workstream not found."}, status=404)
        except CustomUser.DoesNotExist:
            return Response({"detail": "Manager not found."}, status=400)
        except (ValidationError, PermissionDenied) as e:
            return Response({"detail": str(e)}, status=400)


class WorkstreamDeactivateView(APIView):
    permission_classes = [IsSuperAdmin]
    def post(self, request, workstream_id):
        try:
            workstream = WorkStream.objects.get(id=workstream_id)

            workstream_deactivate(
                actor=request.user,
                workstream=workstream,
            )

            return Response(
                {"detail": "Workstream deactivated successfully."},
                status=status.HTTP_200_OK,
            )

        except WorkStream.DoesNotExist:
            return Response({"detail": "Workstream not found."}, status=404)
        except PermissionDenied as e:
            return Response({"detail": str(e)}, status=403)
    

