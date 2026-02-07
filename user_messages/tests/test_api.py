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
        self.other_user = User.objects.create_user(
            email='other@example.com',
            password='password123',
            full_name='Other User',
            role='teacher'
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

    def test_send_message_empty_body(self):
        """
        Test that sending a message with empty body fails validation.
        """
        self.client.force_authenticate(user=self.sender)
        data = {
            'subject': 'Hello Message',
            'body': '',
            'recipient_ids': [self.recipient1.id]
        }
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_send_message_invalid_recipient(self):
        """
        Test that sending a message to non-existent recipient fails.
        """
        self.client.force_authenticate(user=self.sender)
        data = {
            'subject': 'Hello Message',
            'body': 'Message body',
            'recipient_ids': [99999]  # Non-existent user ID
        }
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

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

    def test_list_messages_filter_inbox(self):
        """
        Test filtering messages by inbox (received messages).
        """
        # Create messages
        msg1 = Message.objects.create(sender=self.sender, subject='Sent by sender', body='Body')
        MessageReceipt.objects.create(message=msg1, recipient=self.recipient1)
        
        msg2 = Message.objects.create(sender=self.recipient1, subject='Sent by recipient1', body='Body')
        MessageReceipt.objects.create(message=msg2, recipient=self.sender)
        
        # Sender filters by inbox (should only see msg2)
        self.client.force_authenticate(user=self.sender)
        response = self.client.get(self.list_create_url, {'box': 'inbox'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get('results', [])), 1)
        self.assertEqual(response.data['results'][0]['subject'], 'Sent by recipient1')

    def test_list_messages_filter_sent(self):
        """
        Test filtering messages by sent (messages user sent).
        """
        # Create messages
        msg1 = Message.objects.create(sender=self.sender, subject='Sent by sender', body='Body')
        MessageReceipt.objects.create(message=msg1, recipient=self.recipient1)
        
        msg2 = Message.objects.create(sender=self.recipient1, subject='Sent by recipient1', body='Body')
        MessageReceipt.objects.create(message=msg2, recipient=self.sender)
        
        # Sender filters by sent (should only see msg1)
        self.client.force_authenticate(user=self.sender)
        response = self.client.get(self.list_create_url, {'box': 'sent'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get('results', [])), 1)
        self.assertEqual(response.data['results'][0]['subject'], 'Sent by sender')

    def test_retrieve_message_detail_as_sender(self):
        """
        Test retrieving message details as the sender.
        """
        msg = Message.objects.create(sender=self.sender, subject='Detail Test', body='Body content')
        MessageReceipt.objects.create(message=msg, recipient=self.recipient1)
        
        url = reverse('user_messages:message-detail', kwargs={'pk': msg.id})
        self.client.force_authenticate(user=self.sender)
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['subject'], 'Detail Test')
        self.assertEqual(response.data['body'], 'Body content')

    def test_retrieve_message_detail_as_recipient(self):
        """
        Test retrieving message details as a recipient.
        """
        msg = Message.objects.create(sender=self.sender, subject='Detail Test', body='Body content')
        MessageReceipt.objects.create(message=msg, recipient=self.recipient1)
        
        url = reverse('user_messages:message-detail', kwargs={'pk': msg.id})
        self.client.force_authenticate(user=self.recipient1)
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['subject'], 'Detail Test')

    def test_retrieve_message_detail_unauthorized(self):
        """
        Test that unauthorized users cannot retrieve message details.
        """
        msg = Message.objects.create(sender=self.sender, subject='Private', body='Private content')
        MessageReceipt.objects.create(message=msg, recipient=self.recipient1)
        
        url = reverse('user_messages:message-detail', kwargs={'pk': msg.id})
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_message_as_sender(self):
        """
        Test sender soft-deleting a message.
        """
        msg = Message.objects.create(sender=self.sender, subject='To Delete', body='Body')
        MessageReceipt.objects.create(message=msg, recipient=self.recipient1)
        
        url = reverse('user_messages:message-detail', kwargs={'pk': msg.id})
        self.client.force_authenticate(user=self.sender)
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        msg.refresh_from_db()
        self.assertTrue(msg.is_active is False)

    def test_delete_message_as_recipient(self):
        """
        Test recipient marking message as deleted (receipt only).
        """
        msg = Message.objects.create(sender=self.sender, subject='To Delete', body='Body')
        receipt = MessageReceipt.objects.create(message=msg, recipient=self.recipient1)
        
        url = reverse('user_messages:message-detail', kwargs={'pk': msg.id})
        self.client.force_authenticate(user=self.recipient1)
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        receipt.refresh_from_db()
        self.assertTrue(receipt.is_deleted)
        # Message itself should still be active
        msg.refresh_from_db()
        self.assertTrue(msg.is_active)

    def test_message_thread_view(self):
        """
        Test retrieving all messages in a thread.
        """
        # Create thread with multiple messages
        msg1 = Message.objects.create(sender=self.sender, subject='Thread Start', body='First message')
        thread_id = msg1.thread_id
        MessageReceipt.objects.create(message=msg1, recipient=self.recipient1)
        
        msg2 = Message.objects.create(
            sender=self.recipient1, 
            subject='Re: Thread Start', 
            body='Reply',
            parent_message=msg1,
            thread_id=thread_id
        )
        MessageReceipt.objects.create(message=msg2, recipient=self.sender)
        
        msg3 = Message.objects.create(
            sender=self.sender,
            subject='Re: Re: Thread Start',
            body='Another reply',
            parent_message=msg2,
            thread_id=thread_id
        )
        MessageReceipt.objects.create(message=msg3, recipient=self.recipient1)
        
        # Sender retrieves thread
        url = reverse('user_messages:message-thread', kwargs={'thread_id': thread_id})
        self.client.force_authenticate(user=self.sender)
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get('results', [])), 3)

    def test_message_thread_view_unauthorized(self):
        """
        Test that unauthorized users cannot access thread.
        """
        msg = Message.objects.create(sender=self.sender, subject='Private Thread', body='Body')
        MessageReceipt.objects.create(message=msg, recipient=self.recipient1)
        
        url = reverse('user_messages:message-thread', kwargs={'thread_id': msg.thread_id})
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get('results', [])), 0)

    def test_mark_as_read_patch(self):
        """
        Ensure recipient can mark message as read using PATCH.
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

    def test_mark_as_read_post(self):
        """
        Ensure recipient can mark message as read using POST.
        """
        msg = Message.objects.create(sender=self.sender, subject='Test Msg', body='Body')
        receipt = MessageReceipt.objects.create(message=msg, recipient=self.recipient1)
        
        url = reverse('user_messages:message-mark-read', kwargs={'pk': msg.id})
        
        self.client.force_authenticate(user=self.recipient1)
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        receipt.refresh_from_db()
        self.assertTrue(receipt.is_read)
        self.assertIsNotNone(receipt.read_at)

    def test_mark_as_read_non_recipient(self):
        """
        Test that non-recipients cannot mark message as read.
        """
        msg = Message.objects.create(sender=self.sender, subject='Test Msg', body='Body')
        MessageReceipt.objects.create(message=msg, recipient=self.recipient1)
        
        url = reverse('user_messages:message-mark-read', kwargs={'pk': msg.id})
        
        self.client.force_authenticate(user=self.other_user)
        response = self.client.patch(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_mark_as_read_idempotent(self):
        """
        Test that marking as read multiple times is idempotent.
        """
        msg = Message.objects.create(sender=self.sender, subject='Test Msg', body='Body')
        receipt = MessageReceipt.objects.create(message=msg, recipient=self.recipient1)
        
        url = reverse('user_messages:message-mark-read', kwargs={'pk': msg.id})
        self.client.force_authenticate(user=self.recipient1)
        
        # Mark as read first time
        response1 = self.client.patch(url)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        receipt.refresh_from_db()
        first_read_at = receipt.read_at
        
        # Mark as read second time
        response2 = self.client.patch(url)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        receipt.refresh_from_db()
        
        # read_at should remain the same
        self.assertEqual(receipt.read_at, first_read_at)


class UserSearchApiTests(APITestCase):
    def setUp(self):
        # Create schools
        from school.models import School
        from workstream.models import WorkStream
        
        self.ws = WorkStream.objects.create(name="Test Workstream", slug="test-ws")
        self.school1 = School.objects.create(school_name="School One", slug="school-1", work_stream=self.ws)
        self.school2 = School.objects.create(school_name="School Two", slug="school-2", work_stream=self.ws)
        
        # School 1 users
        self.s1_manager = User.objects.create_user(
            email='s1_manager@example.com', full_name='S1 Manager', role='manager_school', school=self.school1, work_stream=self.ws
        )
        self.s1_teacher = User.objects.create_user(
            email='s1_teacher@example.com', full_name='S1 Teacher', role='teacher', school=self.school1, work_stream=self.ws
        )
        self.s1_student = User.objects.create_user(
            email='s1_student@example.com', full_name='S1 Student', role='student', school=self.school1, work_stream=self.ws
        )
        
        # School 2 users
        self.s2_manager = User.objects.create_user(
            email='s2_manager@example.com', full_name='S2 Manager', role='manager_school', school=self.school2, work_stream=self.ws
        )
        self.s2_teacher = User.objects.create_user(
            email='s2_teacher@example.com', full_name='S2 Teacher', role='teacher', school=self.school2, work_stream=self.ws
        )

        self.search_url = reverse('user_messages:user-search')

    def test_search_empty_query(self):
        self.client.force_authenticate(user=self.s1_manager)
        response = self.client.get(self.search_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return nothing if no search term
        self.assertEqual(len(response.data.get('results', [])), 0)

    def test_school_manager_visibility(self):
        """School manager should only see users in their school."""
        self.client.force_authenticate(user=self.s1_manager)
        
        # Search for "Teacher"
        response = self.client.get(self.search_url, {'search': 'Teacher'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', [])
        
        # Should only see S1 Teacher, not S2 Teacher
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['email'], self.s1_teacher.email)

    def test_teacher_visibility(self):
        """Teacher should see students and staff in their school."""
        self.client.force_authenticate(user=self.s1_teacher)
        
        # Search for "S1"
        response = self.client.get(self.search_url, {'search': 'S1'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', [])
        
        # Should see S1 Manager and S1 Student (and themselves, but usually user_list returns self)
        # Actually user_list doesn't explicitly exclude self
        emails = [r['email'] for r in results]
        self.assertIn(self.s1_manager.email, emails)
        self.assertIn(self.s1_student.email, emails)
        self.assertNotIn(self.s2_manager.email, emails)

    def test_student_visibility(self):
        """Student should only see staff (Teacher, Secretary, Manager) in their school."""
        self.client.force_authenticate(user=self.s1_student)
        
        # Search for "S1"
        response = self.client.get(self.search_url, {'search': 'S1'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', [])
        
        emails = [r['email'] for r in results]
        self.assertIn(self.s1_manager.email, emails)
        self.assertIn(self.s1_teacher.email, emails)
        # Student should NOT see other students unless logic grows (currently restricted to staff)
        self.assertNotIn(self.s1_student.email, emails)
