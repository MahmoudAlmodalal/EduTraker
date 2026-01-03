from rest_framework import status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from accounts.models import CustomUser
from accounts.services.auth_services import (
    workstream_register,
    workstream_login,
)
from django.core.exceptions import ValidationError, PermissionDenied


class WorkstreamRegisterView(APIView):
    """
    Register a new user in a specific workstream.
    Creates user with STUDENT role by default.
    Public endpoint - no authentication required.
    """
    permission_classes = [AllowAny]
    
    class InputSerializer(serializers.Serializer):
        email = serializers.EmailField()
        full_name = serializers.CharField(max_length=150)
        password = serializers.CharField(write_only=True, min_length=8)
        password_confirm = serializers.CharField(write_only=True, min_length=8)
        
        def validate(self, data):
            if data['password'] != data['password_confirm']:
                raise serializers.ValidationError({
                    'password_confirm': 'Passwords do not match.'
                })
            return data
    
    class OutputSerializer(serializers.Serializer): 
        id = serializers.IntegerField()
        email = serializers.EmailField()
        full_name = serializers.CharField()
        role = serializers.CharField()
        work_stream = serializers.IntegerField()
        work_stream_name = serializers.CharField()
        is_active = serializers.BooleanField()
        date_joined = serializers.DateTimeField()
        
    
    def post(self, request, workstream_id):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            user = workstream_register(
                workstream_id=workstream_id,
                email=serializer.validated_data['email'],
                full_name=serializer.validated_data['full_name'],
                password=serializer.validated_data['password'],
            )
            
            return Response(
                {
                    'message': 'Registration successful. You can now login.',
                    'user': self.OutputSerializer(user).data,
                },
                status=status.HTTP_201_CREATED
            )
            
        except ValidationError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class WorkstreamLoginView(APIView):
    """
    Login for workstream users (Students, Teachers, Guardians, etc.).
    Validates user belongs to the specified workstream.
    Returns JWT tokens for authentication.
    Public endpoint - no authentication required.
    """
    permission_classes = [AllowAny]
    
    class InputSerializer(serializers.Serializer):
        email = serializers.EmailField()
        password = serializers.CharField(write_only=True)
    
    class OutputSerializer(serializers.Serializer):
        user = serializers.SerializerMethodField()
        tokens = serializers.DictField()
        
        def get_user(self, obj):
            user = obj['user']
            return {
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'role': user.role,
                'work_stream': user.work_stream_id,
                'work_stream_name': user.work_stream.name if user.work_stream else None,
                'school': user.school_id,
                'school_name': user.school.school_name if user.school else None,
                'is_active': user.is_active,
            }
    
    def post(self, request, workstream_id):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            result = workstream_login(
                workstream_id=workstream_id,
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password'],
            )
            
            return Response(
                self.OutputSerializer(result).data,
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