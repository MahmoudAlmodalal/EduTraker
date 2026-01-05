from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status

from accounts.permissions import IsAdminOrManager
from secretary.models import Secretary
from secretary.selectors import secretary_list, secretary_get
from secretary.services import (
    secretary_create,
    secretary_update,
    secretary_deactivate,
)


# =============================================================================
# Secretary Serializers
# =============================================================================

class SecretaryInputSerializer(serializers.Serializer):
    """Input serializer for creating/updating secretaries."""
    email = serializers.EmailField(required=False)
    full_name = serializers.CharField(max_length=150, required=False)
    password = serializers.CharField(write_only=True, required=False)
    school_id = serializers.IntegerField(required=False)
    department = serializers.CharField(max_length=100, required=False)
    office_number = serializers.CharField(max_length=50, required=False, allow_blank=True, allow_null=True)
    hire_date = serializers.DateField(required=False)


class SecretaryOutputSerializer(serializers.ModelSerializer):
    """Output serializer for secretary responses."""
    email = serializers.EmailField(source='user.email', read_only=True)
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    is_active = serializers.BooleanField(source='user.is_active', read_only=True)
    school_name = serializers.CharField(source='user.school.school_name', read_only=True)

    class Meta:
        model = Secretary
        fields = [
            'user_id', 'email', 'full_name', 'is_active',
            'school_name', 'department', 'office_number', 'hire_date'
        ]
        read_only_fields = ['user_id']


class SecretaryFilterSerializer(serializers.Serializer):
    """Filter serializer for secretary list endpoint."""
    school_id = serializers.IntegerField(required=False)
    department = serializers.CharField(required=False)
    search = serializers.CharField(required=False)


# =============================================================================
# Secretary Views
# =============================================================================

class SecretaryListApi(APIView):
    """
    List all secretaries accessible to the current user.
    """
    permission_classes = [IsAdminOrManager]

    def get(self, request):
        """Return list of secretaries filtered by user permissions."""
        filter_serializer = SecretaryFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)

        secretaries = secretary_list(
            filters=filter_serializer.validated_data,
            user=request.user
        )

        return Response(SecretaryOutputSerializer(secretaries, many=True).data)


class SecretaryCreateApi(APIView):
    """
    Create a new secretary.
    """
    permission_classes = [IsAdminOrManager]

    def post(self, request):
        """Create a new secretary."""
        serializer = SecretaryInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        # Validate required fields
        required = ['email', 'full_name', 'password', 'school_id', 'department', 'hire_date']
        missing = [f for f in required if f not in data]
        if missing:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({f: "This field is required." for f in missing})

        secretary = secretary_create(
            creator=request.user,
            email=data['email'],
            full_name=data['full_name'],
            password=data['password'],
            school_id=data['school_id'],
            department=data['department'],
            hire_date=data['hire_date'],
            office_number=data.get('office_number'),
        )

        return Response(
            SecretaryOutputSerializer(secretary).data,
            status=status.HTTP_201_CREATED
        )


class SecretaryDetailApi(APIView):
    """
    Retrieve, update, or deactivate a specific secretary.
    """
    permission_classes = [IsAdminOrManager]

    def get(self, request, secretary_id):
        """Retrieve a single secretary by ID."""
        secretary = secretary_get(secretary_id=secretary_id, actor=request.user)
        return Response(SecretaryOutputSerializer(secretary).data)

    def patch(self, request, secretary_id):
        """Update a secretary with partial data."""
        secretary = secretary_get(secretary_id=secretary_id, actor=request.user)

        serializer = SecretaryInputSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        updated_secretary = secretary_update(
            secretary=secretary,
            actor=request.user,
            data=serializer.validated_data
        )

        return Response(SecretaryOutputSerializer(updated_secretary).data)

    def delete(self, request, secretary_id):
        """Raises error instructing to use deactivate."""
        return Response(
            {"detail": "Use deactivate endpoint instead of delete."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )


class SecretaryDeactivateApi(APIView):
    """
    Deactivate a secretary account.
    """
    permission_classes = [IsAdminOrManager]

    def post(self, request, secretary_id):
       """Deactivate a secretary."""
       secretary = secretary_get(secretary_id=secretary_id, actor=request.user)
       deactivated_secretary = secretary_deactivate(secretary=secretary, actor=request.user)
       return Response(SecretaryOutputSerializer(deactivated_secretary).data)
