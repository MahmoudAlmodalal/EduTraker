from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from ..models import WorkStream

User = get_user_model()


class WorkstreamApiTests(APITestCase):
    """
    Comprehensive test suite for the Workstream application.
    Covers: Public access, Permissions, CRUD operations, Manager assignment, and Filtering.
    """

    def setUp(self):
        # Create an admin user
        self.admin = User.objects.create_superuser(
            email='admin@example.com', 
            password='password123', 
            full_name='Admin User'
        )
        # Create managers
        self.manager1 = User.objects.create_user(
            email='manager1@example.com', 
            password='password123', 
            full_name='Manager One', 
            role='manager_workstream'
        )
        self.manager2 = User.objects.create_user(
            email='manager2@example.com', 
            password='password123', 
            full_name='Manager Two', 
            role='manager_workstream'
        )
        # Create a non-admin user
        self.teacher = User.objects.create_user(
            email='teacher@example.com',
            password='password123',
            full_name='Teacher User',
            role='teacher'
        )
        
        # Create initial workstreams
        self.workstream = WorkStream.objects.create(
            workstream_name="Test Workstream",
            description="A test workstream",
            capacity=100,
            is_active=True
        )
        
        # Workstream with an assigned manager
        self.managed_ws = WorkStream.objects.create(
            workstream_name="Managed WS",
            description="Workstream with manager",
            manager=self.manager2,
            capacity=50,
            is_active=True
        )
        # Synchronize manager's work_stream field
        self.manager2.work_stream = self.managed_ws
        self.manager2.save()

    # ==================== Public Endpoint Tests ====================

    def test_workstream_info_public_access(self):
        url = reverse('workstream:workstream-info', kwargs={'workstream_id': self.workstream.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.workstream.workstream_name)

    def test_workstream_info_not_found(self):
        url = reverse('workstream:workstream-info', kwargs={'workstream_id': 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_workstream_info_inactive_returns_404(self):
        self.workstream.is_active = False
        self.workstream.save()
        url = reverse('workstream:workstream-info', kwargs={'workstream_id': self.workstream.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ==================== Permission Tests ====================

    def test_list_unauthenticated_fails(self):
        url = reverse('workstream:workstream-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_non_admin_fails(self):
        self.client.force_authenticate(user=self.teacher)
        url = reverse('workstream:workstream-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_non_admin_fails(self):
        self.client.force_authenticate(user=self.teacher)
        url = reverse('workstream:workstream-list-create')
        response = self.client.post(url, {'workstream_name': 'New', 'capacity': 10})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ==================== Filter and List Tests ====================

    def test_list_admin_success(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('workstream:workstream-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data.get('results', response.data)
        self.assertGreaterEqual(len(data), 2)

    def test_search_filter(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('workstream:workstream-list-create')
        # Search for part of an existing name - "Managed" is in "Managed WS"
        response = self.client.get(url, {'search': 'Managed'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Handle both paginated and non-paginated responses
        data = response.data['results'] if isinstance(response.data, dict) and 'results' in response.data else response.data
        self.assertGreaterEqual(len(data), 1)
        self.assertTrue(any('Managed' in ws['workstream_name'] for ws in data))

    def test_active_filter(self):
        self.workstream.is_active = False
        self.workstream.save()
        self.client.force_authenticate(user=self.admin)
        url = reverse('workstream:workstream-list-create')
        response = self.client.get(url, {'is_active': 'true'})
        data = response.data.get('results', response.data)
        names = [ws['workstream_name'] for ws in data]
        self.assertNotIn('Test Workstream', names)
        self.assertIn('Managed WS', names)

    # ==================== Create Tests ====================

    def test_create_success(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('workstream:workstream-list-create')
        data = {'workstream_name': 'Brand New', 'capacity': 50}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(WorkStream.objects.filter(workstream_name='Brand New').exists())

    def test_create_with_manager(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('workstream:workstream-list-create')
        data = {'workstream_name': 'New WS 2', 'manager_id': self.manager1.pk, 'capacity': 20}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        ws = WorkStream.objects.get(workstream_name='New WS 2')
        self.assertEqual(ws.manager, self.manager1)
        self.manager1.refresh_from_db()
        self.assertEqual(self.manager1.work_stream, ws)

    def test_create_duplicate_name_fails(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('workstream:workstream-list-create')
        response = self.client.post(url, {'workstream_name': 'Test Workstream', 'capacity': 10})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invalid_manager_role_fails(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('workstream:workstream-list-create')
        response = self.client.post(url, {'workstream_name': 'BadWS', 'manager_id': self.teacher.pk, 'capacity': 10})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_already_assigned_manager_fails(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('workstream:workstream-list-create')
        response = self.client.post(url, {'workstream_name': 'BadWS', 'manager_id': self.manager2.pk, 'capacity': 10})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ==================== Update Tests ====================

    def test_update_put_success(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('workstream:workstream-update', kwargs={'workstream_id': self.workstream.pk})
        data = {'workstream_name': 'Updated Name', 'capacity': 150}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.workstream.refresh_from_db()
        self.assertEqual(self.workstream.workstream_name, 'Updated Name')

    def test_update_patch_success(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('workstream:workstream-update', kwargs={'workstream_id': self.workstream.pk})
        response = self.client.patch(url, {'capacity': 200})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.workstream.refresh_from_db()
        self.assertEqual(self.workstream.capacity, 200)

    def test_update_assign_manager_success(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('workstream:workstream-update', kwargs={'workstream_id': self.workstream.pk})
        response = self.client.put(url, {'workstream_name': 'WS', 'manager_id': self.manager1.pk, 'capacity': 10})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.workstream.refresh_from_db()
        self.assertEqual(self.workstream.manager, self.manager1)
        self.manager1.refresh_from_db()
        self.assertEqual(self.manager1.work_stream, self.workstream)

    def test_update_404(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('workstream:workstream-update', kwargs={'workstream_id': 9999})
        response = self.client.put(url, {'workstream_name': 'X', 'capacity': 1})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ==================== Deactivate Tests ====================

    def test_deactivate_success(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('workstream:workstream-deactivate', kwargs={'workstream_id': self.workstream.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.workstream.refresh_from_db()
        self.assertFalse(self.workstream.is_active)

    def test_deactivate_non_admin_fails(self):
        self.client.force_authenticate(user=self.teacher)
        url = reverse('workstream:workstream-deactivate', kwargs={'workstream_id': self.workstream.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_deactivate_404(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('workstream:workstream-deactivate', kwargs={'workstream_id': 9999})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
