from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import CustomUser
from .serializers import (
    GuestRegistrationSerializer, 
    WorkstreamStudentSerializer,
    ManagementTokenObtainPairSerializer,
    WorkstreamTokenObtainPairSerializer
)

class GuestRegistrationView(generics.CreateAPIView):
    """
    Registration Endpoint for Admin/Guest users.
    URL: /api/accounts/register/admin/
    Role: Assigned 'guest' automatically.
    """
    queryset = CustomUser.objects.all()
    serializer_class = GuestRegistrationSerializer
    permission_classes = [permissions.AllowAny]


class WorkstreamStudentRegistrationView(generics.CreateAPIView):
    """
    Registration Endpoint for Workstream Students.
    URL: /api/accounts/register/<str:workstream_name>/
    Role: Assigned 'student' and linked to the specific Workstream.
    """
    queryset = CustomUser.objects.all()
    serializer_class = WorkstreamStudentSerializer
    permission_classes = [permissions.AllowAny]

    def get_serializer_context(self):
        """
        Pass the 'workstream_name' from the URL to the serializer
        so it can validate the workstream exists and link the user.
        """
        context = super().get_serializer_context()
        context['workstream_name'] = self.kwargs.get('workstream_name')
        return context


class ManagementLoginView(TokenObtainPairView):
    """
    Login View for Super Admins and Workstream Managers.
    URL: /api/accounts/login/admin/
    """
    serializer_class = ManagementTokenObtainPairSerializer


class WorkstreamLoginView(TokenObtainPairView):
    """
    Login View for Workstream Users (Teachers, Students).
    URL: /api/accounts/login/<str:workstream_name>/
    """
    serializer_class = WorkstreamTokenObtainPairSerializer

    def get_serializer_context(self):
        """
        Pass the 'workstream_name' from the URL to the serializer
        for validation (User must belong to this specific workstream).
        """
        context = super().get_serializer_context()
        context['workstream_name'] = self.kwargs.get('workstream_name')
        return context