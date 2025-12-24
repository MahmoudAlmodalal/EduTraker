from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Student, StudentEnrollment
from .serializers import StudentSerializer, StudentEnrollmentSerializer
from accounts.permissions import IsSchoolManager, IsSecretary, IsTeacher

class StudentViewSet(viewsets.ModelViewSet):
    """
    API for managing Students.
    - Secretaries/Managers: Create and Edit students.
    - Teachers: View students in their school.
    """
    serializer_class = StudentSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [IsSecretary() | IsSchoolManager()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        
        # Admin: All students
        if user.role == 'admin':
            return Student.objects.all()
            
        # School Staff: Students in their school
        if user.school:
            return Student.objects.filter(school=user.school)
            
        return Student.objects.none()

class StudentEnrollmentViewSet(viewsets.ModelViewSet):
    """
    API for enrolling students into classes.
    """
    serializer_class = StudentEnrollmentSerializer
    permission_classes = [IsSchoolManager | IsSecretary]

    def get_queryset(self):
        user = self.request.user
        if user.school:
            return StudentEnrollment.objects.filter(student__school=user.school)
        return StudentEnrollment.objects.none()