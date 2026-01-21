"""
Advanced RBAC Permission Tests

Tests for Role-Based Access Control as per SRS FR-UM-002.
Verifies that users can only access resources within their authorization scope.
"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from workstream.models import WorkStream
from school.models import School
from student.models import Student
from teacher.models import Teacher

User = get_user_model()


class RBACPermissionTests(APITestCase):
    """
    Test RBAC enforcement across different roles.
    SRS Reference: FR-UM-002
    """
    
    def setUp(self):
        # Setup organizational hierarchy
        self.workstream1 = WorkStream.objects.create(workstream_name="WS1", capacity=10)
        self.workstream2 = WorkStream.objects.create(workstream_name="WS2", capacity=10)
        
        self.school1 = School.objects.create(school_name="School 1", work_stream=self.workstream1)
        self.school2 = School.objects.create(school_name="School 2", work_stream=self.workstream2)
        
        # Create users with different roles
        self.admin = User.objects.create_superuser(
            email='admin@test.com', password='pass123', full_name='Admin'
        )
        self.ws_manager = User.objects.create_user(
            email='wsmanager@test.com', password='pass123', full_name='WS Manager',
            role='manager_workstream', work_stream=self.workstream1
        )
        self.school_manager = User.objects.create_user(
            email='schoolmanager@test.com', password='pass123', full_name='School Manager',
            role='manager_school', school=self.school1
        )
        self.teacher = User.objects.create_user(
            email='teacher@test.com', password='pass123', full_name='Teacher',
            role='teacher', school=self.school1
        )
        self.student_user = User.objects.create_user(
            email='student@test.com', password='pass123', full_name='Student',
            role='student', school=self.school1
        )
        self.guardian = User.objects.create_user(
            email='guardian@test.com', password='pass123', full_name='Guardian',
            role='guardian'
        )

    # ========================
    # Admin Permission Tests
    # ========================
    
    def test_admin_can_access_workstream_management(self):
        """Admin should have full access to workstream management."""
        self.client.force_authenticate(user=self.admin)
        url = reverse('workstream:workstream-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_create_workstream(self):
        """Admin should be able to create new workstreams."""
        self.client.force_authenticate(user=self.admin)
        url = reverse('workstream:workstream-list-create')
        data = {'workstream_name': 'New WS', 'capacity': 50}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admin_can_access_user_management(self):
        """Admin should have access to user list."""
        self.client.force_authenticate(user=self.admin)
        url = reverse('user-list')  # No namespace for accounts
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ========================
    # Student Role Restrictions
    # ========================
    
    def test_student_cannot_access_workstream_management(self):
        """Students should NOT be able to access workstream management."""
        self.client.force_authenticate(user=self.student_user)
        url = reverse('workstream:workstream-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_cannot_create_users(self):
        """Students should NOT be able to create user accounts."""
        self.client.force_authenticate(user=self.student_user)
        url = reverse('user-create')
        data = {'email': 'new@test.com', 'full_name': 'New User', 'role': 'student'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ========================
    # Guardian Role Restrictions
    # ========================
    
    def test_guardian_cannot_manage_grades(self):
        """Guardians should NOT be able to enter grades."""
        self.client.force_authenticate(user=self.guardian)
        url = reverse('teacher:mark-record')
        data = {'student_id': 1, 'assignment_id': 1, 'score': 85}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ========================
    # Teacher Role Permissions
    # ========================
    
    def test_teacher_can_access_assignment_creation(self):
        """Teachers should be able to create assignments."""
        Teacher.objects.create(user=self.teacher, hire_date="2025-01-01", employment_status="full_time")
        self.client.force_authenticate(user=self.teacher)
        url = reverse('teacher:assignment-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_teacher_cannot_create_users(self):
        """Teachers should NOT be able to create user accounts."""
        self.client.force_authenticate(user=self.teacher)
        url = reverse('user-create')
        data = {'email': 'new@test.com', 'full_name': 'New User', 'role': 'student'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ========================
    # Unauthenticated Access
    # ========================
    
    def test_unauthenticated_cannot_access_protected_endpoints(self):
        """Unauthenticated users should receive 401 on protected endpoints."""
        endpoints = [
            reverse('workstream:workstream-list-create'),
            reverse('student:student-list'),
            reverse('teacher:assignment-list-create'),
        ]
        for url in endpoints:
            response = self.client.get(url)
            self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
