from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import WorkStream, School, Grade, AcademicYear, SystemConfiguration
from .serializers import (
    WorkStreamSerializer, SchoolSerializer, GradeSerializer, 
    AcademicYearSerializer, CreateStaffAccountSerializer
)
from accounts.permissions import IsSuperAdmin, IsWorkStreamManager, IsSchoolManager

class WorkStreamViewSet(viewsets.ModelViewSet):
    """
    API for managing Workstreams.
    - Super Admin: Can create/edit/delete Workstreams.
    - Workstream Manager: Can view ONLY their own Workstream.
    """
    serializer_class = WorkStreamSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return WorkStream.objects.all()
        if user.role == 'manager_workstream':
            return WorkStream.objects.filter(manager=user)
        return WorkStream.objects.none()
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [IsSuperAdmin()]
        return [permissions.IsAuthenticated()]

class SchoolViewSet(viewsets.ModelViewSet):
    """
    API for managing Schools.
    - Workstream Managers can create schools within their stream.
    """
    serializer_class = SchoolSerializer
    permission_classes = [IsWorkStreamManager]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return School.objects.all()
        # Filter schools belonging to the workstream managed by this user
        if user.role == 'manager_workstream':
            return School.objects.filter(work_stream__manager=user)
        return School.objects.none()

    def perform_create(self, serializer):
        # Automatically link the school to the manager's workstream (if applicable)
        # This logic assumes the manager creating the school owns the workstream
        serializer.save()

class StaffCreationViewSet(viewsets.ViewSet):
    """
    Endpoint for Managers to create Staff (Teachers, Secretaries).
    """
    permission_classes = [IsSchoolManager] 

    def create(self, request):
        serializer = CreateStaffAccountSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {"message": "Staff account created successfully", "email": user.email}, 
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)