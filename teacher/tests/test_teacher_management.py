from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from teacher.models import Teacher
from school.models import School
from workstream.models import WorkStream
from accounts.models import Role

User = get_user_model()

class TeacherManagementTests(APITestCase):
    def setUp(self):
        # Setup infrastructure
        self.workstream = WorkStream.objects.create(workstream_name="WS1", capacity=10)
        self.school = School.objects.create(school_name="School 1", work_stream=self.workstream)
        
        # Setup Admin User
        self.admin_user = User.objects.create_superuser(email='admin@example.com', password='password123', full_name='Admin User', role=Role.ADMIN)
        
        # Setup Manager User
        self.manager_user = User.objects.create_user(email='manager@example.com', password='password123', full_name='Manager User', role=Role.MANAGER_SCHOOL, school=self.school)
        
        # Setup Teacher 1
        self.teacher_user1 = User.objects.create_user(email='teacher1@example.com', password='password123', full_name='Teacher One', role=Role.TEACHER, school=self.school)
        self.teacher1 = Teacher.objects.create(user=self.teacher_user1, hire_date="2025-01-01", employment_status="full_time", specialization="Math")
        
        # Setup Teacher 2
        self.teacher_user2 = User.objects.create_user(email='teacher2@example.com', password='password123', full_name='Teacher Two', role=Role.TEACHER, school=self.school)
        self.teacher2 = Teacher.objects.create(user=self.teacher_user2, hire_date="2025-01-01", employment_status="full_time", specialization="Science")

    def test_list_teachers(self):
        """Test listing teachers as an admin."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('teacher:teacher-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if response is paginated
        data = response.data.get('results', response.data) if isinstance(response.data, dict) else response.data
        self.assertEqual(len(data), 2)

    def test_filter_teachers_by_specialization(self):
        """Test filtering teachers by specialization."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('teacher:teacher-list')
        response = self.client.get(url, {'specialization': 'Math'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data.get('results', response.data) if isinstance(response.data, dict) else response.data
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['specialization'], 'Math')

    def test_create_teacher(self):
        """Test creating a teacher as an admin."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('teacher:teacher-create')
        data = {
            'email': 'newteacher@example.com',
            'full_name': 'New Teacher',
            'password': 'password123',
            'school_id': self.school.id,
            'hire_date': '2025-02-01',
            'employment_status': 'full_time',
            'specialization': 'History'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Teacher.objects.filter(user__email='newteacher@example.com').exists())

    def test_create_teacher_missing_fields(self):
        """Test create teacher validation for missing required fields."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('teacher:teacher-create')
        data = {
            'email': 'badteacher@example.com',
            'full_name': 'Bad Teacher',
            # missing password, school_id, hire_date, employment_status
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_teacher(self):
        """Test retrieving teacher details."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('teacher:teacher-detail', args=[self.teacher1.user_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.teacher_user1.email)

    def test_update_teacher(self):
        """Test updating teacher specialization."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('teacher:teacher-detail', args=[self.teacher1.user_id])
        data = {'specialization': 'Advanced Math'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.teacher1.refresh_from_db()
        self.assertEqual(self.teacher1.specialization, 'Advanced Math')

    def test_deactivate_activate_teacher(self):
        """Test deactivating and then activating a teacher."""
        self.client.force_authenticate(user=self.admin_user)
        
        # Deactivate
        deactivate_url = reverse('teacher:teacher-deactivate', args=[self.teacher1.user_id])
        response = self.client.post(deactivate_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.teacher_user1.refresh_from_db()
        self.assertFalse(self.teacher_user1.is_active)
        
        # Activate
        activate_url = reverse('teacher:teacher-activate', args=[self.teacher1.user_id])
        response = self.client.post(activate_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.teacher_user1.refresh_from_db()
        self.assertTrue(self.teacher_user1.is_active)
