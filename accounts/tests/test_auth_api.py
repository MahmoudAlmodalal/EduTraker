"""
Authentication API Tests

Tests for Authentication endpoints:
- Logout (token blacklisting)
- Password reset request
- Password reset confirmation
- Token refresh

SRS Reference: FR-AUTH-001 to FR-AUTH-005
"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class LogoutApiTests(APITestCase):
    """Test logout endpoint with token blacklisting."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.com', password='pass123',
            full_name='Test User', role='admin'
        )
        self.url = reverse('logout')

    def test_logout_with_valid_token(self):
        """Logout should succeed with valid refresh token."""
        self.client.force_authenticate(user=self.user)
        refresh = RefreshToken.for_user(self.user)
        
        response = self.client.post(self.url, {'refresh': str(refresh)})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_with_invalid_token(self):
        """Logout should fail with invalid refresh token."""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post(self.url, {'refresh': 'invalid-token'})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_without_token(self):
        """Logout should fail without providing refresh token."""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post(self.url, {})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_requires_authentication(self):
        """Logout should require authentication."""
        refresh = RefreshToken.for_user(self.user)
        
        response = self.client.post(self.url, {'refresh': str(refresh)})
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_blacklisted_token_cannot_be_used(self):
        """Blacklisted token should not work for authentication."""
        self.client.force_authenticate(user=self.user)
        refresh = RefreshToken.for_user(self.user)
        
        # Logout to blacklist the token
        self.client.post(self.url, {'refresh': str(refresh)})
        
        # Try to use the blacklisted refresh token
        token_refresh_url = reverse('token-refresh')
        self.client.force_authenticate(user=None)  # Clear authentication
        response = self.client.post(token_refresh_url, {'refresh': str(refresh)})
        
        # Token should be blacklisted
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_400_BAD_REQUEST])


class PasswordResetRequestApiTests(APITestCase):
    """Test password reset request endpoint."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.com', password='pass123',
            full_name='Test User', role='admin'
        )
        self.url = reverse('password-reset-request')

    def test_request_reset_for_existing_email(self):
        """Should return success message for existing email."""
        response = self.client.post(self.url, {'email': 'user@test.com'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)

    def test_request_reset_for_nonexistent_email(self):
        """Should return same success message for non-existent email (security)."""
        response = self.client.post(self.url, {'email': 'nonexistent@test.com'})
        
        # Should not reveal whether email exists
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)

    def test_request_reset_returns_token_for_testing(self):
        """Reset request should return uid and token for testing purposes."""
        response = self.client.post(self.url, {'email': 'user@test.com'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # For testing, uid and token are returned
        self.assertIn('uid', response.data)
        self.assertIn('token', response.data)

    def test_request_reset_for_inactive_user(self):
        """Should return success message for inactive user (security)."""
        self.user.is_active = False
        self.user.save()
        
        response = self.client.post(self.url, {'email': 'user@test.com'})
        
        # Should not reveal user is inactive
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PasswordResetConfirmApiTests(APITestCase):
    """Test password reset confirmation endpoint."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.com', password='pass123',
            full_name='Test User', role='admin'
        )
        self.url = reverse('password-reset-confirm')
        
        # Generate valid reset token
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        
        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = default_token_generator.make_token(self.user)

    def test_reset_password_with_valid_token(self):
        """Should successfully reset password with valid token."""
        data = {
            'uid': self.uid,
            'token': self.token,
            'new_password': 'newpass1234',
            'confirm_password': 'newpass1234'
        }
        response = self.client.post(self.url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify the password was changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpass1234'))

    def test_reset_password_with_invalid_token(self):
        """Should fail with invalid token."""
        data = {
            'uid': self.uid,
            'token': 'invalid-token',
            'new_password': 'newpass1234',
            'confirm_password': 'newpass1234'
        }
        response = self.client.post(self.url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_password_with_invalid_uid(self):
        """Should fail with invalid uid."""
        data = {
            'uid': 'invalid-uid',
            'token': self.token,
            'new_password': 'newpass1234',
            'confirm_password': 'newpass1234'
        }
        response = self.client.post(self.url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_password_mismatch(self):
        """Should fail when passwords don't match."""
        data = {
            'uid': self.uid,
            'token': self.token,
            'new_password': 'newpass1234',
            'confirm_password': 'differentpass'
        }
        response = self.client.post(self.url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_password_too_short(self):
        """Should fail with password less than 8 characters."""
        data = {
            'uid': self.uid,
            'token': self.token,
            'new_password': 'short',
            'confirm_password': 'short'
        }
        response = self.client.post(self.url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TokenRefreshApiTests(APITestCase):
    """Test token refresh endpoint."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.com', password='pass123',
            full_name='Test User', role='admin'
        )
        self.url = reverse('token-refresh')

    def test_refresh_with_valid_token(self):
        """Should return new access token with valid refresh token."""
        refresh = RefreshToken.for_user(self.user)
        
        response = self.client.post(self.url, {'refresh': str(refresh)})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_refresh_with_invalid_token(self):
        """Should fail with invalid refresh token."""
        response = self.client.post(self.url, {'refresh': 'invalid-token'})
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_without_token(self):
        """Should fail without providing refresh token."""
        response = self.client.post(self.url, {})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_refresh_with_expired_token(self):
        """Should fail with expired refresh token."""
        # Create a token and blacklist it to simulate expiry behavior
        refresh = RefreshToken.for_user(self.user)
        refresh.blacklist()
        
        response = self.client.post(self.url, {'refresh': str(refresh)})
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class EmailCaseInsensitivityTests(APITestCase):
    """Test that email addresses are case-insensitive."""
    
    def setUp(self):
        """Create a test user with lowercase email."""
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass123',
            full_name='Test User',
            role='admin'
        )
        self.portal_login_url = reverse('portal-login')
    
    def test_login_with_uppercase_email(self):
        """User should be able to login with uppercase email."""
        response = self.client.post(self.portal_login_url, {
            'email': 'TESTUSER@EXAMPLE.COM',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])
    
    def test_login_with_mixed_case_email(self):
        """User should be able to login with mixed case email."""
        response = self.client.post(self.portal_login_url, {
            'email': 'TestUser@Example.Com',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])
    
    def test_login_with_lowercase_email(self):
        """User should be able to login with original lowercase email."""
        response = self.client.post(self.portal_login_url, {
            'email': 'testuser@example.com',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])
    
    def test_password_reset_request_with_uppercase_email(self):
        """Password reset should work with uppercase email."""
        url = reverse('password-reset-request')
        response = self.client.post(url, {
            'email': 'TESTUSER@EXAMPLE.COM'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
    
    def test_password_reset_request_with_mixed_case_email(self):
        """Password reset should work with mixed case email."""
        url = reverse('password-reset-request')
        response = self.client.post(url, {
            'email': 'TestUser@Example.Com'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
