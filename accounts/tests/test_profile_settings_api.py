from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from school.models import School
from workstream.models import WorkStream

User = get_user_model()


class ProfileSettingsApiTests(APITestCase):
    def setUp(self):
        self.workstream = WorkStream.objects.create(
            workstream_name="Settings Workstream",
            capacity=100,
        )
        self.school = School.objects.create(
            school_name="Settings School",
            work_stream=self.workstream,
        )
        self.user = User.objects.create_user(
            email="settings-user@test.com",
            password="pass12345",
            full_name="Settings User",
            role="teacher",
            school=self.school,
        )
        self.url = reverse("profile-update")

    def test_get_requires_authentication(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_returns_profile_settings_fields(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.user.id)
        self.assertEqual(response.data["full_name"], self.user.full_name)
        self.assertEqual(response.data["email"], self.user.email)
        self.assertEqual(response.data["timezone"], "UTC")
        self.assertTrue(response.data["email_notifications"])
        self.assertTrue(response.data["in_app_alerts"])
        self.assertFalse(response.data["sms_notifications"])
        self.assertFalse(response.data["enable_2fa"])
        self.assertNotIn("password", response.data)

    def test_patch_updates_name_and_email(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            "full_name": "Updated Name",
            "email": "updated-name@test.com",
        }

        response = self.client.patch(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.user.refresh_from_db()
        self.assertEqual(self.user.full_name, "Updated Name")
        self.assertEqual(self.user.email, "updated-name@test.com")

    def test_patch_allows_same_email_for_current_user(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            "full_name": "Updated Name",
            "email": self.user.email,
        }

        response = self.client.patch(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.user.refresh_from_db()
        self.assertEqual(self.user.full_name, "Updated Name")
        self.assertEqual(self.user.email, "settings-user@test.com")

    def test_patch_updates_preference_fields(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            "timezone": "Asia/Gaza",
            "email_notifications": False,
            "in_app_alerts": False,
            "sms_notifications": True,
            "enable_2fa": True,
        }

        response = self.client.patch(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.user.refresh_from_db()
        self.assertEqual(self.user.timezone, "Asia/Gaza")
        self.assertFalse(self.user.email_notifications)
        self.assertFalse(self.user.in_app_alerts)
        self.assertTrue(self.user.sms_notifications)
        self.assertTrue(self.user.enable_2fa)

    def test_patch_updates_password_when_valid(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            self.url,
            {"password": "newpass123"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpass123"))

    def test_patch_rejects_short_password(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            self.url,
            {"password": "short"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("pass12345"))

    def test_patch_ignores_sensitive_fields(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            "role": "admin",
            "is_active": False,
            "work_stream": self.workstream.id,
            "school": self.school.id,
        }

        response = self.client.patch(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.user.refresh_from_db()
        self.assertEqual(self.user.role, "teacher")
        self.assertTrue(self.user.is_active)
        self.assertEqual(self.user.school_id, self.school.id)

    def test_defaults_exist_for_authenticated_user(self):
        another_user = User.objects.create_user(
            email="defaults@test.com",
            password="pass12345",
            full_name="Defaults User",
            role="guardian",
        )
        self.client.force_authenticate(user=another_user)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["timezone"], "UTC")
        self.assertTrue(response.data["email_notifications"])
        self.assertTrue(response.data["in_app_alerts"])
        self.assertFalse(response.data["sms_notifications"])
        self.assertFalse(response.data["enable_2fa"])
