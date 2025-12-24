from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import (
    Teacher, Course, ClassRoom, CourseAllocation, 
    Assignment, Mark, Attendance, LearningMaterial
)
from .serializers import (
    TeacherSerializer, CourseSerializer, ClassRoomSerializer, 
    CourseAllocationSerializer, AssignmentSerializer, MarkSerializer, 
    AttendanceSerializer, LearningMaterialSerializer
)
from accounts.permissions import IsSchoolManager, IsTeacher, IsStudent, IsWorkStreamManager

class TeacherViewSet(viewsets.ModelViewSet):
    """
    Manage Teacher Profiles.
    - School Managers: Create/Edit teachers.
    - Teachers: View their own profile.
    """
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [IsSchoolManager | IsWorkStreamManager]

class CourseViewSet(viewsets.ModelViewSet):
    """
    Manage Courses (e.g., 'Math 101').
    - School Managers: Create/Update courses.
    - Teachers/Students: View courses.
    """
    serializer_class = CourseSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Course.objects.all()
        if user.school:
            return Course.objects.filter(school=user.school)
        return Course.objects.none()

    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [IsSchoolManager()]
        return [permissions.IsAuthenticated()]

class ClassRoomViewSet(viewsets.ModelViewSet):
    """
    Manage Classrooms (e.g., 'Grade 5 - Section A').
    """
    serializer_class = ClassRoomSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.school:
            return ClassRoom.objects.filter(school=user.school)
        return ClassRoom.objects.none()

    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [IsSchoolManager()]
        return [permissions.IsAuthenticated()]

class CourseAllocationViewSet(viewsets.ModelViewSet):
    """
    Assign Teachers to Courses in specific Classrooms.
    """
    serializer_class = CourseAllocationSerializer
    permission_classes = [IsSchoolManager]

    def get_queryset(self):
        user = self.request.user
        if user.school:
            return CourseAllocation.objects.filter(class_room__school=user.school)
        return CourseAllocation.objects.none()

class AssignmentViewSet(viewsets.ModelViewSet):
    """
    Teachers create Assignments/Exams.
    """
    serializer_class = AssignmentSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [IsTeacher()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'teacher':
            # Teachers see assignments they created
            return Assignment.objects.filter(created_by__user=user)
        if user.role == 'student':
            # Students see assignments for their classroom (logic simplified)
            # You would typically join via Enrollment -> Classroom -> Course Allocation
            return Assignment.objects.all() 
        return Assignment.objects.all() # Managers see all

class MarkViewSet(viewsets.ModelViewSet):
    """
    Teachers enter marks for students.
    """
    serializer_class = MarkSerializer
    permission_classes = [IsTeacher | IsSchoolManager]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'teacher':
             # Filter marks for assignments created by this teacher
            return Mark.objects.filter(assignment__created_by__user=user)
        return Mark.objects.filter(student__school=user.school)

class AttendanceViewSet(viewsets.ModelViewSet):
    """
    Teachers take attendance.
    """
    serializer_class = AttendanceSerializer
    permission_classes = [IsTeacher | IsSchoolManager]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'teacher':
            return Attendance.objects.filter(course__allocations__teacher__user=user)
        return Attendance.objects.filter(student__school=user.school)