from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from ..models import WorkStream

User = get_user_model()

class WorkstreamApiTests(APITestCase):
    def setUp(self):
        # Create an admin user for workstream management
        self.admin = User.objects.create_superuser(email='admin@example.com', password='password123', full_name='Admin')
        # Create a workstream manager
        self.manager = User.objects.create_user(email='manager@example.com', password='password123', full_name='WS Manager', role='manager_workstream')
        
        self.workstream = WorkStream.objects.create(
            workstream_name="Test Workstream",
            description="A test workstream",
            capacity=100
        )

    def test_list_workstreams_authenticated(self):
        """Test listing workstreams as authenticated admin."""
        self.client.force_authenticate(user=self.admin)
        url = reverse('workstream:workstream-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_create_workstream_as_admin(self):
        """Test creating a workstream as admin."""
        self.client.force_authenticate(user=self.admin)
        url = reverse('workstream:workstream-list-create')
        data = {
            'workstream_name': 'New Workstream',
            'capacity': 50
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(WorkStream.objects.count(), 2)

    def test_update_workstream(self):
        """Test updating a workstream using PUT method."""
        self.client.force_authenticate(user=self.admin)
        url = reverse('workstream:workstream-update', kwargs={'workstream_id': self.workstream.pk})
        data = {
            'workstream_name': 'Updated Name',
            'capacity': self.workstream.capacity,
            'description': self.workstream.description or ''
        }
        response = self.client.put(url, data)  # Use PUT instead of PATCH
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.workstream.refresh_from_db()
        self.assertEqual(self.workstream.workstream_name, 'Updated Name')

    def test_deactivate_workstream(self):
        """Test soft delete/deactivate workstream."""
        self.client.force_authenticate(user=self.admin)
        url = reverse('workstream:workstream-deactivate', kwargs={'workstream_id': self.workstream.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify it's soft deleted
        self.workstream.refresh_from_db()
        self.assertFalse(self.workstream.is_active)
