from rest_framework import status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from accounts.models import CustomUser
from accounts.services.auth_services import (
    portal_register,
    portal_login,
)
from django.core.exceptions import ValidationError, PermissionDenied


class PortalRegisterView(APIView):
    """
    Register a new user in the portal.
    Creates user with GUEST role by default.
    Public endpoint - no authentication required.
    """
    permission_classes = [AllowAny]
    
    class PortalRegisterInputSerializer(serializers.Serializer):
        email = serializers.EmailField(help_text="User's email address")
        full_name = serializers.CharField(max_length=150, help_text="User's full name")
        password = serializers.CharField(write_only=True, min_length=8, help_text="Password (min 8 characters)")
        password_confirm = serializers.CharField(write_only=True, min_length=8, help_text="Confirm password")
        
        def validate(self, data):
            if data['password'] != data['password_confirm']:
                raise serializers.ValidationError({
                    'password_confirm': 'Passwords do not match.'
                })
            return data
    
    class PortalRegisterOutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        email = serializers.EmailField()
        full_name = serializers.CharField()
        role = serializers.CharField()
        is_active = serializers.BooleanField()
        date_joined = serializers.DateTimeField()
    
    @extend_schema(
        tags=['Portal Authentication'],
        summary='Register a new portal user',
        description='Register a new user in the portal with GUEST role. Account requires admin approval before login.',
        request=PortalRegisterInputSerializer,
        examples=[
            OpenApiExample(
                'Registration Request',
                value={
                    'email': 'newuser@example.com',
                    'full_name': 'John Doe',
                    'password': 'SecurePass123!',
                    'password_confirm': 'SecurePass123!'
                },
                request_only=True,
            ),
        ],
        responses={
            201: OpenApiResponse(
                description='Registration successful',
                examples=[
                    OpenApiExample(
                        'Success',
                        value={
                            'message': 'Registration successful. Your account is pending approval.',
                            'user': {
                                'id': 1,
                                'email': 'newuser@example.com',
                                'full_name': 'John Doe',
                                'role': 'guest',
                                'is_active': True,
                                'date_joined': '2026-01-06T12:00:00Z'
                            }
                        }
                    )
                ]
            ),
            400: OpenApiResponse(description='Validation error or email already exists'),
        }
    )
    def post(self, request):
        serializer = self.PortalRegisterInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            user = portal_register(
                email=serializer.validated_data['email'],
                full_name=serializer.validated_data['full_name'],
                password=serializer.validated_data['password'],
            )
            
            return Response(
                {
                    'message': 'Registration successful. Your account is pending approval.',
                    'user': self.PortalRegisterOutputSerializer(user).data,
                },
                status=status.HTTP_201_CREATED
            )
            
        except ValidationError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class PortalLoginView(APIView):
    """
    Login for portal users (Admin, Workstream Managers).
    Returns JWT tokens for authentication.
    Public endpoint - no authentication required.
    """
    permission_classes = [AllowAny]
    
    class PortalLoginInputSerializer(serializers.Serializer):
        email = serializers.EmailField(help_text="User's email address")
        password = serializers.CharField(write_only=True, help_text="User's password")
    
    class PortalLoginOutputSerializer(serializers.Serializer):
        user = serializers.SerializerMethodField()
        tokens = serializers.DictField(help_text="JWT access and refresh tokens")
        
        def get_user(self, obj):
            user = obj['user']
            return {
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'role': user.role,
                'work_stream': user.work_stream_id,
                'school': user.school_id,
                'is_active': user.is_active,
            }
    
    @extend_schema(
        tags=['Portal Authentication'],
        summary='Login to portal',
        description='Authenticate portal users (Admin, Workstream Managers) and receive JWT tokens.',
        request=PortalLoginInputSerializer,
        examples=[
            OpenApiExample(
                'Login Request',
                value={
                    'email': 'admin@test.com',
                    'password': 'test1234'
                },
                request_only=True,
            ),
        ],
        responses={
            200: OpenApiResponse(
                description='Login successful',
                examples=[
                    OpenApiExample(
                        'Success',
                        value={
                            'user': {
                                'id': 1,
                                'email': 'admin@example.com',
                                'full_name': 'Admin User',
                                'role': 'admin',
                                'work_stream': None,
                                'school': None,
                                'is_active': True
                            },
                            'tokens': {
                                'access': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                                'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'
                            }
                        }
                    )
                ]
            ),
            400: OpenApiResponse(description='Invalid credentials'),
            403: OpenApiResponse(description='User not authorized for portal login'),
        }
    )
    def post(self, request):
        serializer = self.PortalLoginInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            result = portal_login(
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password'],
            )
            
            return Response(
                self.PortalLoginOutputSerializer(result).data,
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