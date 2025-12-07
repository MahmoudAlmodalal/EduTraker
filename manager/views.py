from django.contrib.auth import get_user_model
from rest_framework import permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Workstream, StaffEvaluation, DepartmentActivityReport
from .serializers import (
    WorkstreamSerializer,
    StaffEvaluationSerializer,
    DepartmentActivityReportSerializer,
    CreateStaffAccountSerializer,
)

User = get_user_model()


class IsManager(permissions.BasePermission):
    """
    Simple role-based check. Assumes User has a 'role' field == 'manager'.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "role", None) == "manager"
        )


class WorkstreamViewSet(viewsets.ModelViewSet):
    """
    Workstream management (Admin/Manager).
    """
    queryset = Workstream.objects.all()
    serializer_class = WorkstreamSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class StaffEvaluationViewSet(viewsets.ModelViewSet):
    """
    Staff evaluations (US-Manager-003).
    """
    queryset = StaffEvaluation.objects.all()
    serializer_class = StaffEvaluationSerializer
    permission_classes = [permissions.IsAuthenticated, IsManager]

    def perform_create(self, serializer):
        serializer.save(manager=self.request.user)

    def get_queryset(self):
        qs = super().get_queryset()
        if getattr(self.request.user, "role", None) == "manager":
            return qs.filter(manager=self.request.user)
        return qs.none()


class DepartmentActivityReportViewSet(viewsets.ModelViewSet):
    """
    Monitoring academic performance & department activity (US-Manager-001/002).
    """
    queryset = DepartmentActivityReport.objects.all()
    serializer_class = DepartmentActivityReportSerializer
    permission_classes = [permissions.IsAuthenticated, IsManager]

    def perform_create(self, serializer):
        serializer.save(manager=self.request.user)

    def get_queryset(self):
        qs = super().get_queryset()
        if getattr(self.request.user, "role", None) == "manager":
            return qs.filter(manager=self.request.user)
        return qs.none()


class CreateStaffAccountView(APIView):
    """
    Manager creates secretary / teacher accounts (US-Manager-004).

    POST:
    {
      "first_name": "...",
      "last_name": "...",
      "email": "...",
      "password": "...",
      "role": "teacher" | "secretary"
    }
    """
    permission_classes = [permissions.IsAuthenticated, IsManager]

    def post(self, request, *args, **kwargs):
        serializer = CreateStaffAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(CreateStaffAccountSerializer(user).data, status=201)