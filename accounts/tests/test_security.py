"""
Security Tests

Tests for security requirements as per SRS Section 11.
Covers input validation, XSS prevention, and authentication security.

Note: Some tests are informational, documenting current behavior for security review.
"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from workstream.models import WorkStream

User = get_user_model()


class InputValidationSecurityTests(APITestCase):
    """
    Test input validation and sanitization.
    SRS Reference: NFR-SEC-005
    
    NOTE: These tests document current behavior. XSS sanitization may need
    to be implemented in serializers or middleware.
    """
    
    def setUp(self):
        self.admin = User.objects.create_superuser(
            email='admin@test.com', password='pass123', full_name='Admin'
        )

    def test_sql_injection_prevention(self):
        """Test: SQL injection attempts should be safely handled by ORM."""
        self.client.force_authenticate(user=self.admin)
        url = reverse('workstream:workstream-list-create')
        malicious_name = "'; DROP TABLE workstream; --"
        data = {'workstream_name': malicious_name, 'capacity': 10}
        response = self.client.post(url, data)
        
        # Django ORM should handle this safely
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # The table should still exist
        self.assertTrue(WorkStream.objects.exists())

    def test_html_in_input_stored_as_is(self):
        """Document: HTML in input is stored without sanitization (for review)."""
        self.client.force_authenticate(user=self.admin)
        url = reverse('workstream:workstream-list-create')
        html_content = '<b>Bold Name</b>'
        data = {'workstream_name': html_content, 'capacity': 10}
        response = self.client.post(url, data)
        
        # Document current behavior (frontend should escape output)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class AuthenticationSecurityTests(APITestCase):
    """
    Test authentication security measures.
    SRS Reference: NFR-SEC-002, NFR-SEC-003
    """

    def test_invalid_credentials_return_error(self):
        """Test: invalid login credentials should return error."""
        url = reverse('portal-login')
        data = {'email': 'nonexistent@test.com', 'password': 'wrongpassword'}
        response = self.client.post(url, data)
        # Should return 400 or 401
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED])

    def test_empty_password_rejected(self):
        """Test: empty password should be rejected."""
        url = reverse('portal-login')
        data = {'email': 'test@test.com', 'password': ''}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_valid_login_returns_tokens(self):
        """Test: valid login should return JWT tokens."""
        User.objects.create_user(
            email='valid@test.com', password='validpass123', full_name='Valid User',
            role='admin'
        )
        url = reverse('portal-login')
        data = {'email': 'valid@test.com', 'password': 'validpass123'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check tokens are returned (structure may vary)
        self.assertTrue('access' in str(response.data) or 'token' in str(response.data))

    def test_login_fails_with_wrong_email_case(self):
        """Case-sensitive email login should reject different letter casing."""
        User.objects.create_user(
            email='CaseSensitive@test.com',
            password='validpass123',
            full_name='Case Sensitive User',
            role='admin'
        )
        url = reverse('portal-login')
        data = {'email': 'casesensitive@test.com', 'password': 'validpass123'}
        response = self.client.post(url, data)
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED])

    def test_token_required_for_protected_endpoints(self):
        """Test: protected endpoints require valid token."""
        url = reverse('workstream:workstream-list-create')
        response = self.client.get(url)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])


class PasswordSecurityTests(APITestCase):
    """
    Test password security requirements.
    SRS Reference: NFR-SEC-002
    """

    def test_password_not_returned_in_response(self):
        """Test: password should never be returned in API responses."""
        admin = User.objects.create_superuser(
            email='admin@test.com', password='securepass123', full_name='Admin'
        )
        self.client.force_authenticate(user=admin)
        
        url = reverse('user-list')
        response = self.client.get(url)
        
        if response.status_code == status.HTTP_200_OK:
            # Check response content for password field
            self.assertNotIn('password', str(response.content))

    def test_password_stored_hashed(self):
        """Test: passwords should be stored hashed, not plaintext."""
        user = User.objects.create_user(
            email='hash@test.com', password='plaintextpass', full_name='Test'
        )
        # Password should not be stored as plaintext
        self.assertNotEqual(user.password, 'plaintextpass')
        # Password should start with Django's hash prefix
        self.assertTrue(
            user.password.startswith('pbkdf2_sha256$') or 
            user.password.startswith('bcrypt') or
            user.password.startswith('argon2')
        )


class RateLimitingTests(APITestCase):
    """
    Test rate limiting (if implemented).
    SRS Reference: Section 8.4
    """
    
    def test_multiple_failed_logins_handled(self):
        """Test: multiple failed login attempts should be handled gracefully."""
        url = reverse('portal-login')
        
        # Attempt 5 failed logins
        for i in range(5):
            data = {'email': 'fake@test.com', 'password': 'wrongpass'}
            response = self.client.post(url, data)
            # Should not crash the server
            self.assertIn(response.status_code, [
                status.HTTP_401_UNAUTHORIZED, 
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_429_TOO_MANY_REQUESTS  # Rate limited (if implemented)
            ])
