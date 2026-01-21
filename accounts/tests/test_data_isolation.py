"""
Data Isolation Tests

Tests that verify users cannot access data outside their organizational scope.
SRS Reference: NFR-DATA-002, FR-UM-002
"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from workstream.models import WorkStream
from school.models import School
from student.models import Student

User = get_user_model()


class DataIsolationTests(APITestCase):
    """
    Test data isolation between workstreams and schools.
    Users should only see data within their organizational scope.
    """
    
    def setUp(self):
        # Create two separate workstreams with their own schools
        self.workstream_a = WorkStream.objects.create(workstream_name="Workstream A", capacity=10)
        self.workstream_b = WorkStream.objects.create(workstream_name="Workstream B", capacity=10)
        
        self.school_a = School.objects.create(school_name="School A", work_stream=self.workstream_a)
        self.school_b = School.objects.create(school_name="School B", work_stream=self.workstream_b)
        
        # Create managers for each scope
        self.manager_a = User.objects.create_user(
            email='manager_a@test.com', password='pass123', full_name='Manager A',
            role='manager_school', school=self.school_a
        )
        self.manager_b = User.objects.create_user(
            email='manager_b@test.com', password='pass123', full_name='Manager B',
            role='manager_school', school=self.school_b
        )
        
        # Create students in each school
        self.student_a_user = User.objects.create_user(
            email='student_a@test.com', password='pass123', full_name='Student A',
            role='student', school=self.school_a
        )
        self.student_a = Student.objects.create(
            user=self.student_a_user, date_of_birth="2010-01-01", admission_date="2025-01-01"
        )
        
        self.student_b_user = User.objects.create_user(
            email='student_b@test.com', password='pass123', full_name='Student B',
            role='student', school=self.school_b
        )
        self.student_b = Student.objects.create(
            user=self.student_b_user, date_of_birth="2010-01-01", admission_date="2025-01-01"
        )

    def test_manager_can_access_own_school_students(self):
        """Manager should be able to view students in their own school."""
        self.client.force_authenticate(user=self.manager_a)
        url = reverse('student:student-detail', kwargs={'student_id': self.student_a.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_manager_cannot_access_other_school_students(self):
        """Manager should NOT be able to view students from another school."""
        self.client.force_authenticate(user=self.manager_a)
        url = reverse('student:student-detail', kwargs={'student_id': self.student_b.pk})
        response = self.client.get(url)
        # Should get 403 Forbidden or 404 Not Found (hidden)
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

    def test_student_can_only_see_own_profile(self):
        """Students should only be able to view their own data."""
        self.client.force_authenticate(user=self.student_a_user)
        # Attempt to access another student's profile
        url = reverse('student:student-detail', kwargs={'student_id': self.student_b.pk})
        response = self.client.get(url)
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])


class CrossWorkstreamIsolationTests(APITestCase):
    """Test isolation at the workstream level."""
    
    def setUp(self):
        self.workstream_x = WorkStream.objects.create(workstream_name="WS X", capacity=10)
        self.workstream_y = WorkStream.objects.create(workstream_name="WS Y", capacity=10)
        
        self.ws_manager_x = User.objects.create_user(
            email='ws_x@test.com', password='pass123', full_name='WS Manager X',
            role='manager_workstream', work_stream=self.workstream_x
        )
        self.ws_manager_y = User.objects.create_user(
            email='ws_y@test.com', password='pass123', full_name='WS Manager Y',
            role='manager_workstream', work_stream=self.workstream_y
        )

    def test_ws_manager_cannot_modify_other_workstream(self):
        """Workstream manager should NOT be able to modify another workstream."""
        self.client.force_authenticate(user=self.ws_manager_x)
        url = reverse('workstream:workstream-update', kwargs={'workstream_id': self.workstream_y.pk})
        data = {'workstream_name': 'Hacked Name'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Verify the name was not changed
        self.workstream_y.refresh_from_db()
        self.assertEqual(self.workstream_y.workstream_name, "WS Y")
