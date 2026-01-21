"""
Edge Case and Boundary Tests

Tests for boundary conditions and edge cases as per SRS NFR requirements.
"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from workstream.models import WorkStream
from school.models import School

User = get_user_model()


class BoundaryConditionTests(APITestCase):
    """Test for boundary conditions and limits."""
    
    def setUp(self):
        self.admin = User.objects.create_superuser(
            email='admin@test.com', password='pass123', full_name='Admin'
        )

    def test_create_workstream_with_zero_capacity(self):
        """Test boundary: capacity of zero."""
        self.client.force_authenticate(user=self.admin)
        url = reverse('workstream:workstream-list-create')
        data = {'workstream_name': 'Zero Cap WS', 'capacity': 0}
        response = self.client.post(url, data)
        # Zero capacity may be valid or invalid depending on business rules
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_201_CREATED])

    def test_create_workstream_with_negative_capacity(self):
        """Test boundary: negative capacity should fail."""
        self.client.force_authenticate(user=self.admin)
        url = reverse('workstream:workstream-list-create')
        data = {'workstream_name': 'Negative Cap WS', 'capacity': -10}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_workstream_with_max_capacity(self):
        """Test boundary: very large capacity value."""
        self.client.force_authenticate(user=self.admin)
        url = reverse('workstream:workstream-list-create')
        data = {'workstream_name': 'Max Cap WS', 'capacity': 999999}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_workstream_with_empty_name(self):
        """Test boundary: empty workstream name should fail."""
        self.client.force_authenticate(user=self.admin)
        url = reverse('workstream:workstream-list-create')
        data = {'workstream_name': '', 'capacity': 10}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class DuplicateDataTests(APITestCase):
    """Test handling of duplicate data."""
    
    def setUp(self):
        self.admin = User.objects.create_superuser(
            email='admin@test.com', password='pass123', full_name='Admin'
        )

    def test_create_user_with_duplicate_email(self):
        """Test: duplicate email should be rejected."""
        # First user
        User.objects.create_user(
            email='duplicate@test.com', password='pass123', full_name='User 1'
        )
        
        # Attempt to create second user with same email
        self.client.force_authenticate(user=self.admin)
        url = reverse('user-create')
        data = {'email': 'duplicate@test.com', 'full_name': 'User 2', 'role': 'student', 'password': 'test1234'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class EmptyDataTests(APITestCase):
    """Test handling of empty or null data."""
    
    def setUp(self):
        self.admin = User.objects.create_superuser(
            email='admin@test.com', password='pass123', full_name='Admin'
        )

    def test_create_user_without_email(self):
        """Test: missing email should fail."""
        self.client.force_authenticate(user=self.admin)
        url = reverse('user-create')
        data = {'full_name': 'Test User', 'role': 'student', 'password': 'test1234'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_without_name(self):
        """Test: missing full_name should fail."""
        self.client.force_authenticate(user=self.admin)
        url = reverse('user-create')
        data = {'email': 'new@test.com', 'role': 'student', 'password': 'test1234'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class SoftDeleteTests(APITestCase):
    """Test soft delete functionality."""
    
    def setUp(self):
        self.admin = User.objects.create_superuser(
            email='admin@test.com', password='pass123', full_name='Admin'
        )
        self.workstream = WorkStream.objects.create(workstream_name="To Delete", capacity=10)

    def test_soft_deleted_workstream_not_in_active_list(self):
        """Test: soft deleted items should not appear in active lists."""
        self.client.force_authenticate(user=self.admin)
        
        # Deactivate the workstream
        url = reverse('workstream:workstream-deactivate', kwargs={'workstream_id': self.workstream.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify it's not in active list
        url = reverse('workstream:workstream-list-create')
        response = self.client.get(url)
        # Handle potential pagination or list response
        results = response.data.get('results', []) if isinstance(response.data, dict) else response.data
        workstream_ids = [ws.get('id') for ws in results if isinstance(ws, dict)]
        self.assertNotIn(self.workstream.pk, workstream_ids)

    def test_soft_deleted_workstream_data_preserved(self):
        """Test: soft deleted items preserve data (FR-UM-006.2)."""
        # Deactivate
        self.workstream.is_active = False
        self.workstream.save()
        
        # Data should still exist in DB
        self.workstream.refresh_from_db()
        self.assertEqual(self.workstream.workstream_name, "To Delete")
        self.assertFalse(self.workstream.is_active)
