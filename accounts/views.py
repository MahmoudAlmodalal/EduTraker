from django.contrib.auth import get_user_model
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    CustomTokenObtainPairSerializer,
    UserCreateSerializer,
    UserSerializer,
    UserUpdateSerializer,
)

User = get_user_model()


class IsAdmin(permissions.BasePermission):
    """Permission check for Admin role."""
    
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "admin"
        )


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom JWT login view."""
    serializer_class = CustomTokenObtainPairSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    User management endpoints (Admin only).
    FR-UM-001: Create, modify, and deactivate user accounts.
    """
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    
    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return UserUpdateSerializer
        return UserSerializer
    
    def get_queryset(self):
        """Filter users based on role if needed."""
        queryset = super().get_queryset()
        role = self.request.query_params.get("role", None)
        if role:
            queryset = queryset.filter(role=role)
        return queryset.order_by("-date_joined")
    
    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        """Deactivate a user account (FR-UM-003)."""
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response(
            {"message": f"User {user.email} has been deactivated."},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        """Activate a user account."""
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response(
            {"message": f"User {user.email} has been activated."},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=["get"])
    def me(self, request):
        """Get current user's profile."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)