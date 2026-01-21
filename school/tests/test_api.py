from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from ..models import School, AcademicYear
from workstream.models import WorkStream

User = get_user_model()

class SchoolApiTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(email='admin@example.com', password='password123', full_name='Admin')
        self.workstream = WorkStream.objects.create(workstream_name="WS1", capacity=10)
        self.school = School.objects.create(
            school_name="Test School",
            work_stream=self.workstream,
            capacity=500,
            location="123 Street"
        )
        self.school_url_list = reverse('school:school-list')
        self.school_url_create = reverse('school:school-create')
        self.school_url_detail = reverse('school:school-update', kwargs={'school_id': self.school.pk})

    def test_list_schools(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.school_url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 1)

    def test_create_school(self):
        self.client.force_authenticate(user=self.admin)
        data = {
            'school_name': 'New School',
            'work_stream_id': self.workstream.id,
            'capacity': 100
        }
        response = self.client.post(self.school_url_create, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(School.objects.count(), 2)

    def test_retrieve_school(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.school_url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['school_name'], 'Test School')

    def test_soft_delete_school(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(self.school_url_detail)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.school.refresh_from_db()
        self.assertFalse(self.school.is_active)
