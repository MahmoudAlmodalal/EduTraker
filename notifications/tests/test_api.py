from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from ..models import Notification
from django.utils import timezone

User = get_user_model()

class NotificationApiTests(APITestCase):
    """
    Tests for Notification API endpoints.
    """
    def setUp(self):
        # Create users
        self.user = User.objects.create_user(
            email='student@example.com', 
            password='password123', 
            full_name='Student One', 
            role='student'
        )
        self.other_user = User.objects.create_user(
            email='other@example.com', 
            password='password123', 
            full_name='Other User', 
            role='teacher'
        )
        
        # Create some notifications for the user
        self.notification1 = Notification.objects.create(
            recipient=self.user,
            title="Notification 1",
            message="Message 1",
            notification_type="announcement",
            is_read=False
        )
        self.notification2 = Notification.objects.create(
            recipient=self.user,
            title="Notification 2",
            message="Message 2",
            notification_type="system"
        )
        # Mark notification2 as read
        self.notification2.is_read = True
        self.notification2.read_at = timezone.now()
        self.notification2.save()
        
        # Create a notification for another user
        self.other_notification = Notification.objects.create(
            recipient=self.other_user,
            title="Other Notification",
            message="Other Message",
            notification_type="system"
        )
        
        self.list_url = reverse('notifications:notification-list')

    def test_list_notifications_unauthenticated(self):
        """Test unauthenticated user cannot list notifications."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_notifications_authenticated(self):
        """Test authenticated user can list their own notifications."""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Handle both paginated and non-paginated responses
        results = response.data['results'] if isinstance(response.data, dict) and 'results' in response.data else response.data
        self.assertEqual(len(results), 2)

    def test_filter_notifications_is_read(self):
        """Test filtering notifications by is_read status."""
        self.client.force_authenticate(user=self.user)
        
        # Filter read
        response = self.client.get(self.list_url, {'is_read': 'true'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertTrue(response.data['results'][0]['is_read'])
        
        # Filter unread
        response = self.client.get(self.list_url, {'is_read': 'false'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertFalse(response.data['results'][0]['is_read'])

    def test_filter_notifications_type(self):
        """Test filtering notifications by type."""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get(self.list_url, {'notification_type': 'announcement'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['notification_type'], 'announcement')

    def test_get_notification_detail(self):
        """Test retrieving a single notification."""
        self.client.force_authenticate(user=self.user)
        url = reverse('notifications:notification-detail', kwargs={'pk': self.notification1.pk})
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.notification1.title)

    def test_get_other_user_notification_detail(self):
        """Test user cannot retrieve another user's notification."""
        self.client.force_authenticate(user=self.user)
        url = reverse('notifications:notification-detail', kwargs={'pk': self.other_notification.pk})
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_mark_notification_read(self):
        """Test marking a notification as read via API."""
        self.client.force_authenticate(user=self.user)
        url = reverse('notifications:notification-mark-read', kwargs={'pk': self.notification1.pk})
        
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_read'])
        self.assertIsNotNone(response.data['read_at'])
        
        self.notification1.refresh_from_db()
        self.assertTrue(self.notification1.is_read)

    def test_mark_other_user_notification_read(self):
        """Test user cannot mark another user's notification as read."""
        self.client.force_authenticate(user=self.user)
        url = reverse('notifications:notification-mark-read', kwargs={'pk': self.other_notification.pk})
        
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_pagination(self):
        """Test notification list pagination."""
        self.client.force_authenticate(user=self.user)
        
        # Create more notifications to trigger pagination
        # (Assuming page size is around 10 based on earlier history)
        for i in range(12):
            Notification.objects.create(
                recipient=self.user,
                title=f"Extra {i}",
                message="Message",
                notification_type="system"
            )
            
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        
        # Total should be 2 original + 12 extra = 14
        self.assertEqual(response.data['count'], 14)
        # Results should be paginated
        self.assertLess(len(response.data['results']), 14)

    def test_unread_count_api(self):
        """Test the unread count API endpoint."""
        self.client.force_authenticate(user=self.user)
        url = reverse('notifications:notification-unread-count')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # notification1 is unread, notification2 is read. Count should be 1.
        self.assertEqual(response.data['unread_count'], 1)
        
        # Create another unread notification
        Notification.objects.create(
            recipient=self.user,
            title="Extra Unread",
            message="Message",
            notification_type="system",
            is_read=False
        )
        
        response = self.client.get(url)
        self.assertEqual(response.data['unread_count'], 2)

    def test_mark_all_read_api(self):
        """Test marking all notifications as read via API."""
        self.client.force_authenticate(user=self.user)
        url = reverse('notifications:notification-mark-all-read')
        
        # Initially, 1 is unread
        self.assertEqual(Notification.objects.filter(recipient=self.user, is_read=False).count(), 1)
        
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        
        # Now 0 should be unread
        self.assertEqual(Notification.objects.filter(recipient=self.user, is_read=False).count(), 0)
