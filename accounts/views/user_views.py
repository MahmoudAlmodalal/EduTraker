from rest_framework import status, serializers, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
import csv
from datetime import datetime
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse
from accounts.models import CustomUser, Role
from accounts.selectors.user_selectors import user_list, user_get
from accounts.services.user_services import (
    user_create,
    user_update,
    user_deactivate,
    user_activate
)
from accounts.serializers import MessageSerializer
from accounts.permissions import (IsAdminOrManager,
    IsWorkStreamManager,
    IsSchoolManager,
    IsTeacher,
    IsSecretary,
    IsStaffUser,
    IsAdminOrManagerOrSecretary,
)
from accounts.pagination import PaginatedAPIMixin
from django.core.exceptions import PermissionDenied
from reports.utils import log_activity


class UserListApi(PaginatedAPIMixin, APIView):
    """List all users accessible to current user."""
    permission_classes = [IsAdminOrManager]

    class FilterSerializer(serializers.Serializer):
        role = serializers.ChoiceField(choices=CustomUser.ROLE_CHOICES, required=False, help_text="Filter by role")
        search = serializers.CharField(required=False, help_text="Search by name or email")
        is_active = serializers.BooleanField(required=False, allow_null=True, help_text="Filter by active status")

    class UserOutputSerializer(serializers.ModelSerializer):
        work_stream_name = serializers.SerializerMethodField()
        school_name = serializers.SerializerMethodField()

        class Meta:
            model = CustomUser
            fields = [
                'id', 'email', 'full_name', 'role',
                'work_stream', 'work_stream_name',
                'school', 'school_name',
                'is_active', 'date_joined'
            ]

        def get_work_stream_name(self, obj):
            return obj.work_stream.workstream_name if obj.work_stream else None

        def get_school_name(self, obj):
            return obj.school.school_name if obj.school else None

    @extend_schema(
        tags=['User Management'],
        summary='List all users',
        description='Get a list of all users. Filtered by role permissions.',
        parameters=[
            OpenApiParameter(name='role', type=str, description='Filter by role'),
            OpenApiParameter(name='search', type=str, description='Search by name or email'),
            OpenApiParameter(name='page', type=int, description='Page number'),
        ],
        responses={
            200: UserOutputSerializer(many=True),
        },
        examples=[
            OpenApiExample(
                'User List Response',
                value=[{'id': 1, 'email': 'admin@test.com', 'full_name': 'Admin User', 'password': "12345678", 'role': 'admin', 'work_stream': None, 'work_stream_name': None, 'school': None, 'school_name': None, 'is_active': True, 'date_joined': '2026-01-01T00:00:00Z'}],
                response_only=True, status_codes=['200']
            )
        ]
    )
    def get(self, request):
        filter_serializer = self.FilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        
        users = user_list(
            user=request.user,
            filters=filter_serializer.validated_data
        )
        
        page = self.paginate_queryset(users)
        if page is not None:
            data = self.UserOutputSerializer(page, many=True).data
            return self.get_paginated_response(data)
        
        data = self.UserOutputSerializer(users, many=True).data
        return Response(data)


class UserExportApi(APIView):
    """Export filtered users to CSV."""
    permission_classes = [IsAdminOrManager]

    def get(self, request):
        filter_serializer = UserListApi.FilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        
        users = user_list(
            user=request.user,
            filters=filter_serializer.validated_data
        )

        response = HttpResponse(content_type='text/csv')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        response['Content-Disposition'] = f'attachment; filename="users_export_{timestamp}.csv"'

        writer = csv.writer(response)
        writer.writerow(['ID', 'Full Name', 'Email', 'Role', 'Status', 'Workstream', 'School', 'Date Joined'])

        for user in users:
            writer.writerow([
                user.id,
                user.full_name,
                user.email,
                user.get_role_display(),
                'Active' if user.is_active else 'Inactive',
                user.work_stream.workstream_name if user.work_stream else 'N/A',
                user.school.school_name if user.school else 'N/A',
                user.date_joined.strftime("%Y-%m-%d %H:%M:%S") if user.date_joined else 'N/A'
            ])

        return response


# Roles that have separate profile tables - these should NOT be created via this endpoint
ROLES_WITH_PROFILES = [Role.TEACHER, Role.STUDENT, Role.SECRETARY, Role.GUARDIAN]


class UserCreateApi(APIView):
    """Create a new user without a profile.
    
    For roles that have associated profiles (teacher, student, secretary, guardian),
    use the dedicated creation endpoints in their respective apps.
    """
    permission_classes = [IsAdminOrManagerOrSecretary]

    class UserCreateInputSerializer(serializers.Serializer):
        email = serializers.EmailField(help_text="User email address")
        full_name = serializers.CharField(max_length=150, help_text="Full name")
        password = serializers.CharField(write_only=True, help_text="Password")
        role = serializers.ChoiceField(choices=CustomUser.ROLE_CHOICES, help_text="User role")
        work_stream = serializers.IntegerField(
            source='work_stream_id', required=False, allow_null=True, 
            help_text="Workstream ID"
        )
        school = serializers.IntegerField(
            source='school_id', required=False, allow_null=True, 
            help_text="School ID"
        )

    @extend_schema(
        tags=['User Management'],
        summary='Create a new user',
        description='''Create a new user account.
        
**Important:** Roles with profiles (teacher, student, secretary, guardian) cannot be created 
through this endpoint. Use their dedicated endpoints instead:
- Teachers: `/api/teacher/`
- Students: `/api/student/`
- Secretaries: `/api/secretary/`
- Guardians: `/api/guardian/`

This endpoint is for creating: admin, manager_workstream, manager_school, guest roles.''',
        request=UserCreateInputSerializer,
        examples=[
            OpenApiExample(
                'Create Manager User',
                value={
                    'email': 'manager@example.com',
                    'full_name': 'Workstream Manager',
                    'password': 'SecurePass123!',
                    'role': 'manager_workstream',
                    'work_stream': 1,
                },
                request_only=True,
            ),
        ],
        responses={
            201: OpenApiResponse(
                response=UserListApi.UserOutputSerializer,
                description='User created successfully',
                examples=[
                    OpenApiExample(
                        'Created User',
                        value={
                            'id': 1,
                            'email': 'manager@example.com',
                            'full_name': 'Workstream Manager',
                            'role': 'manager_workstream',
                            'work_stream': 1,
                            'work_stream_name': 'Main Workstream',
                            'school': None,
                            'school_name': None,
                            'is_active': True,
                            'date_joined': '2026-01-17T00:00:00Z'
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                description='Validation error or role with profile',
                examples=[
                    OpenApiExample(
                        'Role With Profile Error',
                        value={
                            'role': 'Users with role "teacher" have a profile. '
                                    'Please use the dedicated /api/teacher/ endpoint instead.'
                        }
                    )
                ]
            ),
            403: OpenApiResponse(description='Not allowed to create user with this role'),
        }
    )
    def post(self, request):
        serializer = self.UserCreateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        role = data.get('role')
        
        # Block roles that have profiles
        if role in ROLES_WITH_PROFILES:
            endpoint_map = {
                Role.TEACHER: '/api/teacher/',
                Role.STUDENT: '/api/student/',
                Role.SECRETARY: '/api/secretary/',
                Role.GUARDIAN: '/api/guardian/',
            }
            endpoint = endpoint_map.get(role, 'their dedicated endpoint')
            return Response(
                {
                    'role': f'Users with role "{role}" have a profile. '
                            f'Please use the dedicated {endpoint} endpoint instead.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = user_create(
            creator=request.user,
            email=data['email'],
            full_name=data['full_name'],
            password=data['password'],
            role=role,
            work_stream_id=data.get('work_stream_id'),
            school_id=data.get('school_id'),
        )
        
        return Response(
            UserListApi.UserOutputSerializer(user).data,
            status=status.HTTP_201_CREATED
        )



class UserUpdateApi(APIView):
    """Get, update or delete a user."""
    permission_classes = [IsStaffUser]

    class UserUpdateInputSerializer(serializers.Serializer):
        email = serializers.EmailField(required=False, help_text="Email")
        full_name = serializers.CharField(max_length=150, required=False, help_text="Full name")
        role = serializers.ChoiceField(choices=CustomUser.ROLE_CHOICES, required=False, help_text="Role")
        work_stream = serializers.IntegerField(source='work_stream_id', required=False, allow_null=True, help_text="Workstream ID")
        school = serializers.IntegerField(source='school_id', required=False, allow_null=True, help_text="School ID")
        is_active = serializers.BooleanField(required=False, help_text="Active status")
        password = serializers.CharField(required=False, write_only=True, help_text="Password")

    @extend_schema(
        tags=['User Management'],
        summary='Get user details',
        description='Get details of a specific user.',
        parameters=[OpenApiParameter(name='user_id', type=int, location=OpenApiParameter.PATH, description='User ID')],
        responses={
            200: OpenApiResponse(
                response=UserListApi.UserOutputSerializer,
                examples=[
                    OpenApiExample(
                        'User Details',
                        value={'id': 1, 'email': 'user@test.com', 'full_name': 'Test User', 'role': 'teacher', 'work_stream': 1, 'work_stream_name': 'Main Workstream', 'school': 2, 'school_name': 'Main School', 'is_active': True, 'date_joined': '2026-01-01T00:00:00Z'}
                    )
                ]
            )
        }
    )
    def get(self, request, user_id):
        try:
            user = user_get(user_id=user_id, actor=request.user)
        except Exception:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(UserListApi.UserOutputSerializer(user).data)

    @extend_schema(
        tags=['User Management'],
        summary='Update a user',
        description='Update user details. Available fields depend on your role.',
        parameters=[OpenApiParameter(name='user_id', type=int, location=OpenApiParameter.PATH, description='User ID')],
        request=UserUpdateInputSerializer,
        examples=[
            OpenApiExample(
                'Update User Request',
                value={
                    'email': 'apdateuser@example.com',
                    'full_name': 'Update User',
                    'role': 'student',
                    'password': 'SecurePass123!',
                    'work_stream': 1,
                    'school': None,
                    'is_active': True,
                },
                request_only=True,
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=UserListApi.UserOutputSerializer,
                examples=[
                    OpenApiExample(
                        'Updated User',
                        value={'id': 1, 'email': 'user@test.com', 'full_name': 'Updated Name', 'role': 'teacher', 'work_stream': 1, 'work_stream_name': 'Main Workstream', 'school': 2, 'school_name': 'Main School', 'is_active': True, 'date_joined': '2026-01-01T00:00:00Z'}
                    )
                ]
            )
        }
    )
    def patch(self, request, user_id):
        user = user_get(user_id=user_id, actor=request.user)

        serializer = self.UserUpdateInputSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        if request.user.role == Role.ADMIN:
            pass

        # WORKSTREAM MANAGER
        elif request.user.role == Role.MANAGER_WORKSTREAM:
            data.pop("role", None)
            data.pop("work_stream", None)

            if "school" in data:
                if user.work_stream_id != request.user.work_stream_id:
                    raise PermissionDenied(
                        "You can only move users inside your own workstream."
                    )

        else:
            data.pop("role", None)
            data.pop("work_stream", None)
            data.pop("school", None)

        user = user_update(user=user, data=data)

        # Log activity
        log_activity(
            actor=request.user,
            action_type='UPDATE',
            entity_type='User',
            description=f"Updated user: {user.full_name}",
            entity_id=user.id,
            request=request
        )

        return Response(status=status.HTTP_204_NO_CONTENT)


class UserProfileUpdateApi(APIView):
    """Update current user's profile."""
    permission_classes = [permissions.IsAuthenticated]

    class UserProfileSettingsSerializer(serializers.ModelSerializer):
        password = serializers.CharField(
            required=False,
            write_only=True,
            min_length=8,
            help_text="New password (minimum 8 characters)",
        )

        class Meta:
            model = CustomUser
            fields = [
                "id",
                "full_name",
                "email",
                "password",
                "timezone",
                "email_notifications",
                "in_app_alerts",
                "sms_notifications",
                "enable_2fa",
            ]
            read_only_fields = ["id"]

        def validate_timezone(self, value):
            value = value.strip()
            if not value:
                raise serializers.ValidationError("Timezone cannot be empty.")
            return value

    @extend_schema(
        tags=['User Management'],
        summary='Get current profile',
        description='Get current user profile and settings preferences.',
        responses={
            200: OpenApiResponse(response=UserProfileSettingsSerializer)
        }
    )
    def get(self, request):
        serializer = self.UserProfileSettingsSerializer(request.user)
        return Response(serializer.data)

    @extend_schema(
        tags=['User Management'],
        summary='Update profile',
        description='Update current user profile and preferences. Cannot update sensitive fields like role.',
        request=UserProfileSettingsSerializer,
        responses={204: OpenApiResponse(description='Profile updated successfully')}
    )
    def patch(self, request):
        user = request.user
        blocked_fields = {
            "role",
            "work_stream",
            "work_stream_id",
            "school",
            "school_id",
            "is_active",
            "is_staff",
            "is_superuser",
            "created_by",
            "groups",
            "user_permissions",
        }

        incoming_data = request.data.copy()
        for field_name in blocked_fields:
            incoming_data.pop(field_name, None)

        serializer = self.UserProfileSettingsSerializer(instance=user, data=incoming_data, partial=True)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user_update(user=user, data=data)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserDeactivateApi(APIView):
    """Deactivate a user."""
    permission_classes = [IsAdminOrManagerOrSecretary]
    
    @extend_schema(
        tags=['User Management'],
        summary='Deactivate a user',
        description='Deactivate a user account (soft delete). You cannot deactivate yourself.',
        parameters=[OpenApiParameter(name='user_id', type=int, location=OpenApiParameter.PATH, description='User ID')],
        request=None,
        responses={
            200: OpenApiResponse(
                response=MessageSerializer,
                description='User deactivated successfully',
                examples=[OpenApiExample('Success', value={'detail': 'User deactivated successfully.'})]
            ),
            400: OpenApiResponse(response=MessageSerializer, description='Cannot deactivate yourself'),
        }
    )
    def post(self, request, user_id):
        if request.user.id == user_id:
            return Response(
                {"detail": "You cannot deactivate yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = user_get(user_id=user_id,actor=request.user)
        user_deactivate(user=user)

        # Log activity
        log_activity(
            actor=request.user,
            action_type='UPDATE',
            entity_type='User',
            description=f"Deactivated user: {user.full_name}",
            entity_id=user.id,
            request=request
        )

        return Response(status=status.HTTP_204_NO_CONTENT)

class UserActivateApi(APIView):
    """Activate a user."""
    permission_classes = [IsAdminOrManagerOrSecretary]
    
    @extend_schema(
        tags=['User Management'],
        summary='Activate a user',
        description='Activate a user account. You cannot activate yourself.',
        parameters=[OpenApiParameter(name='user_id', type=int, location=OpenApiParameter.PATH, description='User ID')],
        request=None,
        responses={
            200: OpenApiResponse(
                response=MessageSerializer,
                description='User activated successfully',
                examples=[OpenApiExample('Success', value={'detail': 'User activated successfully.'})]
            ),
            400: OpenApiResponse(response=MessageSerializer, description='Cannot activate yourself'),
        }
    )
    def post(self, request, user_id):
        if request.user.id == user_id:
            return Response(
                {"detail": "You cannot activate yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = user_get(user_id=user_id,actor=request.user)
        user_activate(user=user)

        # Log activity
        log_activity(
            actor=request.user,
            action_type='UPDATE',
            entity_type='User',
            description=f"Activated user: {user.full_name}",
            entity_id=user.id,
            request=request
        )

        return Response(status=status.HTTP_204_NO_CONTENT)
