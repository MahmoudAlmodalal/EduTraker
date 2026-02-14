from rest_framework import status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from accounts.models import CustomUser
from accounts.services.auth_services import (
    portal_register,
    portal_login,
    logout_user,
    request_password_reset,
    reset_password,
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
                'user_id': user.id, # Alias for frontend
                'email': user.email,
                'full_name': user.full_name,
                'role': user.role,
                'work_stream': user.work_stream_id,
                'school': user.school_id,
                'school_id': user.school_id, # Alias for frontend
                'is_active': user.is_active,
                'timezone': user.timezone,
                'email_notifications': user.email_notifications,
                'in_app_alerts': user.in_app_alerts,
                'sms_notifications': user.sms_notifications,
                'enable_2fa': user.enable_2fa,
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
            
            # Send user_logged_in signal
            from django.contrib.auth.signals import user_logged_in
            user = result['user']
            user_logged_in.send(sender=user.__class__, request=request, user=user)
            
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


class LogoutView(APIView):
    """
    Logout user by blacklisting their refresh token.
    Requires authentication.
    """
    permission_classes = [IsAuthenticated]
    
    class LogoutInputSerializer(serializers.Serializer):
        refresh = serializers.CharField(help_text="Refresh token to invalidate")
    
    @extend_schema(
        tags=['Authentication'],
        summary='Logout user',
        description='Invalidate the refresh token to logout the user.',
        request=LogoutInputSerializer,
        examples=[
            OpenApiExample(
                'Logout Request',
                value={'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'},
                request_only=True,
            ),
        ],
        responses={
            200: OpenApiResponse(
                description='Logout successful',
                examples=[
                    OpenApiExample(
                        'Success',
                        value={'message': 'Successfully logged out.'}
                    )
                ]
            ),
            400: OpenApiResponse(description='Invalid refresh token'),
        }
    )
    def post(self, request):
        serializer = self.LogoutInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            logout_user(refresh_token=serializer.validated_data['refresh'])
            from reports.utils import log_activity
            log_activity(
                actor=request.user,
                action_type='LOGOUT',
                entity_type='User',
                entity_id=request.user.id,
                description=f"User {request.user.email} logged out.",
                request=request
            )
            return Response(
                {'message': 'Successfully logged out.'},
                status=status.HTTP_200_OK
            )
        except ValidationError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class RequestPasswordResetView(APIView):
    """
    Request a password reset link.
    Public endpoint - no authentication required.
    """
    permission_classes = [AllowAny]
    
    class RequestPasswordResetInputSerializer(serializers.Serializer):
        email = serializers.EmailField(help_text="Email address of the account")
    
    @extend_schema(
        tags=['Authentication'],
        summary='Request password reset',
        description='Request a password reset link. If the email exists, a reset link will be sent.',
        request=RequestPasswordResetInputSerializer,
        examples=[
            OpenApiExample(
                'Password Reset Request',
                value={'email': 'user@example.com'},
                request_only=True,
            ),
        ],
        responses={
            200: OpenApiResponse(
                description='Password reset requested',
                examples=[
                    OpenApiExample(
                        'Success',
                        value={
                            'message': 'If this email exists, a password reset link has been sent.',
                            'uid': 'MQ',
                            'token': 'bx1234-abcdef...'
                        }
                    )
                ]
            ),
        }
    )
    def post(self, request):
        serializer = self.RequestPasswordResetInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        result = request_password_reset(email=serializer.validated_data['email'])
        return Response(result, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    """
    Reset password using the reset token.
    Public endpoint - no authentication required.
    """
    permission_classes = [AllowAny]
    
    class ResetPasswordInputSerializer(serializers.Serializer):
        uid = serializers.CharField(help_text="User ID encoded in the reset link")
        token = serializers.CharField(help_text="Password reset token")
        new_password = serializers.CharField(
            min_length=8, 
            write_only=True, 
            help_text="New password (min 8 characters)"
        )
        confirm_password = serializers.CharField(
            min_length=8, 
            write_only=True, 
            help_text="Confirm new password"
        )
        
        def validate(self, data):
            if data['new_password'] != data['confirm_password']:
                raise serializers.ValidationError({
                    'confirm_password': 'Passwords do not match.'
                })
            return data
    
    @extend_schema(
        tags=['Authentication'],
        summary='Reset password',
        description='Reset user password using the reset token from the password reset email.',
        request=ResetPasswordInputSerializer,
        examples=[
            OpenApiExample(
                'Password Reset',
                value={
                    'uid': 'MQ',
                    'token': 'bx1234-abcdef...',
                    'new_password': 'NewSecurePass123!',
                    'confirm_password': 'NewSecurePass123!'
                },
                request_only=True,
            ),
        ],
        responses={
            200: OpenApiResponse(
                description='Password reset successful',
                examples=[
                    OpenApiExample(
                        'Success',
                        value={'message': 'Password has been reset successfully.'}
                    )
                ]
            ),
            400: OpenApiResponse(description='Invalid or expired reset token'),
        }
    )
    def post(self, request):
        serializer = self.ResetPasswordInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            reset_password(
                uid=serializer.validated_data['uid'],
                token=serializer.validated_data['token'],
                new_password=serializer.validated_data['new_password'],
            )
            return Response(
                {'message': 'Password has been reset successfully.'},
                status=status.HTTP_200_OK
            )
        except ValidationError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
