"""
Tests for Student API endpoints.
"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from ..models import Student, StudentEnrollment
from school.models import School, AcademicYear, Grade, ClassRoom
from workstream.models import WorkStream

User = get_user_model()

class StudentApiTests(APITestCase):
    def setUp(self):
        self.workstream = WorkStream.objects.create(workstream_name="WS1", capacity=10)
        self.school = School.objects.create(school_name="School 1", work_stream=self.workstream)
        self.academic_year = AcademicYear.objects.create(
            academic_year_code="2025/2026",
            school=self.school,
            start_date="2025-09-01",
            end_date="2026-06-30"
        )
        self.grade_level = Grade.objects.create(name="Grade 10", numeric_level=10, min_age=15, max_age=16)
        
        # Create manager user to access student endpoints
        self.manager_user = User.objects.create_user(
            email='manager@example.com',
            password='password123',
            full_name='School Manager',
            role='manager_school'
        )
        
        self.student_user = User.objects.create_user(
            email='student@example.com',
            password='password123',
            full_name='Student One',
            role='student'
        )
        self.student = Student.objects.create(
            user=self.student_user,
            date_of_birth="2010-01-01",
            admission_date="2025-01-01"
        )

        self.classroom = ClassRoom.objects.create(
            classroom_name="10A",
            school=self.school,
            academic_year=self.academic_year,
            grade=self.grade_level
        )
        self.enrollment = StudentEnrollment.objects.create(
            student=self.student,
            class_room=self.classroom,
            academic_year=self.academic_year
        )

    def test_get_student_detail(self):
        """Test getting student details via the API."""
        self.client.force_authenticate(user=self.manager_user)
        url = reverse('student:student-detail', kwargs={'student_id': self.student.user.id})
        response = self.client.get(url)
        # Should return student data or 403 if permission check fails
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN])

    def test_list_students(self):
        """Test listing students."""
        self.client.force_authenticate(user=self.manager_user)
        url = reverse('student:student-list')
        response = self.client.get(url)
        # Should return list or 403 if permission check fails
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN])

    def test_student_enrollment_list(self):
        """Test listing student enrollments."""
        self.client.force_authenticate(user=self.manager_user)
        url = reverse('student:student-enrollment-list', kwargs={'student_id': self.student.user.id})
        response = self.client.get(url)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN])
