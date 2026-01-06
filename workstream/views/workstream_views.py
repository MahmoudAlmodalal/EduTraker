from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from django.core.exceptions import ValidationError, PermissionDenied
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse
from workstream.services.workstream_services import workstream_create
from accounts.models import CustomUser
from accounts.permissions import IsSuperAdmin
from workstream.models import WorkStream
from workstream.services.workstream_services import workstream_update
from workstream.services.workstream_services import workstream_deactivate


class WorkstreamInfoView(APIView):
    """
    Public endpoint to get basic workstream info for login page.
    Returns workstream name and active status.
    """
    permission_classes = [AllowAny]
    
    @extend_schema(
        tags=['Workstream - Public'],
        summary='Get workstream info',
        description='Public endpoint to get basic workstream info for the login page. No authentication required.',
        parameters=[
            OpenApiParameter(name='workstream_id', type=int, location=OpenApiParameter.PATH, description='Workstream ID'),
        ],
        responses={
            200: OpenApiResponse(
                description='Workstream found',
                examples=[OpenApiExample('Success', value={'id': 1, 'name': 'Test Workstream'})]
            ),
            404: OpenApiResponse(description='Workstream not found'),
        }
    )
    def get(self, request, workstream_id):
        try:
            workstream = WorkStream.objects.get(id=workstream_id, is_active=True)
            return Response({
                'id': workstream.id,
                'name': workstream.name,
            })
        except WorkStream.DoesNotExist:
            return Response(
                {'detail': 'Workstream not found.'},
                status=status.HTTP_404_NOT_FOUND
            )


class WorkstreamListView(APIView):
    """List all workstreams. Admin only."""
    permission_classes = [IsSuperAdmin]
    
    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = WorkStream
            fields = ['id', 'name', 'description', 'max_user', 'is_active']

    @extend_schema(
        tags=['Workstream Management'],
        summary='List all workstreams',
        description='Get a list of all workstreams. Requires Super Admin authentication.',
        responses={
            200: OutputSerializer(many=True),
        },
        examples=[
            OpenApiExample(
                'Workstream List',
                value=[{'id': 1, 'name': 'Main Workstream', 'description': 'Primary workstream', 'max_user': 100, 'is_active': True}],
                response_only=True, status_codes=['200']
            )
        ]
    )
    def get(self, request):
        from workstream.selectors.workstream_selectors import workstream_list
        filters = request.query_params.dict()
        workstreams = workstream_list(filters=filters, user=request.user)
        return Response(self.OutputSerializer(workstreams, many=True).data)


class WorkstreamDetailView(APIView):
    """Get details of a specific workstream. Admin only."""
    permission_classes = [IsSuperAdmin]
    
    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = WorkStream
            fields = ['id', 'name', 'description', 'max_user', 'is_active']

    @extend_schema(
        tags=['Workstream Management'],
        summary='Get workstream details',
        description='Get detailed information about a specific workstream. Requires Super Admin authentication.',
        parameters=[
            OpenApiParameter(name='workstream_id', type=int, location=OpenApiParameter.PATH, description='Workstream ID'),
        ],
        responses={
            200: OpenApiResponse(
                response=OutputSerializer,
                examples=[OpenApiExample('Workstream Details', value={'id': 1, 'name': 'Main Workstream', 'description': 'Primary workstream', 'max_user': 100, 'is_active': True})]
            )
        }
    )
    def get(self, request, workstream_id):
        from workstream.selectors.workstream_selectors import workstream_get
        workstream = workstream_get(workstream_id=workstream_id, actor=request.user)
        return Response(self.OutputSerializer(workstream).data)


class WorkstreamCreateView(APIView):
    """Create a new WorkStream. Admin-only endpoint."""
    permission_classes = [IsSuperAdmin]
    
    class InputSerializer(serializers.Serializer):
        name = serializers.CharField(max_length=255, help_text="Workstream name")
        description = serializers.CharField(required=False, allow_blank=True, help_text="Optional description")
        manager_id = serializers.IntegerField(required=True, help_text="User ID of the workstream manager")
        max_user = serializers.IntegerField(required=True, min_value=1, help_text="Maximum number of users allowed")

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        name = serializers.CharField()
        description = serializers.CharField()
        manager = serializers.IntegerField(source="manager.id")
        max_user = serializers.IntegerField()
        is_active = serializers.BooleanField()

    @extend_schema(
        tags=['Workstream Management'],
        summary='Create a new workstream',
        description='Create a new workstream with a designated manager. Requires Super Admin authentication.',
        request=InputSerializer,
        examples=[
            OpenApiExample(
                'Create Workstream Request',
                value={
                    'name': 'New Workstream',
                    'description': 'Description of the workstream',
                    'manager_id': 1,
                    'max_user': 100
                },
                request_only=True,
            ),
        ],
        responses={
            201: OpenApiResponse(
                response=OutputSerializer,
                examples=[OpenApiExample('Created Workstream', value={'id': 5, 'name': 'New Workstream', 'description': 'Description', 'manager': 1, 'max_user': 100, 'is_active': True})]
            ),
            400: OpenApiResponse(description='Validation error or manager not found'),
            403: OpenApiResponse(description='Permission denied'),
        }
    )
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
    """Update a workstream. Admin only."""
    permission_classes = [IsSuperAdmin]
    
    class InputSerializer(serializers.Serializer):
        name = serializers.CharField(required=False, help_text="Workstream name")
        description = serializers.CharField(required=False, allow_blank=True, help_text="Description")
        manager_id = serializers.IntegerField(required=False, help_text="Manager user ID")
        max_user = serializers.IntegerField(required=False, min_value=1, help_text="Max users")
        is_active = serializers.BooleanField(required=False, help_text="Active status")

    @extend_schema(
        tags=['Workstream Management'],
        summary='Update a workstream',
        description='Update workstream details. Requires Super Admin authentication.',
        parameters=[
            OpenApiParameter(name='workstream_id', type=int, location=OpenApiParameter.PATH, description='Workstream ID'),
        ],
        request=InputSerializer,
        examples=[
            OpenApiExample(
                'Update Workstream Request',
                value={
                    'name': 'Updated Workstream Name',
                    'description': 'Updated description',
                    'max_user': 150
                },
                request_only=True,
            ),
        ],
        responses={
            200: OpenApiResponse(
                description='Workstream updated successfully',
                examples=[OpenApiExample('Updated Workstream', value={'id': 1, 'name': 'Updated Workstream Name', 'message': 'Workstream updated successfully.', 'data': {'id': 1, 'name': 'Updated Workstream Name', 'description': 'Updated', 'manager': 1, 'max_user': 150, 'is_active': True}})]
            ),
            400: OpenApiResponse(description='Validation error'),
            404: OpenApiResponse(description='Workstream not found'),
        }
    )
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
    """Deactivate a workstream. Admin only."""
    permission_classes = [IsSuperAdmin]
    
    @extend_schema(
        tags=['Workstream Management'],
        summary='Deactivate a workstream',
        description='Deactivate a workstream (soft delete). Requires Super Admin authentication.',
        parameters=[
            OpenApiParameter(name='workstream_id', type=int, location=OpenApiParameter.PATH, description='Workstream ID'),
        ],
        responses={
            200: OpenApiResponse(
                description='Workstream deactivated successfully',
                examples=[OpenApiExample('Deactivated', value={'detail': 'Workstream deactivated successfully.'})]
            ),
            403: OpenApiResponse(description='Permission denied'),
            404: OpenApiResponse(description='Workstream not found'),
        }
    )
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
