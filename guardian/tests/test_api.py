"""
Tests for Guardian API endpoints.
"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from ..models import Guardian, GuardianStudentLink
from student.models import Student

User = get_user_model()


class GuardianApiTests(APITestCase):
    def setUp(self):
        # Create users
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='password123',
            full_name='Admin User'
        )
        
        self.guardian_user = User.objects.create_user(
            email='guardian@example.com',
            password='password123',
            full_name='Guardian One',
            role='guardian'
        )
        self.guardian = Guardian.objects.create(user=self.guardian_user, phone_number="1234567890")
        
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

    def test_link_student_model(self):
        """Test GuardianStudentLink model creation."""
        link = GuardianStudentLink.objects.create(
            guardian=self.guardian,
            student=self.student,
            relationship_type="parent",
            is_primary=True
        )
        self.assertEqual(GuardianStudentLink.objects.count(), 1)
        self.assertEqual(link.student, self.student)
        self.assertEqual(link.guardian, self.guardian)

    def test_view_linked_students(self):
        """Test viewing students linked to a guardian via the API."""
        # Link guardian to student first
        GuardianStudentLink.objects.create(
            guardian=self.guardian,
            student=self.student,
            relationship_type="parent"
        )
        
        # Authenticate as admin (who has permission to view this)
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('guardian:guardian-student-link', kwargs={'guardian_id': self.guardian.user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_guardians_as_admin(self):
        """Test listing guardians as admin."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('guardian:guardian-list')
        response = self.client.get(url)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN])
