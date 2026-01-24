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
            'work_stream': self.workstream.id,
            'capacity': 100
        }
        response = self.client.post(self.school_url_create, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(School.objects.count(), 2)

    def test_retrieve_school(self):
        self.client.force_authenticate(user=self.admin)
        detail_url = reverse('school:school-list') # School detail is usually part of list or we use update view for GET if enabled, but here school-update is ONLY PUT.
        # However, looking at urls.py there is no school-detail. Let's check SchoolListAPIView or create one if needed?
        # Actually, let's just test that we can get it from list with filter.
        response = self.client.get(self.school_url_list, {'work_stream_id': self.workstream.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Handle both paginated and non-paginated responses
        results = response.data['results'] if isinstance(response.data, dict) and 'results' in response.data else response.data
        self.assertEqual(results[0]['school_name'], 'Test School')

    def test_soft_delete_school(self):
        self.client.force_authenticate(user=self.admin)
        deactivate_url = reverse('school:school-deactivate', kwargs={'school_id': self.school.pk})
        response = self.client.post(deactivate_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.school.refresh_from_db()
        self.assertFalse(self.school.is_active)

    def test_activate_school(self):
        self.school.is_active = False
        self.school.save()
        self.client.force_authenticate(user=self.admin)
        activate_url = reverse('school:school-activate', kwargs={'school_id': self.school.pk})
        response = self.client.post(activate_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.school.refresh_from_db()
        self.assertTrue(self.school.is_active)

    def test_update_school(self):
        self.client.force_authenticate(user=self.admin)
        data = {'school_name': 'Updated School Name'}
        response = self.client.put(self.school_url_detail, data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.school.refresh_from_db()
        self.assertEqual(self.school.school_name, 'Updated School Name')

    def test_list_schools_filter_by_workstream(self):
        self.client.force_authenticate(user=self.admin)
        other_ws = WorkStream.objects.create(workstream_name="OtherWS", capacity=5)
        School.objects.create(school_name="Other School", work_stream=other_ws)
        
        response = self.client.get(self.school_url_list, {'work_stream_id': self.workstream.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Handle both paginated and non-paginated responses
        results = response.data['results'] if isinstance(response.data, dict) and 'results' in response.data else response.data
        count = response.data['count'] if isinstance(response.data, dict) and 'count' in response.data else len(results)
        
        self.assertEqual(count, 1)
        self.assertEqual(results[0]['school_name'], 'Test School')

    def test_permission_denied_unauthenticated(self):
        # No authenticate
        response = self.client.get(self.school_url_list)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
