from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse

from accounts.serializers import MessageSerializer

from accounts.permissions import IsAdminOrManager
from accounts.pagination import PaginatedAPIMixin
from secretary.models import Secretary
from secretary.selectors import secretary_list, secretary_get
from secretary.services import (
    secretary_create,
    secretary_update,
    secretary_deactivate,
    secretary_activate,
)


# =============================================================================
# Secretary Serializers
# =============================================================================

class SecretaryInputSerializer(serializers.Serializer):
    """Input serializer for creating/updating secretaries."""
    email = serializers.EmailField(required=False, help_text="Email address")
    full_name = serializers.CharField(max_length=150, required=False, help_text="Full name")
    password = serializers.CharField(write_only=True, required=False, help_text="Password")
    school_id = serializers.IntegerField(required=False, help_text="School ID")
    department = serializers.CharField(max_length=100, required=False, help_text="Department")
    office_number = serializers.CharField(max_length=50, required=False, allow_blank=True, allow_null=True, help_text="Office number")
    hire_date = serializers.DateField(required=False, help_text="Hire date")


class SecretaryOutputSerializer(serializers.ModelSerializer):
    """Output serializer for secretary responses."""
    email = serializers.EmailField(source='user.email', read_only=True)
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    is_active = serializers.BooleanField(source='user.is_active', read_only=True)
    school_name = serializers.CharField(source='user.school.school_name', read_only=True)

    class Meta:
        model = Secretary
        fields = ['user_id', 'email', 'full_name', 'is_active', 'school_name', 'department', 'office_number', 'hire_date']
        read_only_fields = ['user_id']


class SecretaryFilterSerializer(serializers.Serializer):
    """Filter serializer for secretary list endpoint."""
    school_id = serializers.IntegerField(required=False, help_text="Filter by school")
    department = serializers.CharField(required=False, help_text="Filter by department")
    search = serializers.CharField(required=False, help_text="Search by name or email")
    include_inactive = serializers.BooleanField(required=False, default=False, help_text="Include inactive secretaries")
    is_active = serializers.BooleanField(required=False, allow_null=True, help_text="Filter by active status")


# =============================================================================
# Secretary Views
# =============================================================================

class SecretaryListApi(PaginatedAPIMixin, APIView):
    """List all secretaries accessible to the current user."""
    permission_classes = [IsAdminOrManager]

    @extend_schema(
        tags=['Secretary'],
        summary='List secretaries',
        description='Get all secretaries filtered by permissions.',
        parameters=[
            OpenApiParameter(name='school_id', type=int, description='Filter by school'),
            OpenApiParameter(name='department', type=str, description='Filter by department'),
            OpenApiParameter(name='search', type=str, description='Search by name or email'),
            OpenApiParameter(name='include_inactive', type=bool, description='Include inactive secretaries'),
            OpenApiParameter(name='is_active', type=bool, description='Filter by active status'),
            OpenApiParameter(name='page', type=int, description='Page number'),
        ],
        responses={200: SecretaryOutputSerializer(many=True)},
        examples=[
            OpenApiExample(
                'Secretary List Response',
                value=[{
                    'user_id': 10,
                    'email': 'jane.doe@school.com',
                    'full_name': 'Jane Doe',
                    'is_active': True,
                    'school_name': 'West Side Academy',
                    'department': 'Administration',
                    'office_number': 'A-101',
                    'hire_date': '2024-01-15'
                }],
                response_only=True
            )
        ]
    )
    def get(self, request):
        filter_serializer = SecretaryFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        secretaries = secretary_list(filters=filter_serializer.validated_data, user=request.user)
        page = self.paginate_queryset(secretaries)
        if page is not None:
            return self.get_paginated_response(SecretaryOutputSerializer(page, many=True).data)
        return Response(SecretaryOutputSerializer(secretaries, many=True).data)


class SecretaryCreateApi(APIView):
    """Create a new secretary."""
    permission_classes = [IsAdminOrManager]

    @extend_schema(
        tags=['Secretary'],
        summary='Create secretary',
        description='Create a new secretary user and profile.',
        request=SecretaryInputSerializer,
        examples=[OpenApiExample('Create Request', value={'email': 'secretary@school.com', 'full_name': 'Jane Doe', 'password': 'SecurePass123!', 'school_id': 1, 'department': 'Administration', 'hire_date': '2026-01-01'}, request_only=True)],
        responses={
            201: OpenApiResponse(
                response=SecretaryOutputSerializer,
                examples=[
                    OpenApiExample(
                        'Secretary Created',
                        value={
                            'user_id': 11,
                            'email': 'mark.smith@school.com',
                            'full_name': 'Mark Smith',
                            'is_active': True,
                            'school_name': 'West Side Academy',
                            'department': 'Records',
                            'office_number': 'B-201',
                            'hire_date': '2026-02-01'
                        }
                    )
                ]
            ),
            400: OpenApiResponse(description='Validation error')
        }
    )
    def post(self, request):
        serializer = SecretaryInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        required = ['email', 'full_name', 'password', 'school_id', 'department', 'hire_date']
        missing = [f for f in required if f not in data]
        if missing:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({f: "This field is required." for f in missing})
        secretary = secretary_create(
            creator=request.user, email=data['email'], full_name=data['full_name'], password=data['password'],
            school_id=data['school_id'], department=data['department'], hire_date=data['hire_date'], office_number=data.get('office_number'),
        )
        return Response(SecretaryOutputSerializer(secretary).data, status=status.HTTP_201_CREATED)


from accounts.permissions import IsAdminOrManager, IsAdminOrManagerOrSecretary

class SecretaryDetailApi(APIView):
    """Retrieve, update, or deactivate a specific secretary."""
    permission_classes = [IsAdminOrManagerOrSecretary]

    @extend_schema(
        tags=['Secretary'],
        summary='Get secretary details',
        description='Retrieve details of a specific secretary.',
        parameters=[OpenApiParameter(name='secretary_id', type=int, location=OpenApiParameter.PATH, description='Secretary user ID')],
        responses={
            200: OpenApiResponse(
                response=SecretaryOutputSerializer,
                examples=[
                    OpenApiExample(
                        'Secretary Details',
                        value={
                            'user_id': 10,
                            'email': 'jane.doe@school.com',
                            'full_name': 'Jane Doe',
                            'is_active': True,
                            'school_name': 'West Side Academy',
                            'department': 'Administration',
                            'office_number': 'A-101',
                            'hire_date': '2024-01-15'
                        }
                    )
                ]
            )
        }
    )
    def get(self, request, secretary_id):
        secretary = secretary_get(secretary_id=secretary_id, actor=request.user)
        return Response(SecretaryOutputSerializer(secretary).data)

    @extend_schema(
        tags=['Secretary'],
        summary='Update secretary',
        description='Update a secretary with partial data.',
        parameters=[OpenApiParameter(name='secretary_id', type=int, location=OpenApiParameter.PATH, description='Secretary user ID')],
        request=SecretaryInputSerializer,
        examples=[OpenApiExample('Update Request', value={'department': 'Records'}, request_only=True)],
        responses={
            200: OpenApiResponse(
                response=SecretaryOutputSerializer,
                examples=[
                    OpenApiExample(
                        'Secretary Updated',
                        value={
                            'user_id': 10,
                            'email': 'jane.doe@school.com',
                            'full_name': 'Jane Doe',
                            'is_active': True,
                            'school_name': 'West Side Academy',
                            'department': 'Operations',
                            'office_number': 'A-102',
                            'hire_date': '2024-01-15'
                        }
                    )
                ]
            )
        }
    )
    def patch(self, request, secretary_id):
        secretary = secretary_get(secretary_id=secretary_id, actor=request.user)
        serializer = SecretaryInputSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_secretary = secretary_update(secretary=secretary, actor=request.user, data=serializer.validated_data)
        return Response(SecretaryOutputSerializer(updated_secretary).data)

    @extend_schema(
        tags=['Secretary'],
        summary='Delete secretary',
        description='Delete is not allowed. Use deactivate endpoint instead.',
        parameters=[OpenApiParameter(name='secretary_id', type=int, location=OpenApiParameter.PATH, description='Secretary user ID')],
        responses={405: OpenApiResponse(description='Use deactivate endpoint instead')}
    )
    def delete(self, request, secretary_id):
        return Response({"detail": "Use deactivate endpoint instead of delete."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class SecretaryDeactivateApi(APIView):
    """Deactivate a secretary account."""
    permission_classes = [IsAdminOrManager]

    @extend_schema(
        tags=['Secretary'],
        summary='Deactivate secretary',
        description='Deactivate a secretary account (soft delete).',
        parameters=[OpenApiParameter(name='secretary_id', type=int, location=OpenApiParameter.PATH, description='Secretary user ID')],
        request=None,
        responses={
            200: OpenApiResponse(
                response=MessageSerializer,
                description='Secretary deactivated successfully',
                examples=[
                    OpenApiExample(
                        'Secretary Deactivated',
                        value={'detail': 'Secretary deactivated successfully.'}
                    )
                ]
            )
        }
    )
    def post(self, request, secretary_id):
       secretary = secretary_get(secretary_id=secretary_id, actor=request.user)
       secretary_deactivate(secretary=secretary, actor=request.user)
       return Response({"detail": "Secretary deactivated successfully."}, status=status.HTTP_200_OK)


class SecretaryActivateApi(APIView):
    """Activate a secretary account."""
    permission_classes = [IsAdminOrManager]

    @extend_schema(
        tags=['Secretary'],
        summary='Activate secretary',
        description='Activate a secretary account.',
        parameters=[OpenApiParameter(name='secretary_id', type=int, location=OpenApiParameter.PATH, description='Secretary user ID')],
        request=None,
        responses={
            200: OpenApiResponse(
                response=MessageSerializer,
                description='Secretary activated successfully',
                examples=[
                    OpenApiExample(
                        'Secretary Activated',
                        value={'detail': 'Secretary activated successfully.'}
                    )
                ]
            )
        }
    )
    def post(self, request, secretary_id):
       secretary = secretary_get(secretary_id=secretary_id, actor=request.user)
       secretary_activate(secretary=secretary, actor=request.user)
       return Response({"detail": "Secretary activated successfully."}, status=status.HTTP_200_OK)
