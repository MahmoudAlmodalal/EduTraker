from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404
from .models import Role

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Standard serializer for viewing user details.
    """
    work_stream_id = serializers.IntegerField(source='work_stream.id', read_only=True)
    work_stream_name = serializers.CharField(source='work_stream.name', read_only=True)
    school_id = serializers.IntegerField(source='school.id', read_only=True)
    school_name = serializers.CharField(source='school.school_name', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'full_name', 'role',
            'work_stream', 'work_stream_id', 'work_stream_name',
            'school', 'school_id', 'school_name',
            'is_active', 'date_joined'
        ]
        read_only_fields = ['id', 'date_joined', 'is_active']


# ============================================
# ADMIN & MANAGER PORTAL SERIALIZERS
# Base URL: /api/portal/auth/
# ============================================

class GuestRegisterSerializer(serializers.ModelSerializer):
    """
    Registration Serializer for Admin Portal.
    URL: /api/portal/auth/register/
    Logic: Forces role to GUEST.
    """
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['email', 'full_name', 'password', 'password_confirm']

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password_confirm'):
            raise ValidationError({"password_confirm": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password')
        
        # Force role to GUEST
        validated_data['role'] = Role.GUEST
        validated_data['work_stream'] = None
        
        user = User.objects.create_user(password=password, **validated_data)
        return user


class AdminLoginSerializer(serializers.Serializer):
    """
    Login Serializer for Admin & Manager Portal.
    URL: /api/portal/auth/login/
    Logic: Only allows ADMIN or MANAGER_WORKSTREAM roles to login.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        # Authenticate user
        user = authenticate(email=email, password=password)
        
        if not user:
            raise AuthenticationFailed("Invalid email or password.")
        
        if not user.is_active:
            raise AuthenticationFailed("User account is disabled.")

        # Check role restriction - ONLY ADMIN or MANAGER_WORKSTREAM allowed
        allowed_roles = [Role.ADMIN, Role.MANAGER_WORKSTREAM]
        
        if user.role not in allowed_roles:
            raise PermissionDenied(
                "Access Denied: This portal is restricted to Administrators and Workstream Managers only."
            )

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'role': user.role,
                'is_admin': user.role == Role.ADMIN,
                'is_manager': user.role == Role.MANAGER_WORKSTREAM,
                'work_stream': {
                    'id': user.work_stream.id,
                    'name': user.work_stream.name,
                } if user.work_stream else None,
            }
        }


# ============================================
# WORKSTREAM SPECIFIC SERIALIZERS
# Base URL: /api/workstream/<int:workstream_id>/auth/
# ============================================

class StudentRegisterSerializer(serializers.ModelSerializer):
    """
    Registration Serializer for Workstream Portal.
    URL: /api/workstream/<int:workstream_id>/auth/register/
    Logic:
        1. Forces role to STUDENT.
        2. Automatically assigns work_stream from workstream_id in URL.
        3. Validates that workstream_id exists.
    """
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['email', 'full_name', 'password', 'password_confirm']

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password_confirm'):
            raise ValidationError({"password_confirm": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password')
        
        # Get workstream from context (passed by the view)
        workstream = self.context.get('workstream')
        
        if not workstream:
            raise ValidationError("Workstream is required for registration.")
        
        # Force role to STUDENT and assign workstream
        validated_data['role'] = Role.STUDENT
        validated_data['work_stream'] = workstream
        
        user = User.objects.create_user(password=password, **validated_data)
        return user


class WorkstreamLoginSerializer(serializers.Serializer):
    """
    Login Serializer for Workstream Portal.
    URL: /api/workstream/<int:workstream_id>/auth/login/
    Logic:
        1. Validates credentials (email/password).
        2. Crucial Check: User MUST belong to the workstream_id in URL.
        3. If user belongs to different/no workstream, deny login.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        # Authenticate user
        user = authenticate(email=email, password=password)
        
        if not user:
            raise AuthenticationFailed("Invalid email or password.")
        
        if not user.is_active:
            raise AuthenticationFailed("User account is disabled.")

        # Get workstream_id from context (passed by the view)
        workstream_id = self.context.get('workstream_id')
        
        if workstream_id is None:
            raise ValidationError("Workstream ID is missing from the request.")

        # CRUCIAL CHECK: User must belong to this specific workstream
        if not user.work_stream:
            raise PermissionDenied(
                "Access Denied: You are not assigned to any workstream."
            )
        
        if user.work_stream.id != workstream_id:
            raise PermissionDenied(
                "Access Denied: You do not belong to this workstream. "
                "Please use the correct workstream login URL."
            )

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'role': user.role,
                'work_stream': {
                    'id': user.work_stream.id,
                    'name': user.work_stream.name,
                },
                'school': {
                    'id': user.school.id,
                    'name': user.school.school_name,
                } if user.school else None,
            }
        }
