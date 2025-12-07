from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

User = get_user_model()


class AccountsAPITests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin1",
            email="admin@example.com",
            password="adminpass123",
            role="admin",
        )
        self.client = APIClient()
    
    def test_admin_can_create_user(self):
        """Test admin can create a new user."""
        self.client.force_authenticate(user=self.admin)
        url = reverse("user-list")
        data = {
            "username": "teacher1",
            "email": "teacher@example.com",
            "password": "teacherpass123",
            "first_name": "John",
            "last_name": "Doe",
            "role": "teacher",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(User.objects.get(email="teacher@example.com").role, "teacher")
    
    def test_admin_can_deactivate_user(self):
        """Test admin can deactivate a user."""
        teacher = User.objects.create_user(
            username="teacher1",
            email="teacher@example.com",
            password="pass123",
            role="teacher",
        )
        self.client.force_authenticate(user=self.admin)
        url = reverse("user-deactivate", kwargs={"pk": teacher.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        teacher.refresh_from_db()
        self.assertFalse(teacher.is_active)
    
    def test_login_endpoint(self):
        """Test JWT login endpoint."""
        url = reverse("token_obtain_pair")
        data = {
            "email": "admin@example.com",
            "password": "adminpass123",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)