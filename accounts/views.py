from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from .models import CustomUser
from .serializers import (
    UserSerializer,
    GuestRegisterSerializer,
    AdminLoginSerializer,
    StudentRegisterSerializer,
    WorkstreamLoginSerializer
)
from workstream.models import WorkStream


# ============================================
# ADMIN & MANAGER PORTAL VIEWS
# Base URL: /api/portal/auth/
# ============================================

class PortalRegisterView(APIView):
    """
    Registration for Admin Portal.
    URL: /api/portal/auth/register/
    
    Logic: Creates a new user with role forced to GUEST.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = GuestRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'message': 'Registration successful. Account pending approval.',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class PortalLoginView(APIView):
    """
    Login for Admin & Manager Portal.
    URL: /api/portal/auth/login/
    
    Logic: Only allows users with role ADMIN or MANAGER_WORKSTREAM.
    If a student, teacher, or other role tries to login, access is denied
    even if credentials are correct.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AdminLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


# ============================================
# USER MANAGEMENT APIs
# ============================================
from .selectors import get_list_users, get_user_detail
from .services import create_user, update_user, delete_user, deactivate_user
from .serializers import (
    UserCreateInputSerializer,
    UserUpdateInputSerializer,
    UserFilterSerializer,
    UserSerializer
)
from rest_framework.permissions import IsAuthenticated

class UserListApi(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        filter_serializer = UserFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        
        users = get_list_users(
            actor=request.user,
            filters=filter_serializer.validated_data
        )
        
        data = UserSerializer(users, many=True).data
        return Response(data)


class UserCreateApi(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        input_serializer = UserCreateInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        
        user = create_user(
            actor=request.user,
            **input_serializer.validated_data
        )
        
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class UserUpdateApi(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, user_id):
        input_serializer = UserUpdateInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        
        user = update_user(
            actor=request.user,
            user_id=user_id,
            data=input_serializer.validated_data
        )
        
        return Response(UserSerializer(user).data)


class UserDeleteApi(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, user_id):
        delete_user(actor=request.user, user_id=user_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserDeactivateApi(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, user_id):
        deactivate_user(actor=request.user, user_id=user_id)
        return Response({"message": "User deactivated successfully."}, status=status.HTTP_200_OK)


# ============================================
# WORKSTREAM SPECIFIC VIEWS
# Base URL: /api/workstream/<int:workstream_id>/auth/
# ============================================

class WorkstreamRegisterView(APIView):
    """
    Registration for Workstream Portal.
    URL: /api/workstream/<int:workstream_id>/auth/register/
    
    Logic:
        1. Forces role to STUDENT.
        2. Automatically assigns work_stream from workstream_id in URL.
        3. Validates that workstream_id exists in manager.WorkStream.
    """
    permission_classes = [AllowAny]

    def post(self, request, workstream_id):
        # Validate that the workstream exists
        workstream = get_object_or_404(WorkStream, id=workstream_id)
        
        serializer = StudentRegisterSerializer(
            data=request.data,
            context={'workstream': workstream}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'message': f'Registration successful. You are now a student of {workstream.name}.',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class WorkstreamLoginView(APIView):
    """
    Login for Workstream Portal.
    URL: /api/workstream/<int:workstream_id>/auth/login/
    
    Logic:
        1. Validates credentials (email/password).
        2. CRUCIAL CHECK: The user MUST belong to the workstream_id in URL
           (i.e., user.work_stream.id == workstream_id).
        3. If user belongs to a different workstream or no workstream, 
           deny the login.
    """
    permission_classes = [AllowAny]

    def post(self, request, workstream_id):
        # Validate that the workstream exists
        workstream = get_object_or_404(WorkStream, id=workstream_id)
        
        serializer = WorkstreamLoginSerializer(
            data=request.data,
            context={
                'workstream_id': workstream_id,
                'workstream': workstream
            }
        )
        serializer.is_valid(raise_exception=True)
        
        return Response(serializer.validated_data, status=status.HTTP_200_OK)