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
            role='manager_school',
            school=self.school,
            work_stream=self.workstream
        )
        
        self.student_user = User.objects.create_user(
            email='student@example.com',
            password='password123',
            full_name='Student One',
            role='student',
            school=self.school
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
        self.classroom2 = ClassRoom.objects.create(
            classroom_name="10B",
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
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user_id'], self.student.user.id)

    def test_list_students(self):
        """Test listing students."""
        self.client.force_authenticate(user=self.manager_user)
        url = reverse('student:student-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return at least one student (the one created in setUp)
        self.assertGreaterEqual(len(response.data.get('results', response.data)), 1)

    def test_student_enrollment_list(self):
        """Test listing student enrollments."""
        self.client.force_authenticate(user=self.manager_user)
        url = reverse('student:student-enrollment-list', kwargs={'student_id': self.student.user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data.get('results', response.data)), 1)

    def test_student_create_api_success(self):
        """Test successful student creation."""
        self.client.force_authenticate(user=self.manager_user)
        url = reverse('student:student-create')
        data = {
            'email': 'new_student@example.com',
            'full_name': 'New Student',
            'password': 'password123',
            'school_id': self.school.id,
            'grade_id': self.grade_level.id,
            'date_of_birth': '2012-05-20',
            'admission_date': '2026-01-01'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['email'], 'new_student@example.com')
        self.assertTrue(Student.objects.filter(user__email='new_student@example.com').exists())

    def test_student_create_api_missing_fields(self):
        """Test student creation with missing fields."""
        self.client.force_authenticate(user=self.manager_user)
        url = reverse('student:student-create')
        data = {
            'email': 'incomplete@example.com',
            # missing full_name, password, etc.
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_student_update_api(self):
        """Test partial update of a student."""
        self.client.force_authenticate(user=self.manager_user)
        url = reverse('student:student-detail', kwargs={'student_id': self.student.user.id})
        data = {'medical_notes': 'Updated medical notes'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.student.refresh_from_db()
        self.assertEqual(self.student.medical_notes, 'Updated medical notes')

    def test_student_deactivate_activate_api(self):
        """Test deactivating and then activating a student."""
        self.client.force_authenticate(user=self.manager_user)
        
        # Deactivate
        deactivate_url = reverse('student:student-deactivate', kwargs={'student_id': self.student.user.id})
        response = self.client.post(deactivate_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.student.user.refresh_from_db()
        self.assertFalse(self.student.user.is_active)

        # Activate
        activate_url = reverse('student:student-activate', kwargs={'student_id': self.student.user.id})
        response = self.client.post(activate_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.student.user.refresh_from_db()
        self.assertTrue(self.student.user.is_active)

    def test_enrollment_create_api_success(self):
        """Test successful enrollment creation."""
        self.client.force_authenticate(user=self.manager_user)
        url = reverse('student:enrollment-create')
        data = {
            'student_id': self.student.user.id,
            'class_room_id': self.classroom2.id,  # Use classroom2 to avoid unique constraint
            'academic_year_id': self.academic_year.id,
            'status': 'enrolled'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'enrolled')

    def test_enrollment_detail_api(self):
        """Test getting enrollment details."""
        self.client.force_authenticate(user=self.manager_user)
        url = reverse('student:enrollment-detail', kwargs={'enrollment_id': self.enrollment.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.enrollment.id)

    def test_enrollment_update_api(self):
        """Test updating enrollment status."""
        self.client.force_authenticate(user=self.manager_user)
        url = reverse('student:enrollment-detail', kwargs={'enrollment_id': self.enrollment.id})
        data = {'status': 'completed'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.status, 'completed')

    def test_enrollment_deactivate_activate_api(self):
        """Test deactivating and activating an enrollment."""
        self.client.force_authenticate(user=self.manager_user)
        
        # Deactivate
        deactivate_url = reverse('student:enrollment-deactivate', kwargs={'enrollment_id': self.enrollment.id})
        response = self.client.post(deactivate_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.enrollment.refresh_from_db()
        self.assertFalse(self.enrollment.is_active)

        # Activate
        activate_url = reverse('student:enrollment-activate', kwargs={'enrollment_id': self.enrollment.id})
        response = self.client.post(activate_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.enrollment.refresh_from_db()
        self.assertTrue(self.enrollment.is_active)

    def test_permission_checks(self):
        """Test that a student cannot access other students' details or create students."""
        self.client.force_authenticate(user=self.student_user)
        
        # Cannot create student
        create_url = reverse('student:student-create')
        response = self.client.post(create_url, {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Cannot list all students
        list_url = reverse('student:student-list')
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
