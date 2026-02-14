"""
Workstream Authentication Tests

Tests for Workstream-specific authentication:
- Workstream user registration
- Workstream user login
- Workstream capacity validation
- Workstream access control

SRS Reference: FR-WS-001 to FR-WS-003
"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from workstream.models import WorkStream
from school.models import School

User = get_user_model()


class WorkstreamRegistrationTests(APITestCase):
    """Test workstream-specific user registration."""
    
    def setUp(self):
        self.workstream = WorkStream.objects.create(
            workstream_name="Test WS", capacity=5
        )
        self.school = School.objects.create(
            school_name="Test School", work_stream=self.workstream
        )
        self.url = reverse('workstream-register', kwargs={'workstream_id': self.workstream.id})

    def test_register_user_in_workstream(self):
        """Should successfully register a new user in a workstream."""
        data = {
            'email': 'newuser@test.com',
            'full_name': 'New User',
            'password': 'securepass123',
            'password_confirm': 'securepass123'
        }
        response = self.client.post(self.url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify user was created with correct workstream
        user = User.objects.get(email='newuser@test.com')
        self.assertEqual(user.work_stream_id, self.workstream.id)
        self.assertEqual(user.role, 'student')  # Default role for workstream registration

    def test_register_duplicate_email_rejected(self):
        """Should reject registration with existing email."""
        User.objects.create_user(
            email='existing@test.com', password='pass123',
            full_name='Existing User', role='student'
        )
        
        data = {
            'email': 'existing@test.com',
            'full_name': 'New User',
            'password': 'securepass123',
            'password_confirm': 'securepass123'
        }
        response = self.client.post(self.url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_password_mismatch_rejected(self):
        """Should reject registration when passwords don't match."""
        data = {
            'email': 'newuser@test.com',
            'full_name': 'New User',
            'password': 'securepass123',
            'password_confirm': 'differentpass'
        }
        response = self.client.post(self.url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_in_nonexistent_workstream(self):
        """Should fail when registering in non-existent workstream."""
        url = reverse('workstream-register', kwargs={'workstream_id': 99999})
        data = {
            'email': 'newuser@test.com',
            'full_name': 'New User',
            'password': 'securepass123',
            'password_confirm': 'securepass123'
        }
        response = self.client.post(url, data)
        
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND])

    def test_register_exceeds_capacity(self):
        """Should fail when workstream capacity is exceeded."""
        # Fill workstream to capacity
        for i in range(5):
            User.objects.create_user(
                email=f'user{i}@test.com', password='pass123',
                full_name=f'User {i}', role='student',
                work_stream=self.workstream
            )
        
        data = {
            'email': 'newuser@test.com',
            'full_name': 'New User',
            'password': 'securepass123',
            'password_confirm': 'securepass123'
        }
        response = self.client.post(self.url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('maximum', str(response.data).lower())

    def test_register_in_inactive_workstream(self):
        """Should fail when registering in inactive workstream."""
        self.workstream.is_active = False
        self.workstream.save()
        
        data = {
            'email': 'newuser@test.com',
            'full_name': 'New User',
            'password': 'securepass123',
            'password_confirm': 'securepass123'
        }
        response = self.client.post(self.url, data)
        
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND])


class WorkstreamLoginTests(APITestCase):
    """Test workstream-specific user login."""
    
    def setUp(self):
        self.workstream = WorkStream.objects.create(
            workstream_name="Test WS", capacity=10
        )
        self.other_workstream = WorkStream.objects.create(
            workstream_name="Other WS", capacity=10
        )
        
        self.user = User.objects.create_user(
            email='user@test.com', password='pass123',
            full_name='Test User', role='student',
            work_stream=self.workstream
        )
        self.admin = User.objects.create_user(
            email='admin@test.com', password='pass123',
            full_name='Admin User', role='admin'
        )
        
        self.url = reverse('workstream-login', kwargs={'workstream_id': self.workstream.id})

    def test_login_user_in_correct_workstream(self):
        """Should successfully login user in their workstream."""
        data = {
            'email': 'user@test.com',
            'password': 'pass123'
        }
        response = self.client.post(self.url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])

    def test_login_with_invalid_credentials(self):
        """Should fail with invalid credentials."""
        data = {
            'email': 'user@test.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.url, data)
        
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED])

    def test_login_user_in_wrong_workstream(self):
        """Should fail when user tries to login to wrong workstream."""
        url = reverse('workstream-login', kwargs={'workstream_id': self.other_workstream.id})
        data = {
            'email': 'user@test.com',
            'password': 'pass123'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_login_to_any_workstream(self):
        """Admin should be able to login to any workstream."""
        url = reverse('workstream-login', kwargs={'workstream_id': self.other_workstream.id})
        data = {
            'email': 'admin@test.com',
            'password': 'pass123'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_to_nonexistent_workstream(self):
        """Should fail when logging into non-existent workstream."""
        url = reverse('workstream-login', kwargs={'workstream_id': 99999})
        data = {
            'email': 'user@test.com',
            'password': 'pass123'
        }
        response = self.client.post(url, data)
        
        # Could be 404 or 400 depending on implementation
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

    def test_login_inactive_user(self):
        """Should fail when inactive user tries to login."""
        self.user.is_active = False
        self.user.save()
        
        data = {
            'email': 'user@test.com',
            'password': 'pass123'
        }
        response = self.client.post(self.url, data)
        
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED])

    def test_login_returns_user_info(self):
        """Login response should include user information."""
        data = {
            'email': 'user@test.com',
            'password': 'pass123'
        }
        response = self.client.post(self.url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)


class WorkstreamCapacityTests(APITestCase):
    """Test workstream capacity validation."""
    
    def setUp(self):
        self.workstream = WorkStream.objects.create(
            workstream_name="Small WS", capacity=2
        )

    def test_capacity_check_counts_active_users_only(self):
        """Capacity check should only count active users."""
        url = reverse('workstream-register', kwargs={'workstream_id': self.workstream.id})
        
        # Create one active and one inactive user
        User.objects.create_user(
            email='active@test.com', password='pass123',
            full_name='Active User', role='student',
            work_stream=self.workstream, is_active=True
        )
        User.objects.create_user(
            email='inactive@test.com', password='pass123',
            full_name='Inactive User', role='student',
            work_stream=self.workstream, is_active=False
        )
        
        # Should allow registration (only 1 active user out of 2 capacity)
        data = {
            'email': 'newuser@test.com',
            'full_name': 'New User',
            'password': 'securepass123',
            'password_confirm': 'securepass123'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_at_capacity_registration_fails(self):
        """Registration should fail when at exact capacity."""
        url = reverse('workstream-register', kwargs={'workstream_id': self.workstream.id})
        
        # Fill to capacity
        for i in range(2):
            User.objects.create_user(
                email=f'user{i}@test.com', password='pass123',
                full_name=f'User {i}', role='student',
                work_stream=self.workstream
            )
        
        # This should fail
        data = {
            'email': 'newuser@test.com',
            'full_name': 'New User',
            'password': 'securepass123',
            'password_confirm': 'securepass123'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class WorkstreamEmailCaseInsensitivityTests(APITestCase):
    """Test that email addresses are case-insensitive for workstream auth."""
    
    def setUp(self):
        """Create test workstream and user."""
        self.workstream = WorkStream.objects.create(
            workstream_name="Test WS", capacity=10
        )
        self.user = User.objects.create_user(
            email='wsuser@example.com',
            password='testpass123',
            full_name='WS User',
            role='student',
            work_stream=self.workstream
        )
        self.login_url = reverse('workstream-login', kwargs={'workstream_id': self.workstream.id})
    
    def test_workstream_login_with_uppercase_email(self):
        """User should be able to login to workstream with uppercase email."""
        response = self.client.post(self.login_url, {
            'email': 'WSUSER@EXAMPLE.COM',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
    
    def test_workstream_login_with_mixed_case_email(self):
        """User should be able to login to workstream with mixed case email."""
        response = self.client.post(self.login_url, {
            'email': 'WsUser@Example.Com',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
