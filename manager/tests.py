from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient

from .models import Workstream

User = get_user_model()


class ManagerBasicTests(APITestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            username="manager1",
            email="manager@example.com",
            password="pass1234",
            role="manager",
        )
        self.client = APIClient()
        self.client.force_authenticate(self.manager)

    def test_create_workstream(self):
        url = reverse("workstream-list")
        data = {"name": "WS-1", "capacity": 100, "description": "Test workstream"}
        resp = self.client.post(url, data, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(Workstream.objects.count(), 1)