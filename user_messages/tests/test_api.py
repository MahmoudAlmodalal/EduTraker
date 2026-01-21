from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from ..models import Message, MessageReceipt

User = get_user_model()

class UserMessageApiTests(APITestCase):
    def setUp(self):
        # Create users
        self.sender = User.objects.create_user(
            email='sender@example.com', 
            password='password123', 
            full_name='Sender User',
            role='teacher'
        )
        self.recipient1 = User.objects.create_user(
            email='recipient1@example.com', 
            password='password123', 
            full_name='Recipient One',
            role='student'
        )
        self.recipient2 = User.objects.create_user(
            email='recipient2@example.com', 
            password='password123', 
            full_name='Recipient Two',
            role='guardian'
        )
        
        # URL endpoints
        self.list_create_url = reverse('user_messages:message-list-create')

    def test_send_message(self):
        """
        Ensure we can send a message to recipients.
        """
        self.client.force_authenticate(user=self.sender)
        data = {
            'subject': 'Hello Message',
            'body': 'Content of the message',
            'recipient_ids': [self.recipient1.id, self.recipient2.id]
        }
        response = self.client.post(self.list_create_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(MessageReceipt.objects.count(), 2)
        
        message = Message.objects.first()
        self.assertEqual(message.sender, self.sender)
        self.assertEqual(message.subject, 'Hello Message')

    def test_list_messages(self):
        """
        Ensure user can list their messages (sent and received).
        """
        # Create a message sent by sender to recipient1
        msg = Message.objects.create(sender=self.sender, subject='Test Msg', body='Body')
        MessageReceipt.objects.create(message=msg, recipient=self.recipient1)
        
        # Sender checks list
        self.client.force_authenticate(user=self.sender)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 1 message found
        self.assertEqual(len(response.data.get('results', [])), 1)
        
        # Recipient checks list
        self.client.force_authenticate(user=self.recipient1)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get('results', [])), 1)
        
        # Non-recipient checks list
        self.client.force_authenticate(user=self.recipient2)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get('results', [])), 0)

    def test_mark_as_read(self):
        """
        Ensure recipient can mark message as read.
        """
        msg = Message.objects.create(sender=self.sender, subject='Test Msg', body='Body')
        receipt = MessageReceipt.objects.create(message=msg, recipient=self.recipient1)
        
        url = reverse('user_messages:message-mark-read', kwargs={'pk': msg.id})
        
        self.client.force_authenticate(user=self.recipient1)
        response = self.client.patch(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        receipt.refresh_from_db()
        self.assertTrue(receipt.is_read)
        self.assertIsNotNone(receipt.read_at)
