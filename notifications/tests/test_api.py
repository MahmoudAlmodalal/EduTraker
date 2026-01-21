from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from ..models import Notification

User = get_user_model()

class NotificationModelTests(APITestCase):
    """
    Tests for Notification model functionality.
    Note: API endpoints for notifications are not yet implemented.
    """
    def setUp(self):
        self.user = User.objects.create_user(email='user@example.com', password='password123', full_name='User One', role='student')
        self.notification = Notification.objects.create(
            recipient=self.user,
            title="Welcome",
            message="Welcome to EduTrack",
            notification_type="system"
        )

    def test_notification_creation(self):
        """Test notification is created correctly."""
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(self.notification.title, "Welcome")
        self.assertFalse(self.notification.is_read)

    def test_mark_read_model(self):
        """Test marking notification as read via model."""
        from django.utils import timezone
        self.notification.is_read = True
        self.notification.read_at = timezone.now()
        self.notification.save()
        
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)
        self.assertIsNotNone(self.notification.read_at)
