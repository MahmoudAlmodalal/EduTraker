from rest_framework import status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse
from accounts.models import CustomUser
from accounts.services.auth_services import (
    workstream_register_user,
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
    
    class WorkstreamRegisterInputSerializer(serializers.Serializer):
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
    
    class WorkstreamRegisterOutputSerializer(serializers.Serializer): 
        id = serializers.IntegerField()
        email = serializers.EmailField()
        full_name = serializers.CharField()
        role = serializers.CharField()
        work_stream = serializers.IntegerField(source='work_stream.id')
        work_stream_name = serializers.CharField()
        is_active = serializers.BooleanField()
        date_joined = serializers.DateTimeField()
        
    @extend_schema(
        tags=['Workstream Authentication'],
        summary='Register in a workstream',
        description='Register a new user in a specific workstream with STUDENT role by default.',
        parameters=[
            OpenApiParameter(name='workstream_id', type=int, location=OpenApiParameter.PATH, description='Workstream ID'),
        ],
        request=WorkstreamRegisterInputSerializer,
        examples=[
            OpenApiExample(
                'Register Request',
                value={
                    'email': 'student@example.com',
                    'full_name': 'John Student',
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
                            'message': 'Registration successful. You can now login.',
                            'user': {'id': 1, 'email': 'student@example.com', 'full_name': 'John Student', 'role': 'student', 'work_stream': 1, 'work_stream_name': 'Main Workstream', 'is_active': True, 'date_joined': '2026-01-06T12:00:00Z'}
                        }
                    )
                ]
            ),
            400: OpenApiResponse(description='Validation error'),
        }
    )
    def post(self, request, workstream_id):
        serializer = self.WorkstreamRegisterInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            user = workstream_register_user(
                workstream_id=workstream_id,
                email=serializer.validated_data['email'],
                full_name=serializer.validated_data['full_name'],
                password=serializer.validated_data['password'],
            )
            
            return Response(
                {
                    'message': 'Registration successful. You can now login.',
                    'user': self.WorkstreamRegisterOutputSerializer(user).data,
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
    
    class WorkstreamLoginInputSerializer(serializers.Serializer):
        email = serializers.EmailField(help_text="User's email address")
        password = serializers.CharField(write_only=True, help_text="User's password")
    
    class WorkstreamLoginOutputSerializer(serializers.Serializer):
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
                'work_stream_name': user.work_stream.name if user.work_stream else None,
                'school': user.school_id,
                'school_name': user.school.school_name if user.school else None,
                'is_active': user.is_active,
            }
    
    @extend_schema(
        tags=['Workstream Authentication'],
        summary='Login to workstream',
        description='Authenticate workstream users (Students, Teachers, Guardians, etc.) and receive JWT tokens.',
        parameters=[
            OpenApiParameter(name='workstream_id', type=int, location=OpenApiParameter.PATH, description='Workstream ID'),
        ],
        request=WorkstreamLoginInputSerializer,
        examples=[
            OpenApiExample(
                'Login Request',
                value={
                    'email': 'teacher@test.com',
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
                            'user': {'id': 1, 'email': 'teacher@test.com', 'full_name': 'Teacher Name', 'role': 'teacher', 'work_stream': 1, 'work_stream_name': 'Main Workstream', 'school': 1, 'school_name': 'Main School', 'is_active': True},
                            'tokens': {'access': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...', 'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'}
                        }
                    )
                ]
            ),
            400: OpenApiResponse(description='Invalid credentials'),
            403: OpenApiResponse(description='User not authorized for this workstream'),
        }
    )
    def post(self, request, workstream_id):
        serializer = self.WorkstreamLoginInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            result = workstream_login(
                workstream_id=workstream_id,
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password'],
            )
            
            return Response(
                self.WorkstreamLoginOutputSerializer(result).data,
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