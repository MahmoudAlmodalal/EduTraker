from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404
from .models import Role
from manager.models import WorkStream

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """
    Standard serializer for viewing user details.
    """
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'role', 'school', 'work_stream', 'is_active', 'date_joined']
        read_only_fields = ['id', 'date_joined', 'is_active']


class GuestRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Admin Registration URL (/register/admin/).
    Registers a user with the 'guest' role by default.
    """
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'full_name', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        
        # Force role to GUEST
        validated_data['role'] = Role.GUEST
        validated_data['work_stream'] = None
        
        user = User.objects.create_user(password=password, **validated_data)
        return user


class WorkstreamStudentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Workstream Registration URL (/register/<workstream>/).
    Registers a user as 'student' and links them to the specific Workstream.
    """
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'full_name', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        
        # 1. Get workstream name from the View context
        ws_name = self.context.get('workstream_name')
        
        if not ws_name:
            raise ValidationError("Workstream name is missing from the registration context.")

        # 2. Find the workstream (case-insensitive)
        # Using filter().first() avoids crashing if not found, allowing a clean error
        workstream_obj = WorkStream.objects.filter(name__iexact=ws_name).first()
        
        if not workstream_obj:
            raise ValidationError(f"The workstream '{ws_name}' does not exist.")
        
        # 3. Force role to STUDENT and assign Workstream
        validated_data['role'] = Role.STUDENT
        validated_data['work_stream'] = workstream_obj
        
        user = User.objects.create_user(password=password, **validated_data)
        return user


class ManagementTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Login Serializer for Super Admins and Workstream Managers only.
    """
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Restrict access to specific management roles
        allowed_roles = [Role.ADMIN, Role.MANAGER_WORKSTREAM]
        
        if self.user.role not in allowed_roles:
            raise PermissionDenied("Access Denied: This login is restricted to Administrators and Managers.")
        
        # Add custom claims to the JWT response
        data['role'] = self.user.role
        data['full_name'] = self.user.full_name
        data['is_admin'] = self.user.role == Role.ADMIN
        
        return data


class WorkstreamTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Login Serializer for Workstream Users (Teachers, Students, School Managers).
    Validates that the user belongs to the specific workstream from the URL.
    """
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # 1. Retrieve the workstream name passed from the View context
        requested_workstream = self.context.get('workstream_name')
        
        # 2. Check if the user is actually assigned to any workstream
        if not self.user.work_stream:
            raise PermissionDenied("Access Denied: You are not assigned to any workstream.")

        # 3. Validation: Match User's Workstream vs. URL Workstream
        # Using .lower() for case-insensitive comparison
        if str(self.user.work_stream.name).lower() != str(requested_workstream).lower():
            raise PermissionDenied(
                f"Access Denied: You do not belong to the '{requested_workstream}' workstream."
            )

        # Add custom claims to the JWT response
        data['role'] = self.user.role
        data['full_name'] = self.user.full_name
        data['work_stream'] = self.user.work_stream.name
        data['school'] = self.user.school.school_name if self.user.school else None
        
        return data