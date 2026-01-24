from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from accounts.models import Role
from workstream.models import WorkStream
from school.models import School
from student.models import Student
from ..models import Guardian, GuardianStudentLink

User = get_user_model()


class GuardianApiTests(APITestCase):
    def setUp(self):
        # Create Workstreams
        self.ws1 = WorkStream.objects.create(workstream_name="Workstream 1", capacity=10)
        self.ws2 = WorkStream.objects.create(workstream_name="Workstream 2", capacity=10)

        # Create Schools
        self.school1 = School.objects.create(school_name="School 1", work_stream=self.ws1, capacity=100)
        self.school2 = School.objects.create(school_name="School 2", work_stream=self.ws1, capacity=100)
        self.school3 = School.objects.create(school_name="School 3", work_stream=self.ws2, capacity=100)

        # Create Users with different roles
        self.admin = User.objects.create_superuser(
            email='admin@example.com', password='password123', full_name='Admin'
        )
        
        self.ws_manager = User.objects.create_user(
            email='ws_manager@example.com', password='password123', full_name='WS Manager',
            role=Role.MANAGER_WORKSTREAM, work_stream=self.ws1
        )
        
        self.school_manager1 = User.objects.create_user(
            email='sm1@example.com', password='password123', full_name='SM 1',
            role=Role.MANAGER_SCHOOL, school=self.school1
        )
        
        self.school_manager2 = User.objects.create_user(
            email='sm2@example.com', password='password123', full_name='SM 2',
            role=Role.MANAGER_SCHOOL, school=self.school2
        )

        self.teacher1 = User.objects.create_user(
            email='teacher1@example.com', password='password123', full_name='Teacher 1',
            role=Role.TEACHER, school=self.school1
        )

        # Create Guardians
        self.guardian1_user = User.objects.create_user(
            email='guardian1@example.com', password='password123', full_name='Guardian 1',
            role=Role.GUARDIAN, school=self.school1
        )
        self.guardian1 = Guardian.objects.create(user=self.guardian1_user, phone_number="111")

        self.guardian2_user = User.objects.create_user(
            email='guardian2@example.com', password='password123', full_name='Guardian 2',
            role=Role.GUARDIAN, school=self.school2
        )
        self.guardian2 = Guardian.objects.create(user=self.guardian2_user, phone_number="222")

        # Create Students
        self.student1_user = User.objects.create_user(
            email='student1@example.com', password='password123', full_name='Student 1',
            role=Role.STUDENT, school=self.school1
        )
        self.student1 = Student.objects.create(
            user=self.student1_user, date_of_birth="2010-01-01", admission_date="2025-01-01"
        )

        self.student2_user = User.objects.create_user(
            email='student2@example.com', password='password123', full_name='Student 2',
            role=Role.STUDENT, school=self.school2
        )
        self.student2 = Student.objects.create(
            user=self.student2_user, date_of_birth="2010-01-01", admission_date="2025-01-01"
        )

    # --- Guardian CRUD Tests ---

    def test_list_guardians_rbac(self):
        """Test listing guardians based on roles and schools."""
        # Admin sees all
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(reverse('guardian:guardian-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

        # WS Manager sees guardians in their WS (both school 1 and 2)
        self.client.force_authenticate(user=self.ws_manager)
        response = self.client.get(reverse('guardian:guardian-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

        # School Manager 1 sees only guardians in school 1
        self.client.force_authenticate(user=self.school_manager1)
        response = self.client.get(reverse('guardian:guardian-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['email'], self.guardian1_user.email)

    def test_create_guardian_rbac(self):
        """Test creating a guardian."""
        url = reverse('guardian:guardian-create')
        data = {
            "email": "new_guardian@example.com",
            "full_name": "New Guardian",
            "password": "password123",
            "school_id": self.school1.id,
            "phone_number": "555"
        }

        # School Manager 1 can create in school 1
        self.client.force_authenticate(user=self.school_manager1)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Guardian.objects.filter(user__email="new_guardian@example.com").exists())

        # School Manager 2 cannot create in school 1
        self.client.force_authenticate(user=self.school_manager2)
        data["email"] = "other_guardian@example.com"
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_guardian_detail_and_update(self):
        """Test retrieving and updating guardian details."""
        url = reverse('guardian:guardian-detail', kwargs={'guardian_id': self.guardian1_user.id})

        # Teacher in same school can view
        self.client.force_authenticate(user=self.teacher1)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Guardian can view self
        self.client.force_authenticate(user=self.guardian1_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Update phone number
        data = {"phone_number": "999"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.guardian1.refresh_from_db()
        self.assertEqual(self.guardian1.phone_number, "999")

        # Guardian cannot update another guardian
        url2 = reverse('guardian:guardian-detail', kwargs={'guardian_id': self.guardian2_user.id})
        response = self.client.patch(url2, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_guardian_deactivation(self):
        """Test deactivating a guardian."""
        url = reverse('guardian:guardian-deactivate', kwargs={'guardian_id': self.guardian1_user.id})
        
        self.client.force_authenticate(user=self.school_manager1)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        self.guardian1.refresh_from_db()
        self.guardian1_user.refresh_from_db()
        self.assertFalse(self.guardian1.is_active)
        self.assertFalse(self.guardian1_user.is_active)

    # --- Student Link Tests ---

    def test_link_student_constraints(self):
        """Test linking guardian and student."""
        url = reverse('guardian:guardian-student-link', kwargs={'guardian_id': self.guardian1_user.id})
        
        # Link in same school
        data = {
            "student_id": self.student1_user.id,
            "relationship_type": "parent"
        }
        self.client.force_authenticate(user=self.school_manager1)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Link in DIFFERENT school should fail
        # School Manager 1 cannot even see Student 2, so it returns 403
        data = {
            "student_id": self.student2_user.id,
            "relationship_type": "parent"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_linked_students(self):
        """Test listing linked students."""
        GuardianStudentLink.objects.create(
            guardian=self.guardian1, student=self.student1, relationship_type="parent"
        )
        
        url = reverse('guardian:guardian-student-link', kwargs={'guardian_id': self.guardian1_user.id})
        self.client.force_authenticate(user=self.school_manager1)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['student_id'], self.student1_user.id)
